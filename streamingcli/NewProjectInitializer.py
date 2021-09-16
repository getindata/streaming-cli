from streamingcli.Config import INITIAL_PROJECT_REPO
import click
import git


class NewProjectInitializer:
    @staticmethod
    def createProject(project_name: str):
        with click.progressbar(length=100,
                               label='Generating project structure') as bar:
            class CloneProgress(git.RemoteProgress):
                def update(self, op_code, cur_count, max_count=None, message=''):
                    bar.update(current_item=cur_count, n_steps=int(cur_count))

            git.Repo.clone_from(INITIAL_PROJECT_REPO, f"./{project_name}", progress=CloneProgress())
