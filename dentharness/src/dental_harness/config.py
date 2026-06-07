"""Configuration loading.

Config lives in a YAML file so the model and runtime knobs are data, not code
(Principles 3 and 7). Paths in the config are resolved relative to the project
root, which is the directory that contains the config file's parent.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

# project root = dentharness/  (this file is src/dental_harness/config.py)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "config.yaml"


class Settings:
    def __init__(self, data: dict[str, Any], root: Path) -> None:
        self.data = data
        self.root = root

    @property
    def model(self) -> dict[str, Any]:
        return self.data.get("model", {"provider": "mock"})

    @property
    def max_turns(self) -> int:
        return int(self.data.get("loop", {}).get("max_turns", 8))

    def path(self, name: str) -> Path:
        """Resolve a configured path relative to the project root."""
        rel = self.data.get("paths", {}).get(name, name)
        p = Path(rel)
        return p if p.is_absolute() else self.root / p


def load_settings(path: str | os.PathLike[str] | None = None) -> Settings:
    cfg_path = Path(
        path
        or os.environ.get("DENTAL_HARNESS_CONFIG")
        or DEFAULT_CONFIG
    )
    with cfg_path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    # Root is the parent of the config/ directory holding this file.
    root = cfg_path.resolve().parent.parent
    return Settings(data, root)
