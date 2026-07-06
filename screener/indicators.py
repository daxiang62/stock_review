"""技术指标计算模块
基于 MyTT 计算常用技术指标，并把结果作为新列追加到 K 线 DataFrame 上。
输入 DataFrame 需包含列: open, high, low, close, volume
"""
import pandas as pd
from MyTT import MA, MACD, KDJ, RSI, BOLL


def add_ma(df: pd.DataFrame, periods=(5, 10, 20, 60)) -> pd.DataFrame:
    """追加多条均线，列名如 ma5/ma10/ma20/ma60"""
    close = df["close"].values
    for n in periods:
        df[f"ma{n}"] = MA(close, n)
    return df


def add_macd(df: pd.DataFrame, short: int = 12, long: int = 26, m: int = 9) -> pd.DataFrame:
    """追加 MACD 指标: dif, dea, macd"""
    dif, dea, macd = MACD(df["close"].values, short, long, m)
    df["dif"], df["dea"], df["macd"] = dif, dea, macd
    return df


def add_kdj(df: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
    """追加 KDJ 指标: kdj_k, kdj_d, kdj_j"""
    k, d, j = KDJ(df["close"].values, df["high"].values, df["low"].values, n, m1, m2)
    df["kdj_k"], df["kdj_d"], df["kdj_j"] = k, d, j
    return df


def add_rsi(df: pd.DataFrame, periods=(6, 12, 24)) -> pd.DataFrame:
    """追加 RSI 指标，列名如 rsi6/rsi12/rsi24"""
    close = df["close"].values
    for n in periods:
        df[f"rsi{n}"] = RSI(close, n)
    return df


def add_boll(df: pd.DataFrame, n: int = 20, p: int = 2) -> pd.DataFrame:
    """追加布林带: boll_up, boll_mid, boll_low"""
    up, mid, low = BOLL(df["close"].values, n, p)
    df["boll_up"], df["boll_mid"], df["boll_low"] = up, mid, low
    return df


def add_vol_ma(df: pd.DataFrame, periods=(5, 10)) -> pd.DataFrame:
    """追加成交量均线，列名如 vol_ma5/vol_ma10"""
    vol = df["volume"].values
    for n in periods:
        df[f"vol_ma{n}"] = MA(vol, n)
    return df


def add_all(df: pd.DataFrame) -> pd.DataFrame:
    """一次性追加常用全套指标"""
    add_ma(df)
    add_macd(df)
    add_kdj(df)
    add_rsi(df)
    add_boll(df)
    add_vol_ma(df)
    return df
