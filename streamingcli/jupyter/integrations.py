from __future__ import print_function

import asyncio
import signal

import nest_asyncio
import pandas as pd
from IPython import display
from IPython.core.display import display as core_display
from IPython.core.magic import (
    Magics, magics_class, line_magic,
    cell_magic
)
from IPython.core.magic_arguments import argument, parse_argstring, magic_arguments
from ipywidgets import FloatProgress, IntText
from jupyter_core.paths import jupyter_config_dir
from py4j.protocol import Py4JJavaError
from pyflink.common import Configuration
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.java_gateway import get_gateway
from pyflink.table import StreamTableEnvironment, EnvironmentSettings, ResultKind

from streamingcli.jupyter.deployment_bar import DeploymentBar
from streamingcli.jupyter.display import pyflink_result_kind_to_string
from streamingcli.jupyter.reflection import get_method_names_for
from streamingcli.jupyter.sql_syntax_highlighting import SQLSyntaxHighlighting
from streamingcli.jupyter.sql_utils import inline_sql_in_cell, is_dml, is_query
from streamingcli.jupyter.variable_substitution import CellContentFormatter


@magics_class
class Integrations(Magics):

    def __init__(self, shell):
        super(Integrations, self).__init__(shell)
        conf = Configuration()
        conf.set_integer("rest.port", 8099)
        conf.set_integer("parallelism.default", 1)
        self.s_env = StreamExecutionEnvironment(
            get_gateway().jvm.org.apache.flink.streaming.api.environment.StreamExecutionEnvironment
            .createLocalEnvironmentWithWebUI(conf._j_configuration))
        self.st_env = StreamTableEnvironment.create(stream_execution_environment=self.s_env,
                                                    environment_settings=EnvironmentSettings
                                                    .new_instance()
                                                    .in_streaming_mode()
                                                    .build())
        self.interrupted = False
        self.polling_ms = 100
        # 20ms
        self.async_wait_s = 2e-2
        Integrations.__enable_sql_syntax_highlighting()
        self.deployment_bar = DeploymentBar(interrupt_callback=self.__interrupt_execute)
        # Indicates whether a job is executing on the Flink cluster in the background
        self.background_execution_in_progress = False
        # Enables nesting blocking async tasks
        nest_asyncio.apply()

    @cell_magic
    def flink_execute_sql(self, line, cell):
        if self.background_execution_in_progress:
            self.__retract_user_as_something_is_executing_in_background()
            return

        # override SIGINT handlers so that they are not propagated
        # to flink java processes. A copy of the original handler is saved
        # so that we can restore it later on.
        # Side note: boolean assignment is atomic in python.
        self.interrupted = False
        original_sigint = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self.__interrupt_execute)
        try:
            cell = self.__enrich_cell(cell)
            task = self.__internal_execute_sql(line, cell)
            if is_dml(cell) or is_query(cell):
                self.deployment_bar.show_deployment_bar()
                asyncio.create_task(task).add_done_callback(self.__handle_done)
            else:
                # if not DML or SELECT then the operation is synchronous
                # synchronous operations are not interactive, one cannot cancel them
                # and hence showing the deployment bar does not make sense
                asyncio.run(task)
        finally:
            signal.signal(signal.SIGINT, original_sigint)

    # a workaround for https://issues.apache.org/jira/browse/FLINK-23020
    async def __internal_execute_sql(self, _line, cell):
        signal.signal(signal.SIGINT, self.__interrupt_execute)
        if is_dml(cell) or is_query(cell):
            print('This job runs in a background, please either wait or interrupt its execution before continuing')
            self.background_execution_in_progress = True
        print('Job starting...')
        execution_result = self.st_env.execute_sql(cell)
        print('Job started')
        successful_execution_msg = 'Execution successful'

        # active polling
        while not self.interrupted:
            try:
                # Explicit await is needed to unblock the main thread to pick up other tasks.
                # In Jupyter's main execution pool there is only one worker thread.
                await asyncio.sleep(self.async_wait_s)
                execution_result.wait(self.polling_ms)
                if is_query(cell):
                    # if a select query has been executing then `wait` returns as soon as the first
                    # row is available. To display the results
                    print('Pulling query results...')
                    await self.display_execution_result(execution_result)
                    return
                else:
                    # if finished then return early even if the user interrupts after this
                    # the actual invocation has already finished
                    print(successful_execution_msg)
                    return
            except Py4JJavaError as err:
                # consume timeout error or rethrow any other
                if 'java.util.concurrent.TimeoutException' not in str(err.java_exception):
                    raise err

        if self.interrupted:
            job_client = execution_result.get_job_client()
            if job_client is not None:
                print(f'Job cancelled {job_client.get_job_id()}')
                job_client.cancel().result()
            else:
                # interrupted and executed a stmt without a proper job (see the underlying execute_sql call)
                print('Job interrupted')
            # in either case return early
            return

        # usual happy path
        print(successful_execution_msg)

    async def display_execution_result(self, execution_result):
        """
         Displays the execution result and returns a dataframe containing all the results.
         Display is done in a stream-like fashion displaying the results as they come.
        """

        columns = execution_result.get_table_schema().get_field_names()
        df = pd.DataFrame(columns=columns)
        result_kind = execution_result.get_result_kind()

        if result_kind == ResultKind.SUCCESS_WITH_CONTENT:
            with execution_result.collect() as results:
                print('Results will be pulled from the job. You can interrupt any time to show partial results.')
                print('Execution result will bind to `execution_result` variable.')
                progress_bar = IntText(value=0, description='Loaded rows: ')
                core_display(progress_bar)
                for result in results:
                    # Explicit await for the same reason as in `__internal_execute_sql`
                    await asyncio.sleep(self.async_wait_s)
                    res = [cell for cell in result]
                    a_series = pd.Series(res, index=df.columns)
                    df = df.append(a_series, ignore_index=True)
                    progress_bar.value += 1

                    if self.interrupted:
                        print('Query interrupted')
                        break
        else:
            series = pd.Series([pyflink_result_kind_to_string(result_kind)], index=df.columns)
            df = df.append(series, ignore_index=True)

        display.display(df)
        self.shell.user_ns['execution_result'] = df

        return df

    @line_magic
    @magic_arguments()
    @argument('-n', '--function_name', type=str,
              help='A function name which will be used in SQL eg. MY_COUNTER',
              required=True)
    @argument('-u', '--object_name', type=str,
              help='A created udf object eg. my_counter',
              required=True)
    def flink_register_function(self, line):
        args = parse_argstring(self.flink_register_function, line)
        shell = self.shell
        function_name = args.function_name
        udf_obj = shell.user_ns[args.object_name]
        self.st_env.create_temporary_function(function_name, udf_obj)
        print(f'Function {function_name} registered')

    @staticmethod
    def __enable_sql_syntax_highlighting():
        methods_decorated_with_cell_magic = get_method_names_for(Integrations, 'cell_magic')
        sql_highlighting = SQLSyntaxHighlighting(methods_decorated_with_cell_magic, jupyter_config_dir())
        sql_highlighting.add_syntax_highlighting_js()

    def __interrupt_execute(self, *args):
        self.interrupted = True

    def __handle_done(self, fut):
        self.background_execution_in_progress = False
        print('Execution done')
        # https://stackoverflow.com/questions/48161387/python-how-to-print-the-stacktrace-of-an-exception-object-without-a-currently
        # will raise an exception to the main thread
        if fut.exception():
            fut.result()

    def __enrich_cell(self, cell):
        enriched_cell = CellContentFormatter(cell, self.shell.user_ns).substitute_user_variables()
        joined_cell = inline_sql_in_cell(enriched_cell)
        return joined_cell

    @staticmethod
    def __retract_user_as_something_is_executing_in_background():
        print('Please wait for the previously submitted task to finish or cancel it.')


def load_ipython_extension(ipython):
    ipython.register_magics(Integrations)
