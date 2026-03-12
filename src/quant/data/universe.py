from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import yaml


def load_universe(path: str | Path) -> Dict[str, List[str]]:
    path = Path(path)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    # Ensure all values are lists
    out: Dict[str, List[str]] = {}
    for k, v in data.items():
        if v is None:
            out[k] = []
        elif isinstance(v, list):
            out[k] = [str(x) for x in v]
        else:
            out[k] = [str(v)]
    return out
