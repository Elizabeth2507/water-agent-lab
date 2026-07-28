from pathlib import Path

from water_agent_lab.hashing import compute_config_hashes, compute_file_sha256


def test_compute_file_sha256_is_stable(tmp_path: Path) -> None:
    file_path = tmp_path / "config.yaml"
    file_path.write_text("available_water: 100\n", encoding="utf-8")

    first_hash = compute_file_sha256(file_path)
    second_hash = compute_file_sha256(file_path)

    assert first_hash == second_hash
    assert len(first_hash) == 64


def test_compute_file_sha256_changes_when_file_changes(tmp_path: Path) -> None:
    file_path = tmp_path / "config.yaml"

    file_path.write_text("available_water: 100\n", encoding="utf-8")
    first_hash = compute_file_sha256(file_path)

    file_path.write_text("available_water: 80\n", encoding="utf-8")
    second_hash = compute_file_sha256(file_path)

    assert first_hash != second_hash


def test_compute_config_hashes(tmp_path: Path) -> None:
    first_config = tmp_path / "first.yaml"
    second_config = tmp_path / "second.yaml"

    first_config.write_text("scenario_name: first\n", encoding="utf-8")
    second_config.write_text("scenario_name: second\n", encoding="utf-8")

    hashes = compute_config_hashes([first_config, second_config])

    assert str(first_config) in hashes
    assert str(second_config) in hashes
    assert len(hashes[str(first_config)]) == 64
    assert len(hashes[str(second_config)]) == 64
