from __future__ import annotations

import importlib
from typing import List

import pandas as pd

from quant.data.symbols import baostock_to_a_share


def fetch_daily(universe: List[str], start: str, end: str) -> pd.DataFrame:
    if importlib.util.find_spec("baostock") is None:
        raise ImportError("baostock not installed. pip install baostock")
    import baostock as bs  # type: ignore

    bs.login()
    frames = []
    for ticker in universe:
        rs = bs.query_history_k_data_plus(
            ticker,
            "date,open,high,low,close,volume,turn,tradestatus",
            start_date=start,
            end_date=end,
            frequency="d",
            adjustflag="2",
        )
        data_list = []
        while (rs.error_code == "0") and rs.next():
            data_list.append(rs.get_row_data())
        if data_list:
            df = pd.DataFrame(data_list, columns=rs.fields)
            df["ticker"] = baostock_to_a_share(ticker)
            df["market"] = "A_SHARE"
            df.rename(columns={"turn": "turnover"}, inplace=True)
            frames.append(df)
    bs.logout()
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    return out
