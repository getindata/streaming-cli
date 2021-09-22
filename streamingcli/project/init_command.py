from streamingcli.Config import INITIAL_PROJECT_REPO
from streamingcli.project.local_project_config import LocalProjectConfigFactory
import click
import git
import pathlib


class NewProjectInitializer:
    @staticmethod
    def check_if_directory_exists(project_name: str) -> bool:
        return pathlib.Path(f"./{project_name}").exists()

    @staticmethod
    def createProject(project_name: str):
        if NewProjectInitializer.check_if_directory_exists(project_name=project_name):
            raise click.ClickException("Project directory already exists!")

        with click.progressbar(length=100,
                               label='Generating project structure') as bar:
            class CloneProgress(git.RemoteProgress):
                def update(self, op_code, cur_count, max_count=None, message=''):
                    bar.update(current_item=cur_count, n_steps=int(cur_count))

            git.Repo.clone_from(INITIAL_PROJECT_REPO, f"./{project_name}", progress=CloneProgress())

        LocalProjectConfigFactory.generate_initial_project_config(project_name)
