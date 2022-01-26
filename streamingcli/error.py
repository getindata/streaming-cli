class StreamingCliError(Exception):
    """Base class for all exceptions in streamingcli module"""

    message: str
    """explanation of the error"""

    def __init__(self, message: str) -> None:
        self.message = message


class FailedToOpenNotebookFile(StreamingCliError):
    """Exception raised if Jupyter Notebook file cannot be read"""

    def __init__(self, notebook_path: str) -> None:
        self.message = f"Could not open or file does not exist: {notebook_path}"
