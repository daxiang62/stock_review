"""Akshare 数据源客户端
开源免费的财经数据接口，适合日常行情、涨跌停、龙虎榜等数据获取
"""
import akshare as ak
import pandas as pd
from .base_client import BaseStockClient


class AkshareClient(BaseStockClient):
    """Akshare数据源实现"""
    
    def __init__(self, timeout: int = 30, **kwargs):
        super().__init__(**kwargs)
        self.timeout = timeout
    
    def connect(self) -> bool:
        """Akshare不需要显式连接，直接返回True"""
        self.is_connected = True
        return True
    
    def disconnect(self) -> None:
        """不需要断开"""
        self.is_connected = False
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取全市场股票列表"""
        df = ak.stock_info_a_code_name()
        df.columns = ["code", "name"]
        # 添加市场字段
        df["market"] = df["code"].apply(
            lambda x: "SH" if x.startswith("6") else "SZ" if x.startswith(("0","3")) else "BJ"
        )
        return df
    
    def get_daily_kline(self, stock_code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取日线K线数据"""
        code = self._format_stock_code(stock_code, add_market=False)
        start = self._format_date(start_date, "%Y%m%d") if start_date else ""
        end = self._format_date(end_date, "%Y%m%d") if end_date else ""
        
        df = ak.stock_zh_a_hist(symbol=code, start_date=start, end_date=end, adjust="qfq")
        # 统一列名
        rename_map = {
            "日期": "date",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
            "成交额": "amount",
            "涨跌幅": "change_pct"
        }
        df = df.rename(columns=rename_map)
        # 只保留需要的列
        return df[["date", "open", "high", "low", "close", "volume", "amount", "change_pct"]]
    
    def get_limit_up_stocks(self, trade_date: str = None) -> pd.DataFrame:
        """获取涨停股票列表"""
        date = self._format_date(trade_date, "%Y%m%d") if trade_date else ""
        df = ak.stock_zt_pool_em(date=date)
        
        rename_map = {
            "代码": "code",
            "名称": "name",
            "涨跌幅": "change_pct",
            "首次封板时间": "first_limit_up_time",
            "连板数": "limit_up_count",
            "成交额": "amount",
            "流通市值": "float_market_value",
            "所属行业": "industry"
        }
        df = df.rename(columns=rename_map)
        return df[["code", "name", "change_pct", "first_limit_up_time", "limit_up_count", "amount", "float_market_value", "industry"]]
    
    def get_limit_down_stocks(self, trade_date: str = None) -> pd.DataFrame:
        """获取跌停股票列表"""
        date = self._format_date(trade_date, "%Y%m%d") if trade_date else ""
        df = ak.stock_zt_pool_dt_em(date=date)
        
        rename_map = {
            "代码": "code",
            "名称": "name",
            "涨跌幅": "change_pct",
            "成交额": "amount",
            "流通市值": "float_market_value",
            "所属行业": "industry"
        }
        df = df.rename(columns=rename_map)
        return df[["code", "name", "change_pct", "amount", "float_market_value", "industry"]]
    
    def get_stock_finance(self, stock_code: str) -> pd.DataFrame:
        """获取财务报表数据"""
        code = self._format_stock_code(stock_code, add_market=False)
        df = ak.stock_financial_report_sina(stock=code, symbol="资产负债表")
        return df
    
    def get_lhb_data(self, trade_date: str = None) -> pd.DataFrame:
        """获取龙虎榜数据"""
        date = self._format_date(trade_date, "%Y%m%d") if trade_date else ""
        df = ak.stock_lhb_detail_em(date=date)
        
        rename_map = {
            "代码": "code",
            "名称": "name",
            "收盘价": "close",
            "涨跌幅": "change_pct",
            "净额": "net_amount",
            "买入额": "buy_amount",
            "卖出额": "sell_amount",
            "所属行业": "industry"
        }
        df = df.rename(columns=rename_map)
        return df[["code", "name", "close", "change_pct", "net_amount", "buy_amount", "sell_amount", "industry"]]
    
    # ========== 扩展Akshare特有接口 ==========
    def get_boom_stocks(self, trade_date: str = None) -> pd.DataFrame:
        """获取炸板股票列表（Akshare独有）"""
        date = self._format_date(trade_date, "%Y%m%d") if trade_date else ""
        df = ak.stock_zt_pool_zb_em(date=date)
        
        rename_map = {
            "代码": "code",
            "名称": "name",
            "涨跌幅": "change_pct",
            "炸板次数": "boom_count",
            "成交额": "amount",
            "所属行业": "industry"
        }
        df = df.rename(columns=rename_map)
        return df
