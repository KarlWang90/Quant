from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


def record_approval(orders: pd.DataFrame, approved: bool, log_dir: str) -> Path:
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = Path(log_dir) / f"approval_{ts}.csv"
    out = orders.copy()
    out["approved"] = approved
    out.to_csv(out_path, index=False)
    return out_path
