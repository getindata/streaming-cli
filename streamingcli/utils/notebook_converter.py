import argparse
import shlex
import sys
from dataclasses import dataclass, field

import click
import nbformat
from jinja2 import Environment
from streamingcli.Config import JUPYTER_SQL_MAGICS, JUPYTER_UDF_MAGICS
from streamingcli.project.template_loader import TemplateLoader
import autopep8


@dataclass
class NotebookEntry:
    type: str


@dataclass
class Sql(NotebookEntry):
    value: str = ""
    type: str = "SQL"


@dataclass
class RegisterUdf(NotebookEntry):
    function_name: str = ""
    object_name: str = ""
    type: str = "REGISTER_UDF"


@dataclass
class Code(NotebookEntry):
    value: str = ""
    type: str = "CODE"


class NotebookConverter:
    _register_udf_parser = argparse.ArgumentParser()
    _register_udf_parser.add_argument("--function_name")
    _register_udf_parser.add_argument("--object_name")

    @staticmethod
    def convert_notebook(notebook_path: str) -> str:
        try:
            notebook = NotebookConverter.load_notebook(notebook_path)
            code_cells = filter(lambda _: _.cell_type == 'code', notebook.cells)
            script_entries = []
            for cell in code_cells:
                script_entries.append(NotebookConverter.get_notebook_entry(cell))
            return NotebookConverter.render_flink_app(script_entries)
        except IOError:
            raise click.ClickException(f"Could not open file: {notebook_path}")
        except:
            raise click.ClickException(
                f"Unexpected exception: {sys.exc_info()}")

    @staticmethod
    def load_notebook(notebook_path: str) -> nbformat.NotebookNode:
        with open(notebook_path, 'r+') as notebook_file:
            return nbformat.reads(notebook_file.read(), as_version=4)

    @staticmethod
    def get_notebook_entry(cell: {}) -> NotebookEntry:
        if cell.source.startswith(tuple(JUPYTER_SQL_MAGICS)):
            return Sql(value='\n'.join(cell.source.split('\n')[1:]))
        if cell.source.startswith(tuple(JUPYTER_UDF_MAGICS)):
            args = NotebookConverter._register_udf_parser.parse_args(shlex.split(cell.source)[1:])
            return RegisterUdf(function_name=args.function_name, object_name=args.object_name)
        if cell.source.startswith(('%load_config_file', '##')):
            loaded_variables = {
                "ddd": 1,
                "aaa": "xxx"
            }
            variable_strings = []
            for v in loaded_variables:
                if isinstance(loaded_variables[v], str):
                    variable_strings.append(f"{v}=\"{loaded_variables[v]}\"")
                else:
                    variable_strings.append(f"{v}={loaded_variables[v]}")
            all_variable_strings = "\n".join(variable_strings)
            return Code(value=f"{all_variable_strings}\n{cell.source}")
        elif not cell.source.startswith(('%reload_ext', '##')):
            return Code(value=cell.source)

    @staticmethod
    def render_flink_app(notebook_entries: list) -> str:
        flink_app_template = TemplateLoader.load_project_template("flink_app.py.template")
        flink_app_script = Environment().from_string(flink_app_template).render(
            notebook_entries=notebook_entries
        )
        return autopep8.fix_code(flink_app_script)
