import sys
from pathlib import Path
from typing import Any

import tomli


def exc_info() -> tuple[type[BaseException] | None, BaseException | None]:
    """Get current exception information
    :return: Return current exception information: (type, value).
    """
    type_, value, _ = sys.exc_info()
    return type_, value


def find_base_path(file_name: Path | str = "pyproject.toml") -> Path:
    """Searches for the base path of the project based on the presence of a unique file.

    Args:
        file_name (Path | str, optional): The name of the file to search for.
        Defaults to "pyproject.toml".

    Returns:
        Path | None: The base path of the project, or None if not found.
    """

    current_path = Path(__file__).resolve().parent
    # Stop when reaching the root directory
    while current_path != current_path.parent:
        if (current_path / file_name).is_file():
            return current_path
        current_path = current_path.parent

    return current_path


def get_project_info(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Get project information from pyproject.toml

    Args:
        path (Path): Path to pyproject.toml

    Returns:
        tuple: (poetry, information)
    """
    with open(f"{path}/pyproject.toml", "rb") as reader:
        pyproject = tomli.load(reader)
        poetry = pyproject["tool"]["poetry"]
        information = pyproject["information"]

    return poetry, information


def is_running_in_docker() -> bool:
    """Check if the current environment is running inside Docker."""
    return Path("/.dockerenv").exists()
