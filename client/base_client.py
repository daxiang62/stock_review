"""股票数据源基类
统一所有数据源的接口规范，方便后续切换和扩展数据源
"""
from abc import ABC, abstractmethod
import pandas as pd
from datetime import datetime


class BaseStockClient(ABC):
    """股票数据源抽象基类"""
    
    def __init__(self, **kwargs):
        """初始化客户端
        :param kwargs: 各数据源需要的配置参数（token、超时等）
        """
        self.name = self.__class__.__name__
        self.is_connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """连接数据源，成功返回True，失败返回False"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """断开数据源连接"""
        pass
    
    def __enter__(self):
        """上下文管理器支持"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.disconnect()
    
    # ==================== 统一数据接口 ====================
    @abstractmethod
    def get_stock_list(self) -> pd.DataFrame:
        """获取全市场股票列表
        :return: DataFrame，列至少包含：code(代码), name(名称), market(市场)
        """
        pass
    
    @abstractmethod
    def get_daily_kline(self, stock_code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取日线K线数据
        :param stock_code: 股票代码，如"600000"或"600000.SH"
        :param start_date: 开始日期，格式"YYYY-MM-DD"或"YYYYMMDD"
        :param end_date: 结束日期，格式"YYYY-MM-DD"或"YYYYMMDD"
        :return: DataFrame，列至少包含：date(日期), open(开盘), high(最高), low(最低), close(收盘), volume(成交量), amount(成交额)
        """
        pass
    
    @abstractmethod
    def get_limit_up_stocks(self, trade_date: str = None) -> pd.DataFrame:
        """获取指定日期的涨停股票列表
        :param trade_date: 交易日期，默认最近交易日
        :return: DataFrame，列至少包含：code, name, change_pct, first_limit_up_time, limit_up_count
        """
        pass
    
    @abstractmethod
    def get_limit_down_stocks(self, trade_date: str = None) -> pd.DataFrame:
        """获取指定日期的跌停股票列表"""
        pass
    
    @abstractmethod
    def get_stock_finance(self, stock_code: str) -> pd.DataFrame:
        """获取股票财务数据"""
        pass
    
    @abstractmethod
    def get_lhb_data(self, trade_date: str = None) -> pd.DataFrame:
        """获取龙虎榜数据"""
        pass
    
    # ==================== 工具方法 ====================
    def _format_date(self, date_str: str, output_format: str = "%Y%m%d") -> str:
        """统一日期格式转换"""
        if not date_str:
            return datetime.now().strftime(output_format)
        
        # 处理常见格式
        for fmt in ["%Y-%m-%d", "%Y%m%d", "%Y/%m/%d"]:
            try:
                return datetime.strptime(date_str, fmt).strftime(output_format)
            except ValueError:
                continue
        raise ValueError(f"不支持的日期格式: {date_str}")
    
    def _format_stock_code(self, stock_code: str, add_market: bool = True) -> str:
        """统一股票代码格式
        :param add_market: 是否添加市场后缀（.SH/.SZ）
        """
        code = stock_code.replace(".SH", "").replace(".SZ", "").replace(".BJ", "")
        if not add_market:
            return code
        
        if code.startswith("6"):
            return f"{code}.SH"
        elif code.startswith("0") or code.startswith("3"):
            return f"{code}.SZ"
        elif code.startswith("8") or code.startswith("4"):
            return f"{code}.BJ"
        return code
