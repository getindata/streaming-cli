import pytest
from streamingcli.utils.notebook_converter import NotebookConverter


class TestNotebookConverter:
    """Test converting full Jupyter Notebook with udf to Python class"""

    def test_converter(self):
        # given
        file_path = 'tests/streamingcli/utils/jupyter/notebook1.ipynb'
        # expect
        x = NotebookConverter.convert_notebook(file_path)
        print(x)
        assert x == '''import sys
from pyflink.table import DataTypes
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, DataTypes
from pyflink.table.udf import udf

env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)
t_env = StreamTableEnvironment.create(env)


t_env.execute_sql(f"""CREATE TABLE datagen (
    id INT
) WITH (
    'connector' = 'datagen',
    'number-of-rows' = '10'
)""")


@udf(result_type=DataTypes.BOOLEAN())
def filter_print(condition, message):
    with open('filename.txt', 'a+') as f:
        print(f'{message}', file=f)
    return condition


t_env.create_temporary_function("filter_print", filter_print)


t_env.execute_sql(f"""select * from datagen WHERE filter_print(true, id)""")
'''
