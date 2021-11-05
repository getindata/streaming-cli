import sys

import click
import nbformat
from jinja2 import Environment
from streamingcli.Config import JUPYTER_SQL_TAGS
from streamingcli.project.template_loader import TemplateLoader


class NotebookConverter:

    @staticmethod
    def convert_notebook(notebook_path: str) -> str:
        try:
            notebook = NotebookConverter.load_notebook(notebook_path=notebook_path)
            sql_queries = NotebookConverter.get_sql_queries(notebook=notebook)
            return NotebookConverter.render_flink_app(sql_queries=sql_queries)
        except IOError:
            raise click.ClickException(f"Could not open file: {notebook_path}")
        except:
            raise click.ClickException(f"Unexpected exception: {sys.exc_info()}")

    @staticmethod
    def load_notebook(notebook_path: str) -> nbformat.NotebookNode:
        with open(notebook_path, 'r+') as notebook_file:
            return nbformat.reads(notebook_file.read(), as_version=4)

    @staticmethod
    def filter_code_cells(notebook: nbformat.NotebookNode):
        return filter(lambda cell: cell.cell_type == 'code' and cell.source.split('\n')[0] in JUPYTER_SQL_TAGS, notebook.cells)

    @staticmethod
    def get_sql_queries(notebook: nbformat.NotebookNode):
        code_cells = NotebookConverter.filter_code_cells(notebook=notebook)
        return map(lambda cell: '\n'.join(cell.source.split('\n')[1:]) , code_cells)

    @staticmethod
    def render_flink_app(sql_queries) -> str:
        flink_app_template = TemplateLoader.load_project_template("flink_app.py.template")
        flink_app_script = Environment().from_string(flink_app_template).render(
            sqls=sql_queries
        )
        return flink_app_script
