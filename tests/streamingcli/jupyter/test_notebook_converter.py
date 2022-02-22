import unittest

from streamingcli.error import FailedToOpenNotebookFile
from streamingcli.jupyter.notebook_converter import convert_notebook


class TestNotebookConverter(unittest.TestCase):
    """Test converting full Jupyter Notebook with udf to Python class"""

    def test_converter(self):
        # given
        file_path = 'tests/streamingcli/resources/jupyter/notebook1.ipynb'
        # expect
        converted_notebook = convert_notebook(file_path)
        assert converted_notebook.content == '''import sys
from pyflink.table import DataTypes
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, DataTypes
from pyflink.table.udf import udf

env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)
t_env = StreamTableEnvironment.create(env)


maximum_number_of_rows = 10
some_text_variable = "some_text_value"


number_of_rows = 10


t_env.execute_sql(f"""CREATE TABLE datagen (
    id INT
) WITH (
    'connector' = 'datagen',
    'number-of-rows' = '{number_of_rows}'
)""")


@udf(result_type=DataTypes.BOOLEAN())
def filter_print(condition, message):
    with open('filename.txt', 'a+') as f:
        print(f'{message}', file=f)
    return condition


t_env.create_temporary_function("filter_print", filter_print)
'''

    def test_notebook_with_remote_java_udf_conversion(self):
        # given
        file_path = 'tests/streamingcli/resources/jupyter/notebook2.ipynb'
        # expect
        converted_notebook = convert_notebook(file_path)
        assert converted_notebook.content == '''from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, DataTypes
from pyflink.table.udf import udf

env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)
t_env = StreamTableEnvironment.create(env)


maximum_number_of_rows = 10
some_text_variable = "some_text_value"


t_env.create_java_temporary_function("remote_trace", "com.getindata.TraceUDF")


t_env.create_java_temporary_function("other_function", "com.getindata.Other")


t_env.execute_sql(f"""CREATE TABLE datagen (
    id INT
) WITH (
    'connector' = 'datagen',
    'number-of-rows' = '100'
)""")
'''

    def test_notebook_with_local_java_udf_conversion(self):
        # given
        file_path = 'tests/streamingcli/resources/jupyter/notebook3.ipynb'
        # expect
        converted_notebook = convert_notebook(file_path)
        assert converted_notebook.content == '''from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, DataTypes
from pyflink.table.udf import udf

env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)
t_env = StreamTableEnvironment.create(env)


t_env.create_java_temporary_function("local_trace", "com.getindata.TraceUDF")


t_env.execute_sql(f"""CREATE TABLE datagen (
    id INT
) WITH (
    'connector' = 'datagen',
    'number-of-rows' = '100'
)""")
'''

    def test_error_raised(self):
        with self.assertRaises(FailedToOpenNotebookFile):
            convert_notebook("not/existing/path")

    def test_notebook_with_flink_execute_sql_file(self):
        # given
        file_path = 'tests/streamingcli/resources/jupyter/notebook4.ipynb'

        # expect
        converted_notebook = convert_notebook(file_path)
        assert converted_notebook.content == '''from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, DataTypes
from pyflink.table.udf import udf

env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)
t_env = StreamTableEnvironment.create(env)


t_env.execute_sql(f"""CREATE TABLE datagen (
    id INT
) WITH (
      'connector' = 'datagen',
      'number-of-rows' = '{number_of_rows}'
      )""")


t_env.execute_sql(
    f"""select * from datagen WHERE remote_trace(true, 'TRACE_ME', id)""")


t_env.execute_sql(f"""select * from other""")
'''
