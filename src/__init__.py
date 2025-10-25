import tomllib
from pathlib import Path

def _get_version() -> str:
    try:
        pyproject_path = Path(__file__).parent.parent
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        return pyproject_data["tool"]["poetry"]["version"]
    except (FileNotFoundError, KeyError):
        return "0.0.0"

__version__ = _get_version()
__all__ = ["__version__"]