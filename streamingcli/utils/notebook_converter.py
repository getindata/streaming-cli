from pydoc import cli
from click import ClickException
import nbformat
from streamingcli.Config import JUPYTER_TAGS
from streamingcli.project.template_loader import TemplateLoader
from jinja2 import Environment
import click 
import sys

class NotebookConverter:

    def convert_notebook(notebook_path: str) -> str:
        try:
            with open(notebook_path, 'r+') as notebook_file:
                notebook = nbformat.reads(notebook_file.read(), as_version=4)
            code_cells = filter(lambda cell: cell.cell_type == 'code'
                            and cell.source.split('\n')[0] in JUPYTER_TAGS, notebook.cells)
            sql_queries = map(lambda cell: '\n'.join(cell.source.split('\n')[1:]) , code_cells)
            flink_app_template = TemplateLoader.load_project_template("flink_app.py.template")
            flink_app_script = Environment().from_string(flink_app_template).render(
                sqls = sql_queries
            )   
            return flink_app_script
        except IOError:
            raise click.ClickException(f"Could not open file: {notebook_path}")
        except:
            raise click.ClickException(f"Unexpected exception: {sys.exc_info()}")
