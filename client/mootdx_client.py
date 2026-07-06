"""MooTDX 数据源客户端
对接通达信行情服务器，速度极快，支持实时行情、历史K线、分时数据等
优势: 本地直连券商行情服务器，无API限制，速度是公开接口的10倍以上
"""
from typing import Optional
import pandas as pd
from mootdx.quotes import Quotes
from mootdx.utils import get_best_host
from .base_client import BaseStockClient


class MootdxClient(BaseStockClient):
    """MooTDX通达信数据源实现"""
    
    def __init__(self, market: str = "std", server: Optional[tuple] = None, **kwargs):
        """初始化MooTDX客户端
        :param market: 市场类型: std=沪深京, hk=港股, us=美股
        :param server: 自定义行情服务器 (host, port)，不填自动选最快的
        """
        super().__init__(**kwargs)
        self.market = market
        self.custom_server = server
        self.client: Optional[Quotes] = None
    
    def connect(self) -> bool:
        """连接通达信行情服务器"""
        try:
            # 自动选择最优服务器
            if not self.custom_server:
                best_host = get_best_host(market=self.market)
                if not best_host:
                    print("无法获取最优通达信服务器")
                    return False
                host, port = best_host["ip"], best_host["port"]
            else:
                host, port = self.custom_server
            
            # 初始化行情客户端
            self.client = Quotes.factory(market=self.market, host=host, port=port, timeout=5)
            # 测试连接
            test_data = self.client.quotes(symbol=["600000"])
            if test_data is not None and len(test_data) > 0:
                self.is_connected = True
                print(f"MooTDX连接成功: {host}:{port}")
                return True
            return False
        except Exception as e:
            print(f"MooTDX连接失败: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """断开连接"""
        if self.client:
            self.client.close()
            self.is_connected = False
            self.client = None
    
    def _tdx_code_to_market(self, stock_code: str) -> int:
        """股票代码转MooTDX市场标识
        0=深市, 1=沪市, 2=北交所
        """
        code = stock_code.replace(".SH", "").replace(".SZ", "").replace(".BJ", "")
        if code.startswith("6"):
            return 1
        elif code.startswith(("0", "3")):
            return 0
        elif code.startswith(("8", "4")):
            return 2
        return 0  # 默认深市
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取全市场股票列表"""
        if not self.is_connected:
            self.connect()
        
        # 获取沪深股票列表
        sh_df = self.client.stock_list(market=1)
        sz_df = self.client.stock_list(market=0)
        bj_df = self.client.stock_list(market=2)
        
        df = pd.concat([sh_df, sz_df, bj_df], ignore_index=True)
        df.columns = ["code", "name", "pinyin"]
        # 添加市场字段
        df["market"] = df["code"].apply(
            lambda x: "SH" if x.startswith("6") else "SZ" if x.startswith(("0","3")) else "BJ"
        )
        return df[["code", "name", "market"]]
    
    def get_daily_kline(self, stock_code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取日线K线数据（支持历史所有数据）"""
        if not self.is_connected:
            self.connect()
        
        market = self._tdx_code_to_market(stock_code)
        code = self._format_stock_code(stock_code, add_market=False)
        
        # 拉取全部日线数据
        df = self.client.bars(symbol=code, market=market, category=9, count=10000)  # category=9=日线
        
        # 格式化列名
        rename_map = {
            "datetime": "date",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "vol": "volume",
            "amount": "amount"
        }
        df = df.rename(columns=rename_map)
        
        # 转换日期格式
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        
        # 按日期范围过滤
        if start_date:
            start = self._format_date(start_date, "%Y-%m-%d")
            df = df[df["date"] >= start]
        if end_date:
            end = self._format_date(end_date, "%Y-%m-%d")
            df = df[df["date"] <= end]
        
        # 计算涨跌幅
        df["change_pct"] = df["close"].pct_change() * 100
        
        return df[["date", "open", "high", "low", "close", "volume", "amount", "change_pct"]].reset_index(drop=True)
    
    def get_limit_up_stocks(self, trade_date: str = None) -> pd.DataFrame:
        """MooTDX不直接提供涨跌停列表，需要本地计算"""
        raise NotImplementedError("MooTDX不直接提供涨跌停数据，建议结合Akshare使用或本地计算")
    
    def get_limit_down_stocks(self, trade_date: str = None) -> pd.DataFrame:
        """MooTDX不直接提供涨跌停列表"""
        raise NotImplementedError("MooTDX不直接提供涨跌停数据，建议结合Akshare使用或本地计算")
    
    def get_stock_finance(self, stock_code: str) -> pd.DataFrame:
        """MooTDX不提供财务数据"""
        raise NotImplementedError("MooTDX不支持财务数据获取，请使用Baostock/Tushare")
    
    def get_lhb_data(self, trade_date: str = None) -> pd.DataFrame:
        """MooTDX不提供龙虎榜数据"""
        raise NotImplementedError("MooTDX不支持龙虎榜数据获取，请使用Akshare")
    
    # ========== MooTDX独有高性能接口 ==========
    def get_realtime_quotes(self, stock_codes: list) -> pd.DataFrame:
        """获取多只股票的实时行情（毫秒级延迟）
        :param stock_codes: 股票代码列表，如 ["600000", "000001"]
        """
        if not self.is_connected:
            self.connect()
        
        # 批量获取行情
        quotes = self.client.quotes(symbol=stock_codes)
        
        rename_map = {
            "symbol": "code",
            "name": "name",
            "price": "current_price",
            "open": "open",
            "high": "high",
            "low": "low",
            "last_close": "prev_close",
            "vol": "volume",
            "amount": "amount",
            "bid1": "bid1",
            "bid1_vol": "bid1_vol",
            "ask1": "ask1",
            "ask1_vol": "ask1_vol"
        }
        quotes = quotes.rename(columns=rename_map)
        # 计算涨跌幅
        quotes["change_pct"] = (quotes["current_price"] / quotes["prev_close"] - 1) * 100
        
        return quotes[[
            "code", "name", "current_price", "change_pct", "open", "high", "low", 
            "prev_close", "volume", "amount", "bid1", "bid1_vol", "ask1", "ask1_vol"
        ]]
    
    def get_minute_kline(self, stock_code: str, period: int = 1) -> pd.DataFrame:
        """获取分钟K线数据
        :param period: 分钟级别: 1=1分钟, 5=5分钟, 15=15分钟, 30=30分钟, 60=60分钟
        """
        if not self.is_connected:
            self.connect()
        
        market = self._tdx_code_to_market(stock_code)
        code = self._format_stock_code(stock_code, add_market=False)
        
        # 映射分钟级别
        category_map = {1: 0, 5: 1, 15: 2, 30: 3, 60: 4}
        category = category_map.get(period, 0)
        
        df = self.client.bars(symbol=code, market=market, category=category, count=10000)
        df["datetime"] = df["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
        
        rename_map = {
            "datetime": "time",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "vol": "volume",
            "amount": "amount"
        }
        return df.rename(columns=rename_map).reset_index(drop=True)
    
    def get_transaction_detail(self, stock_code: str, date: str = None) -> pd.DataFrame:
        """获取当日逐笔成交明细"""
        if not self.is_connected:
            self.connect()
        
        market = self._tdx_code_to_market(stock_code)
        code = self._format_stock_code(stock_code, add_market=False)
        
        df = self.client.transaction(symbol=code, market=market, start=0, count=2000)
        df["time"] = df["time"].astype(str).apply(lambda x: f"{x[:2]}:{x[2:4]}:{x[4:]}")
        
        rename_map = {
            "time": "time",
            "price": "price",
            "vol": "volume",
            "num": "trade_count",
            "buyorsell": "direction"  # 0=卖, 1=买
        }
        df = df.rename(columns=rename_map)
        df["direction"] = df["direction"].map({0: "卖", 1: "买"})
        
        return df[["time", "price", "volume", "direction", "trade_count"]]
