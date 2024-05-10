from pathlib import Path


def read_file(file_path: Path | str) -> str:
    path = Path(file_path)
    with path.open("r") as file:
        return file.read()
