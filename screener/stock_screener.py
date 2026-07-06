"""股票筛选工具
数据源: MooTDX (通达信行情) 拉取日线K线
指标层: MyTT 计算技术指标
筛选层: 内置多种选股策略，也支持自定义策略函数

用法:
    from screener import StockScreener, Strategies

    screener = StockScreener()
    result = screener.screen(Strategies.ma_bullish)
    print(result)
"""
from typing import Callable, Optional, List
import pandas as pd
from MyTT import CROSS

from client import get_client
from client.base_client import BaseStockClient
from utils.log_utils import get_logger
from .indicators import add_all
from .formula import compile_formula

logger = get_logger("stock_screener")

# 策略类型: 输入带指标的K线DataFrame，返回最新一根K线是否满足条件
StrategyFunc = Callable[[pd.DataFrame], bool]

# 结果中展示的关键指标列
_SUMMARY_COLS = [
    "close", "change_pct", "ma5", "ma10", "ma20", "ma60",
    "dif", "dea", "kdj_j", "rsi6",
]


class StockScreener:
    """股票筛选引擎"""

    def __init__(self, client: Optional[BaseStockClient] = None,
                 kline_days: int = 120, min_data_len: int = 60):
        """
        :param client: 数据源客户端，默认使用 MooTDX
        :param kline_days: 每只股票取最近多少根日线用于计算指标
        :param min_data_len: 数据不足该长度的股票直接跳过（指标不可靠）
        """
        self.client = client or get_client("mootdx")
        self.kline_days = kline_days
        self.min_data_len = min_data_len

    # ==================== 股票池 ====================
    def get_stock_pool(self, boards=("60", "000", "001", "002", "003", "300", "301"),
                       exclude_st: bool = True) -> pd.DataFrame:
        """获取待筛选股票池
        :param boards: 保留的代码前缀（默认沪深主板+中小板+创业板，排除科创/北交所）
        :param exclude_st: 是否排除 ST 股
        :return: DataFrame[code, name, market]
        """
        df = self.client.get_stock_list()
        df = df[df["code"].str.startswith(tuple(boards))]
        if exclude_st:
            df = df[~df["name"].str.contains("ST", case=False, na=False)]
        return df.reset_index(drop=True)

    # ==================== 单只股票取数+算指标 ====================
    def _prepare_kline(self, code: str) -> Optional[pd.DataFrame]:
        """拉取单只股票K线并计算指标，数据不足返回 None"""
        try:
            df = self.client.get_daily_kline(code)
        except Exception as e:
            logger.warning(f"{code} 获取K线失败: {e}")
            return None

        if df is None or len(df) < self.min_data_len:
            return None

        df = df.tail(self.kline_days).reset_index(drop=True)
        add_all(df)
        return df

    # ==================== 核心筛选 ====================
    def screen(self, strategy: StrategyFunc,
               stock_pool: Optional[pd.DataFrame] = None,
               limit: Optional[int] = None) -> pd.DataFrame:
        """按策略筛选股票
        :param strategy: 策略函数，接收带指标的K线df，返回最新一根是否命中
        :param stock_pool: 待筛选股票池 DataFrame[code, name]，默认取全市场主板
        :param limit: 只扫描前 N 只（调试用），默认全部
        :return: 命中股票 DataFrame，含代码/名称及关键指标
        """
        if stock_pool is None:
            stock_pool = self.get_stock_pool()
        if limit:
            stock_pool = stock_pool.head(limit)

        total = len(stock_pool)
        strategy_name = getattr(strategy, "__name__", "custom")
        logger.info(f"开始筛选: 策略[{strategy_name}] 股票池共 {total} 只")

        matched: List[dict] = []
        for i, row in enumerate(stock_pool.itertuples(index=False), start=1):
            code, name = row.code, row.name
            df = self._prepare_kline(code)
            if df is None:
                continue

            try:
                if strategy(df):
                    last = df.iloc[-1]
                    record = {"code": code, "name": name}
                    for col in _SUMMARY_COLS:
                        record[col] = round(float(last[col]), 2) if col in df.columns else None
                    matched.append(record)
            except Exception as e:
                logger.warning(f"{code} 策略执行异常: {e}")

            if i % 200 == 0:
                logger.info(f"进度 {i}/{total}，已命中 {len(matched)} 只")

        logger.info(f"筛选完成: 策略[{strategy_name}] 命中 {len(matched)} 只")
        return pd.DataFrame(matched)

    def screen_by_formula(self, formula: str,
                          stock_pool: Optional[pd.DataFrame] = None,
                          limit: Optional[int] = None) -> pd.DataFrame:
        """按 MyTT/通达信 风格选股条件字符串筛选股票
        :param formula: 选股条件字符串，如 "CROSS(MA(C,5), MA(C,10))"
        :param stock_pool: 待筛选股票池 DataFrame[code, name]，默认取全市场主板
        :param limit: 只扫描前 N 只（调试用），默认全部
        :return: 命中股票 DataFrame，含代码/名称及关键指标
        """
        strategy = compile_formula(formula)
        return self.screen(strategy, stock_pool=stock_pool, limit=limit)


class Strategies:
    """内置选股策略集合
    每个策略接收带指标的K线DataFrame，判断最新一根K线是否满足条件
    """

    @staticmethod
    def ma_bullish(df: pd.DataFrame) -> bool:
        """均线多头排列: MA5>MA10>MA20>MA60 且收盘价站上MA5"""
        last = df.iloc[-1]
        return (last["close"] > last["ma5"] > last["ma10"]
                > last["ma20"] > last["ma60"])

    @staticmethod
    def macd_golden_cross(df: pd.DataFrame) -> bool:
        """MACD金叉: DIF上穿DEA，且发生在0轴附近或之上"""
        cross = bool(CROSS(df["dif"].values, df["dea"].values)[-1])
        return cross and df.iloc[-1]["dif"] > 0

    @staticmethod
    def kdj_golden_cross(df: pd.DataFrame) -> bool:
        """KDJ金叉: K上穿D，且处于相对低位(J<50)"""
        cross = bool(CROSS(df["kdj_k"].values, df["kdj_d"].values)[-1])
        return cross and df.iloc[-1]["kdj_j"] < 50

    @staticmethod
    def volume_breakout(df: pd.DataFrame) -> bool:
        """放量突破: 收盘价站上MA20，且成交量放大到5日均量2倍以上"""
        last = df.iloc[-1]
        return (last["close"] > last["ma20"]
                and last["volume"] > 2 * last["vol_ma5"])

    @staticmethod
    def boll_breakout(df: pd.DataFrame) -> bool:
        """布林突破: 收盘价突破布林带上轨"""
        last = df.iloc[-1]
        return last["close"] > last["boll_up"]

    @staticmethod
    def rsi_oversold_rebound(df: pd.DataFrame) -> bool:
        """RSI超卖反弹: 前一日RSI6<20，当日RSI6回升"""
        prev, last = df.iloc[-2], df.iloc[-1]
        return prev["rsi6"] < 20 and last["rsi6"] > prev["rsi6"]
