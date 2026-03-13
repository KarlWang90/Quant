from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


@dataclass
class Config:
    data: Dict[str, Any]

    @property
    def paths(self) -> Dict[str, str]:
        return self.data.get("paths", {})

    @property
    def project(self) -> Dict[str, Any]:
        return self.data.get("project", {})

    @property
    def universe(self) -> Dict[str, Any]:
        return self.data.get("universe", {})

    @property
    def trading(self) -> Dict[str, Any]:
        return self.data.get("trading", {})

    @property
    def cost_model(self) -> Dict[str, Any]:
        return self.data.get("cost_model", {})

    @property
    def labels(self) -> Dict[str, Any]:
        return self.data.get("labels", {})

    @property
    def model(self) -> Dict[str, Any]:
        return self.data.get("model", {})

    @property
    def validation(self) -> Dict[str, Any]:
        return self.data.get("validation", {})

    @property
    def signal(self) -> Dict[str, Any]:
        return self.data.get("signal", {})

    @property
    def messaging(self) -> Dict[str, Any]:
        return self.data.get("messaging", {})

    @property
    def data_sources(self) -> Dict[str, Any]:
        return self.data.get("data_sources", {})


def load_config(path: str | Path) -> Config:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Config(data=data)
