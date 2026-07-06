"""股票筛选工具包
基于 MooTDX 行情数据 + MyTT 技术指标的选股引擎

统一入口:
    from screener import screen_stocks

    # 直接用 MyTT/通达信 风格的条件语言选股
    result = screen_stocks("CROSS(MA(C,5), MA(C,10))")
    result = screen_stocks("(C > MA(C,20)) AND (VOL > MA(VOL,5)*2)")
    print(result)
"""
from typing import Optional
import pandas as pd

from .stock_screener import StockScreener, Strategies
from .formula import compile_formula
from . import indicators


def screen_stocks(formula: str,
                  screener: Optional[StockScreener] = None,
                  stock_pool: Optional[pd.DataFrame] = None,
                  limit: Optional[int] = None,
                  **screener_kwargs) -> pd.DataFrame:
    """统一选股入口: 传入 MyTT/通达信 风格的选股条件字符串，返回命中股票

    :param formula: 选股条件字符串，如 "CROSS(MA(C,5), MA(C,10))"
    :param screener: 可复用的 StockScreener 实例，默认新建（用 MooTDX 数据源）
    :param stock_pool: 待筛选股票池 DataFrame[code, name]，默认全市场主板
    :param limit: 只扫描前 N 只（调试用），默认全部
    :param screener_kwargs: 透传给 StockScreener 的初始化参数（如 kline_days）
    :return: 命中股票 DataFrame，含代码/名称及关键指标
    """
    screener = screener or StockScreener(**screener_kwargs)
    return screener.screen_by_formula(formula, stock_pool=stock_pool, limit=limit)


__all__ = [
    "screen_stocks",
    "compile_formula",
    "StockScreener",
    "Strategies",
    "indicators",
]
