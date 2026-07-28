import hashlib
from pathlib import Path


def compute_file_sha256(file_path: str | Path) -> str:
    """
    Compute the SHA256 hash of a file.
    """
    path = Path(file_path)

    sha256_hash = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest()


def compute_config_hashes(config_paths: list[Path]) -> dict[str, str]:
    """
    Compute SHA256 hashes for several config files.
    """
    return {
        str(config_path): compute_file_sha256(config_path)
        for config_path in config_paths
    }
