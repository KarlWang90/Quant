from __future__ import annotations


def a_share_to_baostock(symbol: str) -> str:
    symbol = symbol.strip()
    if symbol.startswith("sh.") or symbol.startswith("sz."):
        return symbol
    if symbol.endswith(".SH"):
        return f"sh.{symbol.split('.')[0]}"
    if symbol.endswith(".SZ"):
        return f"sz.{symbol.split('.')[0]}"
    return symbol


def baostock_to_a_share(symbol: str) -> str:
    symbol = symbol.strip()
    if symbol.startswith("sh."):
        return f"{symbol.split('.')[1]}.SH"
    if symbol.startswith("sz."):
        return f"{symbol.split('.')[1]}.SZ"
    return symbol


def a_share_to_akshare(symbol: str) -> str:
    symbol = symbol.strip()
    if symbol.endswith(".SH") or symbol.endswith(".SZ"):
        return symbol.split(".")[0]
    return symbol
