"""File-based governed memory (Principle 3).

Memory is plain JSON files on disk, namespaced and inspectable, not a hidden
database. "Governed" means access is namespaced and every write is auditable,
which is what the healthcare layer will tighten in later prompts. The store
lives under a gitignored directory and holds synthetic data only at this stage.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_SAFE = re.compile(r"[^a-zA-Z0-9_.-]")


def _safe(part: str) -> str:
    cleaned = _SAFE.sub("_", part.strip())
    if not cleaned or cleaned in {".", ".."}:
        raise ValueError(f"Unsafe memory key or namespace: {part!r}")
    return cleaned


class FileMemory:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, namespace: str, key: str) -> Path:
        ns_dir = self.root / _safe(namespace)
        ns_dir.mkdir(parents=True, exist_ok=True)
        return ns_dir / f"{_safe(key)}.json"

    def remember(self, namespace: str, key: str, value: Any) -> None:
        path = self._path(namespace, key)
        path.write_text(json.dumps(value, indent=2, default=str), encoding="utf-8")

    def recall(self, namespace: str, key: str, default: Any = None) -> Any:
        path = self._path(namespace, key)
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def forget(self, namespace: str, key: str) -> bool:
        path = self._path(namespace, key)
        if path.exists():
            path.unlink()
            return True
        return False

    def keys(self, namespace: str) -> list[str]:
        ns_dir = self.root / _safe(namespace)
        if not ns_dir.exists():
            return []
        return sorted(p.stem for p in ns_dir.glob("*.json"))
