from enum import Enum

from streamingcli.Config import PYTHON_TEMPLATE_PROJECT, TEMPLATE_PROJECT_REPOSITORIES, JUPYTER_TEMPLATE_PROJECT


class ProjectType(Enum):
    PYTHON = 'python'
    JUPYTER = 'jupyter'

    @staticmethod
    def to_template_repository(project_type) -> str:
        if project_type == ProjectType.PYTHON:
            return TEMPLATE_PROJECT_REPOSITORIES[PYTHON_TEMPLATE_PROJECT]
        if project_type == ProjectType.JUPYTER:
            return TEMPLATE_PROJECT_REPOSITORIES[JUPYTER_TEMPLATE_PROJECT]
