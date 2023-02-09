import unittest

from streamingcli.error import FailedToOpenNotebookFile
from streamingcli.jupyter.notebook_converter import convert_notebook


class TestNotebookConverter(unittest.TestCase):
    """Test converting full Jupyter Notebook with udf to Python class"""

    def test_converter(self):
        # given
        file_path = "tests/streamingcli/resources/jupyter/notebook1.ipynb"
        # expect
        converted_notebook = convert_notebook(file_path)
        assert (
            converted_notebook.content
            == '''import sys
from pyflink.table import DataTypes
from pyflink.table.udf import udf
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

stream_env = StreamExecutionEnvironment.get_execution_environment()
stream_env.set_parallelism(1)
table_env = StreamTableEnvironment.create(stream_env)


maximum_number_of_rows = 10
some_text_variable = "some_text_value"


number_of_rows = 10


table_env.execute_sql(f"""CREATE TABLE datagen (
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


table_env.create_temporary_function("filter_print", filter_print)
'''
        )

    def test_notebook_with_remote_java_udf_conversion(self):
        # given
        file_path = "tests/streamingcli/resources/jupyter/notebook2.ipynb"
        # expect
        converted_notebook = convert_notebook(file_path)
        assert (
            converted_notebook.content
            == '''from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

stream_env = StreamExecutionEnvironment.get_execution_environment()
stream_env.set_parallelism(1)
table_env = StreamTableEnvironment.create(stream_env)


maximum_number_of_rows = 10
some_text_variable = "some_text_value"


table_env.create_java_temporary_function(
    "remote_trace", "com.getindata.TraceUDF")


table_env.create_java_temporary_function(
    "other_function", "com.getindata.Other")


table_env.execute_sql(f"""CREATE TABLE datagen (
    id INT
) WITH (
    'connector' = 'datagen',
    'number-of-rows' = '100'
)""")
'''
        )

    def test_notebook_with_local_java_udf_conversion(self):
        # given
        file_path = "tests/streamingcli/resources/jupyter/notebook3.ipynb"
        # expect
        converted_notebook = convert_notebook(file_path)
        assert (
            converted_notebook.content
            == '''from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

stream_env = StreamExecutionEnvironment.get_execution_environment()
stream_env.set_parallelism(1)
table_env = StreamTableEnvironment.create(stream_env)


table_env.create_java_temporary_function(
    "local_trace", "com.getindata.TraceUDF")


table_env.execute_sql(f"""CREATE TABLE datagen (
    id INT
) WITH (
    'connector' = 'datagen',
    'number-of-rows' = '100'
)""")
'''
        )

    def test_error_raised(self):
        with self.assertRaises(FailedToOpenNotebookFile):
            convert_notebook("not/existing/path")

    def test_notebook_with_flink_execute_sql_file(self):
        # given
        file_path = "tests/streamingcli/resources/jupyter/with_init/notebook4.ipynb"

        # expect
        converted_notebook = convert_notebook(file_path)
        assert (
            converted_notebook.content
            == '''from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

stream_env = StreamExecutionEnvironment.get_execution_environment()
stream_env.set_parallelism(1)
table_env = StreamTableEnvironment.create(stream_env)


table_env.execute_sql(f"""CREATE TABLE datagen (
    id INT
) WITH (
      'connector' = 'datagen',
      'number-of-rows' = '{number_of_rows}'
      )""")


table_env.execute_sql(
    f"""select * from datagen WHERE remote_trace(true, 'TRACE_ME', id)""")


table_env.execute_sql(f"""select * from other""")
'''
        )

    def test_notebook_with_show_and_describe(self):
        # given
        file_path = "tests/streamingcli/resources/jupyter/notebook5.ipynb"
        # expect
        converted_notebook = convert_notebook(file_path)
        assert (
            converted_notebook.content
            == '''from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

stream_env = StreamExecutionEnvironment.get_execution_environment()
stream_env.set_parallelism(1)
table_env = StreamTableEnvironment.create(stream_env)


table_env.execute_sql(f"""CREATE TABLE datagen (
    id INT
) WITH (
    'connector' = 'datagen',
    'number-of-rows' = '100'
)""")
'''
        )

    def test_notebook_hidden_to_env_conversion(self):
        # given
        file_path = "tests/streamingcli/resources/jupyter/notebook_env.ipynb"
        # expect
        converted_notebook = convert_notebook(file_path)
        assert (
            converted_notebook.content
            == '''import os
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

stream_env = StreamExecutionEnvironment.get_execution_environment()
stream_env.set_parallelism(1)
table_env = StreamTableEnvironment.create(stream_env)


mysql_table_name = 'datagen'


__env_var_0__MY_ENV_VARIABLE = os.environ["MY_ENV_VARIABLE"]


table_env.execute_sql(f"""CREATE TABLE datagen (
    id INT
) WITH (
    'connector' = 'datagen',
    'number-of-rows' = '{__env_var_0__MY_ENV_VARIABLE}'
)""")


__env_var_1__MYSQL_USER = os.environ["MYSQL_USER"]


__env_var_2__MYSQL_PASSWORD = os.environ["MYSQL_PASSWORD"]


table_env.execute_sql(f"""CREATE TABLE mysql (
    id INT
) WITH (
    'connector' = 'jdbc',
    'url' = 'jdbc:mysql://localhost:3306/mydatabase',
    'table-name' = '{mysql_table_name}',
    'username' = '{__env_var_1__MYSQL_USER}',
    'password' = '{__env_var_2__MYSQL_PASSWORD}'
)""")


table_env.execute_sql(f"""INSERT INTO mysql (SELECT * FROM datagen)""")
'''
        )

    def test_notebook_load_secret(self):
        # given
        file_path = "tests/streamingcli/resources/jupyter/notebook6.ipynb"
        # expect
        converted_notebook = convert_notebook(file_path)
        assert (
            converted_notebook.content
            == '''from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

stream_env = StreamExecutionEnvironment.get_execution_environment()
stream_env.set_parallelism(1)
table_env = StreamTableEnvironment.create(stream_env)


with open("tests/streamingcli/resources/jupyter/secret.txt", "r") as secret_file:
    certificate = secret_file.read().rstrip()


kafka_topic = 'example_topic'


table_env.execute_sql(f"""CREATE TABLE kafka (
    id INT
) WITH (
    'connector' = 'kafka',
    'topic' = '{kafka_topic}',
    'properties.bootstrap.servers' = 'localhost:9092',
    'properties.security.protocol' = 'SSL',
    'properties.group.id' = 'testGroup',
    'scan.startup.mode' = 'earliest-offset',
    'format' = 'json',
    'properties.ssl.truststore.certificates' = '{certificate}',
    'properties.ssl.truststore.type' = 'PEM'
)""")


table_env.execute_sql(f"""CREATE TABLE mysql (
    id INT
) WITH (
    'connector' = 'jdbc',
    'url' = 'jdbc:mysql://localhost:3306/mydatabase',
    'table-name' = 'table_name',
    'username' = 'username',
    'password' = 'password'
)""")


table_env.execute_sql(f"""INSERT INTO mysql (SELECT * FROM kafka)""")
'''
        )

    def test_notebook_load_config_secrets(self):
        # given
        file_path = "tests/streamingcli/resources/jupyter/notebook1.ipynb"
        # expect
        converted_notebook = convert_notebook(
            file_path, {"certificate": "/var/secrets/secret.txt"}
        )
        assert (
            converted_notebook.content
            == '''import sys
from pyflink.table import DataTypes
from pyflink.table.udf import udf
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

stream_env = StreamExecutionEnvironment.get_execution_environment()
stream_env.set_parallelism(1)
table_env = StreamTableEnvironment.create(stream_env)


with open("/var/secrets/secret.txt", "r") as secret_file:
    certificate = secret_file.read().rstrip()


maximum_number_of_rows = 10
some_text_variable = "some_text_value"


number_of_rows = 10


table_env.execute_sql(f"""CREATE TABLE datagen (
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


table_env.create_temporary_function("filter_print", filter_print)
'''
        )

    def test_notebook_with_flink_code(self):
        # given
        file_path = "tests/streamingcli/resources/jupyter/notebook7.ipynb"
        # expect
        converted_notebook = convert_notebook(file_path)
        assert (
            converted_notebook.content
            == """from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

stream_env = StreamExecutionEnvironment.get_execution_environment()
stream_env.set_parallelism(1)
table_env = StreamTableEnvironment.create(stream_env)


execution_output = stream_env.from_collection(
    collection=[(1, 'aaa'), (2, 'bb'), (3, 'cccc')],
    type_info=Types.ROW([Types.INT(), Types.STRING()])
)
"""
        )
