import argparse
import json
import os
import shlex
import sys
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Sequence

import autopep8
import nbformat
import sqlparse
from jinja2 import Environment

from ..error import FailedToOpenNotebookFile, StreamingCliError
from ..project.template_loader import TemplateLoader


@dataclass
class ConvertedNotebook:
    content: str
    remote_jars: List[str] = field(default_factory=lambda: [])
    local_jars: List[str] = field(default_factory=lambda: [])


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


@dataclass
class RegisterJar(NotebookEntry):
    url: str = ""
    type: str = "REGISTER_JAR"


@dataclass
class RegisterLocalJar(NotebookEntry):
    local_path: str = ""
    type: str = "REGISTER_LOCAL_JAR"


class NotebookConverter:
    """
    Read Jupyter Notebook .ipynb file and convert it to Python script.
    """

    notebook_path: str
    """String representing path to .ipynb file"""
    _udf_parser = argparse.ArgumentParser()
    """Argument parser for %register_udf magic"""
    _udf_parser.add_argument("--function_name", "-n")
    _udf_parser.add_argument("--object_name", "-u")
    _udf_parser.add_argument("--language", "-l")
    _udf_parser.add_argument("--remote_path", "-r")
    _udf_parser.add_argument("--local_path", "-p")
    _load_config_parser = argparse.ArgumentParser()
    """Argument parser for %load_config magic"""
    _load_config_parser.add_argument("--path", "-p")
    _flink_execute_sql_file_parser = argparse.ArgumentParser()
    """Argument parser for %flink_execute_sql_file magic"""
    _flink_execute_sql_file_parser.add_argument("--path", "-p")

    def __init__(self, notebook_path: str):
        self.notebook_path = notebook_path

    """
    Read and convert Jupyter Notebook

    :return: object representing converted Jupyter Notebook
    :rtype: ConvertedNotebook
    """

    def convert_notebook(self) -> ConvertedNotebook:
        try:
            notebook = self._load_notebook(self.notebook_path)
            code_cells = filter(lambda _: _.cell_type == 'code', notebook.cells)
            script_entries: List[NotebookEntry] = []
            for cell in code_cells:
                entries = self._get_notebook_entry(cell, os.path.dirname(self.notebook_path))
                if entries:
                    for e in entries:
                        script_entries.append(e)
            return self._render_flink_app(script_entries)
        except IOError:
            raise FailedToOpenNotebookFile(self.notebook_path)
        except Exception:  # noqa
            raise StreamingCliError(
                f"Unexpected exception while converting notebook file: {sys.exc_info()}"
            )

    @staticmethod
    def _load_notebook(notebook_path: str) -> nbformat.NotebookNode:
        with open(notebook_path, 'r+') as notebook_file:
            return nbformat.reads(notebook_file.read(), as_version=4)

    @staticmethod
    def _get_notebook_entry(cell: nbformat.NotebookNode, notebook_dir: str) -> Sequence[NotebookEntry]:
        if cell.source.startswith('%'):
            return NotebookConverter._handle_magic_cell(cell, notebook_dir)
        elif not cell.source.startswith('##'):
            return [Code(value=cell.source)]
        else:
            return []

    @staticmethod
    def _handle_magic_cell(cell: nbformat.NotebookNode, notebook_dir: str) -> Sequence[NotebookEntry]:
        source = cell.source
        if source.startswith('%%flink_execute_sql'):
            sql_statement = '\n'.join(source.split('\n')[1:])
            if sql_statement.lower().startswith('select'):
                return []
            return [Sql(value=sql_statement)]
        if source.startswith('%flink_execute_sql_file'):
            return NotebookConverter._get_statements_from_file(source, notebook_dir)
        if source.startswith('%flink_register_function'):
            args = NotebookConverter._udf_parser.parse_args(shlex.split(source)[1:])
            return [RegisterJavaUdf(function_name=args.function_name,
                                    object_name=args.object_name,
                                    ) if args.language == 'java' else
                    RegisterUdf(function_name=args.function_name,
                                object_name=args.object_name)]
        if source.startswith('%load_config_file'):
            return [NotebookConverter._get_variables_from_file(source, notebook_dir)]
        if source.startswith('%flink_register_jar'):
            args = NotebookConverter._udf_parser.parse_args(shlex.split(source)[1:])
            return [RegisterJar(url=args.remote_path) if args.remote_path is not None else
                    RegisterLocalJar(local_path=args.local_path)]
        return []

    @staticmethod
    def _get_variables_from_file(source: str, notebook_dir: str) -> Code:
        args = NotebookConverter._load_config_parser.parse_args(shlex.split(source)[1:])
        file_path = args.path if os.path.isabs(args.path) else f"{notebook_dir}/{args.path}"
        loaded_variables = NotebookConverter._load_config_file(path=file_path)
        variable_strings = []
        for v in loaded_variables:
            if isinstance(loaded_variables[v], str):
                variable_strings.append(f"{v}=\"{loaded_variables[v]}\"")
            else:
                variable_strings.append(f"{v}={loaded_variables[v]}")
        all_variable_strings = "\n".join(variable_strings)
        return Code(value=f"{all_variable_strings}")

    @staticmethod
    def _get_statements_from_file(source: str, notebook_dir: str) -> Sequence[NotebookEntry]:
        args = NotebookConverter._flink_execute_sql_file_parser.parse_args(shlex.split(source)[1:])
        file_path = args.path if os.path.isabs(args.path) else f"{notebook_dir}/{args.path}"
        with open(file_path, "r") as f:
            statements = list(map(lambda s: Sql(value=s.rstrip(';')), sqlparse.split(f.read())))
        return statements

    @staticmethod
    def _load_config_file(path: str) -> Dict[str, Any]:
        with open(path, "r") as json_file:
            return json.load(json_file)

    @staticmethod
    def _render_flink_app(notebook_entries: Sequence[NotebookEntry]) -> ConvertedNotebook:
        flink_app_template = TemplateLoader.load_project_template("flink_app.py.template")
        flink_app_script = Environment().from_string(flink_app_template).render(
            notebook_entries=notebook_entries
        )
        remote_jars = map(lambda entry: asdict(entry)["url"],
                          filter(lambda entry: isinstance(entry, RegisterJar), notebook_entries))
        local_jars = map(lambda entry: asdict(entry)["local_path"],
                         filter(lambda entry: isinstance(entry, RegisterLocalJar), notebook_entries))
        return ConvertedNotebook(content=autopep8.fix_code(flink_app_script), remote_jars=list(remote_jars),
                                 local_jars=list(local_jars))


def convert_notebook(notebook_path: str) -> ConvertedNotebook:
    return NotebookConverter(notebook_path).convert_notebook()
