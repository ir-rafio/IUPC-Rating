import json
import os
import tempfile
from pathlib import Path


def load_json(path: Path):
    with path.open() as file:
        return json.load(file)


def save_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", text=True)
    try:
        with os.fdopen(descriptor, "w") as file:
            json.dump(value, file, indent=2)
            file.write("\n")
        os.replace(temporary_name, path)
    except Exception:
        Path(temporary_name).unlink(missing_ok=True)
        raise
