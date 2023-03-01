import argparse
import json
import os
import re
import shlex
import sys
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple, cast

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

    secrets_paths: Dict[str, str]
    """Mapping from secret variable name to path of the file holding the secret."""

    hidden_variable_counter: int
    """Counter of hidden variables that are read from ENVs"""

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

    _load_secret_parser = argparse.ArgumentParser()
    """Argument parser for %load_secret magic"""
    _load_secret_parser.add_argument("--path", "-p")
    _load_secret_parser.add_argument("varname")

    _flink_execute_sql_file_parser = argparse.ArgumentParser()
    """Argument parser for %flink_execute_sql_file magic"""
    _flink_execute_sql_file_parser.add_argument("--path", "-p")

    def __init__(self, notebook_path: str, secrets_paths: Optional[Dict[str, str]]):
        self.notebook_path = notebook_path
        self.secrets_paths = secrets_paths or {}
        self.hidden_variable_counter = 0

    """
    Read and convert Jupyter Notebook

    :return: object representing converted Jupyter Notebook
    :rtype: ConvertedNotebook
    """

    def convert_notebook(self) -> ConvertedNotebook:
        try:
            notebook = self._load_notebook(self.notebook_path)
            code_cells = filter(lambda _: _.cell_type == "code", notebook.cells)
            script_entries: List[NotebookEntry] = []
            script_entries.extend(self._load_secrets_from_scli_config())
            script_entries.extend(
                self._read_init_sql(os.path.dirname(self.notebook_path))
            )
            for cell in code_cells:
                entries = self._get_notebook_entry(
                    cell, os.path.dirname(self.notebook_path)
                )
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
        with open(notebook_path, "r+") as notebook_file:
            return nbformat.reads(notebook_file.read(), as_version=4)

    def _get_notebook_entry(
        self, cell: nbformat.NotebookNode, notebook_dir: str
    ) -> Sequence[NotebookEntry]:
        if cell.source.startswith("%"):
            return self._handle_magic_cell(cell, notebook_dir)
        elif not cell.source.startswith("##") and not cell.source.startswith("!"):
            return [Code(value=cell.source)]
        else:
            return []

    def _handle_magic_cell(
        self, cell: nbformat.NotebookNode, notebook_dir: str
    ) -> Sequence[NotebookEntry]:
        source = cell.source
        if source.startswith("%%flink_execute_sql"):
            sql_statement = "\n".join(source.split("\n")[1:])
            if NotebookConverter._skip_statement(sql_statement):
                return []
            return self._convert_sql_statement_to_python_instructions(sql_statement)
        if source.startswith("%%flink_execute"):
            code = "\n".join(source.split("\n")[1:])
            return [Code(value=code)]
        if source.startswith("%flink_execute_sql_file"):
            return self._get_statements_from_file(source, notebook_dir)
        if source.startswith("%flink_register_function"):
            args = NotebookConverter._udf_parser.parse_args(shlex.split(source)[1:])
            return [
                RegisterJavaUdf(
                    function_name=args.function_name,
                    object_name=args.object_name,
                )
                if args.language == "java"
                else RegisterUdf(
                    function_name=args.function_name, object_name=args.object_name
                )
            ]
        if source.startswith("%load_config_file"):
            return [NotebookConverter._get_variables_from_file(source, notebook_dir)]
        if source.startswith("%flink_register_jar"):
            args = NotebookConverter._udf_parser.parse_args(shlex.split(source)[1:])
            return [
                RegisterJar(url=args.remote_path)
                if args.remote_path is not None
                else RegisterLocalJar(local_path=args.local_path)
            ]
        if source.startswith("%load_secret_file"):
            args = NotebookConverter._load_secret_parser.parse_args(
                shlex.split(source)[1:]
            )
            file_path = (
                args.path if os.path.isabs(args.path) else f"{notebook_dir}/{args.path}"
            )
            return [NotebookConverter._load_secret_from_file(args.varname, file_path)]
        return []

    @staticmethod
    def _get_variables_from_file(source: str, notebook_dir: str) -> Code:
        args = NotebookConverter._load_config_parser.parse_args(shlex.split(source)[1:])
        file_path = (
            args.path if os.path.isabs(args.path) else f"{notebook_dir}/{args.path}"
        )
        loaded_variables = NotebookConverter._load_config_file(path=file_path)
        variable_strings = []
        for v in loaded_variables:
            if isinstance(loaded_variables[v], str):
                variable_strings.append(f'{v}="{loaded_variables[v]}"')
            else:
                variable_strings.append(f"{v}={loaded_variables[v]}")
        all_variable_strings = "\n".join(variable_strings)
        return Code(value=f"{all_variable_strings}")

    def _get_statements_from_file(
        self, source: str, notebook_dir: str
    ) -> Sequence[NotebookEntry]:
        args = NotebookConverter._flink_execute_sql_file_parser.parse_args(
            shlex.split(source)[1:]
        )
        file_path = (
            args.path if os.path.isabs(args.path) else f"{notebook_dir}/{args.path}"
        )
        with open(file_path, "r") as f:
            instructions = [
                instruction
                for statement in sqlparse.split(f.read())
                for instruction in self._convert_sql_statement_to_python_instructions(
                    statement.rstrip(";")
                )
            ]
        return instructions

    def _read_init_sql(self, notebook_dir: str) -> Sequence[NotebookEntry]:
        file_path = f"{notebook_dir}/init.sql"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return [
                    instruction
                    for statement in sqlparse.split(f.read())
                    for instruction in self._convert_sql_statement_to_python_instructions(
                        statement.rstrip(";")
                    )
                ]
        return []

    @staticmethod
    def _load_config_file(path: str) -> Dict[str, Any]:
        with open(path, "r") as json_file:
            return json.load(json_file)

    @staticmethod
    def _render_flink_app(
        notebook_entries: Sequence[NotebookEntry],
    ) -> ConvertedNotebook:
        flink_app_template = TemplateLoader.load_project_template(
            "flink_app.py.template"
        )
        flink_app_script = (
            Environment()
            .from_string(flink_app_template)
            .render(notebook_entries=notebook_entries)
        )
        remote_jars = [
            asdict(entry)["url"]
            for entry in notebook_entries
            if isinstance(entry, RegisterJar)
        ]
        local_jars = [
            asdict(entry)["local_path"]
            for entry in notebook_entries
            if isinstance(entry, RegisterLocalJar)
        ]
        return ConvertedNotebook(
            content=autopep8.fix_code(flink_app_script),
            remote_jars=remote_jars,
            local_jars=local_jars,
        )

    @staticmethod
    def _skip_statement(statement: str) -> bool:
        return (
            statement.strip().lower().startswith(("select", "show", "desc", "explain"))
        )

    def _convert_sql_statement_to_python_instructions(
        self, sql_statement: str
    ) -> List[NotebookEntry]:
        sql_statement, env_var_loads = self._convert_hidden_variables_to_env_vars(
            sql_statement
        )
        return env_var_loads + [Sql(value=sql_statement)]

    def _convert_hidden_variables_to_env_vars(
        self, sql_statement: str
    ) -> Tuple[str, List[NotebookEntry]]:
        hidden_var_pattern = r"(\$\{ *[_a-zA-Z][_a-zA-Z0-9]* *\})"
        hidden_list = cast(List[str], re.findall(hidden_var_pattern, sql_statement))
        hidden_env_load_instructions: List[NotebookEntry] = (
            [Code(value="import os")] if len(hidden_list) > 0 else []
        )
        for hidden in hidden_list:
            var_name = hidden[2:-1].strip()

            hidden_variable_index = self.hidden_variable_counter
            self.hidden_variable_counter = self.hidden_variable_counter + 1

            hidden_env_variable = f"__env_var_{hidden_variable_index}__{var_name}"
            hidden_env_load_instructions.append(
                Code(value=f'{hidden_env_variable} = os.environ["{var_name}"]')
            )

            sql_statement = sql_statement.replace(
                hidden, "{" + hidden_env_variable + "}"
            )
        return sql_statement, hidden_env_load_instructions

    def _load_secrets_from_scli_config(self) -> Sequence[NotebookEntry]:
        return [
            self._load_secret_from_file(var_name, filepath)
            for var_name, filepath in self.secrets_paths.items()
        ]

    @staticmethod
    def _load_secret_from_file(var_name: str, filepath: str) -> NotebookEntry:
        return Code(
            value=f'with open("{filepath}", "r") as secret_file:\n    {var_name} = secret_file.read().rstrip()'
        )


def convert_notebook(
    notebook_path: str, secrets_paths: Optional[Dict[str, str]] = None
) -> ConvertedNotebook:
    return NotebookConverter(notebook_path, secrets_paths).convert_notebook()
