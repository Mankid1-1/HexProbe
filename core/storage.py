from pathlib import Path
import os


DEFAULT_DATA_DIR = Path.home() / ".hexprobe"


def get_data_dir() -> Path:
    """
    Return the HexProbe data directory, creating it if needed.
    """
    data_dir = Path(os.getenv("HEXPROBE_DATA_DIR", DEFAULT_DATA_DIR))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir
