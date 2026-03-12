from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


def generate_signal_report(signals: pd.DataFrame, output_dir: str) -> Path:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(output_dir) / f"signals_{ts}.csv"
    signals.to_csv(path, index=False)
    return path
