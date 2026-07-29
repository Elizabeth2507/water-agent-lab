from pathlib import Path

import pytest

from water_agent_lab.cleanup import demo_output_exists, remove_demo_output


def test_demo_output_exists(tmp_path: Path) -> None:
    output_dir = tmp_path / "demo"
    output_dir.mkdir()

    assert demo_output_exists(output_dir) is True


def test_demo_output_exists_returns_false_for_missing_dir(tmp_path: Path) -> None:
    output_dir = tmp_path / "missing_demo"

    assert demo_output_exists(output_dir) is False


def test_remove_demo_output_removes_directory(tmp_path: Path) -> None:
    output_dir = tmp_path / "demo"
    output_dir.mkdir()
    (output_dir / "results.csv").write_text("test", encoding="utf-8")

    remove_demo_output(output_dir)

    assert not output_dir.exists()


def test_remove_demo_output_ignores_missing_directory(tmp_path: Path) -> None:
    output_dir = tmp_path / "missing_demo"

    remove_demo_output(output_dir)

    assert not output_dir.exists()


def test_remove_demo_output_rejects_file_path(tmp_path: Path) -> None:
    file_path = tmp_path / "not_a_directory.txt"
    file_path.write_text("test", encoding="utf-8")

    with pytest.raises(ValueError):
        remove_demo_output(file_path)
