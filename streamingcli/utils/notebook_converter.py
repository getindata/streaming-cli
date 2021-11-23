import argparse
import shlex
import sys
from dataclasses import dataclass
from typing import Optional

import click
import nbformat
from jinja2 import Environment
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
class RegisterJavaUdf(RegisterUdf):
    type: str = "REGISTER_JAVA_UDF"


@dataclass
class Code(NotebookEntry):
    value: str = ""
    type: str = "CODE"


class NotebookConverter:
    _register_udf_parser = argparse.ArgumentParser()
    _register_udf_parser.add_argument("--function_name")
    _register_udf_parser.add_argument("--object_name")
    _register_udf_parser.add_argument("--language")

    @staticmethod
    def convert_notebook(notebook_path: str) -> str:
        try:
            notebook = NotebookConverter.load_notebook(notebook_path)
            code_cells = filter(lambda _: _.cell_type == 'code', notebook.cells)
            script_entries = []
            for cell in code_cells:
                entry = NotebookConverter.get_notebook_entry(cell)
                if entry is not None:
                    script_entries.append(entry)
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
    def get_notebook_entry(cell) -> Optional[NotebookEntry]:
        if cell.source.startswith('%'):
            return NotebookConverter.handle_magic_cell(cell)
        elif not cell.source.startswith('##'):
            return Code(value=cell.source)

    @staticmethod
    def handle_magic_cell(cell) -> Optional[NotebookEntry]:
        if cell.source.startswith('%%flink_execute_sql'):
            return Sql(value='\n'.join(cell.source.split('\n')[1:]))
        if cell.source.startswith('%flink_register_function'):
            args = NotebookConverter._register_udf_parser.parse_args(shlex.split(cell.source)[1:])
            return RegisterJavaUdf(function_name=args.function_name,
                                   object_name=args.object_name,
                                   ) if args.language == 'java' else \
                RegisterUdf(function_name=args.function_name,
                            object_name=args.object_name)
        return None

    @staticmethod
    def render_flink_app(notebook_entries: list) -> str:
        flink_app_template = TemplateLoader.load_project_template("flink_app.py.template")
        flink_app_script = Environment().from_string(flink_app_template).render(
            notebook_entries=notebook_entries
        )
        return autopep8.fix_code(flink_app_script)
