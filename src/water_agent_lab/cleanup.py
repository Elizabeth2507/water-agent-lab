import shutil
from pathlib import Path


def demo_output_exists(output_dir: str | Path) -> bool:
    """
    Return whether a demo output directory exists.
    """
    return Path(output_dir).exists()


def remove_demo_output(output_dir: str | Path) -> None:
    """
    Remove a demo output directory.
    """
    path = Path(output_dir)

    if not path.exists():
        return

    if not path.is_dir():
        raise ValueError(f"Demo output path is not a directory: {path}")

    shutil.rmtree(path)
