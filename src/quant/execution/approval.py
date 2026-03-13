from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


def write_approval_request(orders: pd.DataFrame, log_dir: str) -> Path:
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = Path(log_dir) / f"approval_request_{ts}.csv"
    out = orders.copy()
    if "approval_status" not in out.columns:
        out["approval_status"] = "PENDING"
    out.to_csv(out_path, index=False)
    return out_path


def record_approval(orders: pd.DataFrame, decision: str, log_dir: str) -> Path:
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = Path(log_dir) / f"approval_{decision.lower()}_{ts}.csv"
    out = orders.copy()
    out["approval_status"] = decision.upper()
    out.to_csv(out_path, index=False)
    return out_path
