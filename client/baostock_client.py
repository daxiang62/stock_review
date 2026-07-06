"""Baostock 数据源客户端
免费开源的证券数据接口，财务数据稳定，适合基本面分析
"""
import baostock as bs
import pandas as pd
from .base_client import BaseStockClient


class BaostockClient(BaseStockClient):
    """Baostock数据源实现"""
    
    
    def connect(self) -> bool:
        """连接Baostock服务器"""
        try:
            lg = bs.login()
            if lg.error_code == '0':
                self.is_connected = True
                return True
            print(f"Baostock连接失败: {lg.error_msg}")
            return False
        except Exception as e:
            print(f"Baostock连接异常: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """断开连接"""
        if self.is_connected:
            bs.logout()
            self.is_connected = False
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取全市场股票列表"""
        if not self.is_connected:
            self.connect()
        
        rs = bs.query_all_stock(day="latest")
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        
        df = pd.DataFrame(data_list, columns=rs.fields)
        df.columns = ["code", "name", "isST"]
        df["code"] = df["code"].str.replace(".", "")
        return df
    
    def get_daily_kline(self, stock_code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取日线K线数据（复权数据更准确）"""
        if not self.is_connected:
            self.connect()
        
        code = self._format_stock_code(stock_code, add_market=True).lower()
        start = self._format_date(start_date, "%Y-%m-%d") if start_date else "2015-01-01"
        end = self._format_date(end_date, "%Y-%m-%d") if end_date else pd.Timestamp.now().strftime("%Y-%m-%d")
        
        rs = bs.query_history_k_data_plus(
            code,
            "date,open,high,low,close,volume,amount,pctChg",
            start_date=start,
            end_date=end,
            frequency="d",
            adjustflag="2"  # 2=后复权，1=前复权，0=不复权
        )
        
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        
        df = pd.DataFrame(data_list, columns=rs.fields)
        # 转换数据类型
        numeric_cols = ["open", "high", "low", "close", "volume", "amount", "pctChg"]
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)
        df = df.rename(columns={"pctChg": "change_pct"})
        return df
    
    def get_limit_up_stocks(self, trade_date: str = None) -> pd.DataFrame:
        """Baostock不直接提供涨跌停数据，返回空"""
        raise NotImplementedError("Baostock不支持涨跌停数据获取，请使用Akshare")
    
    def get_limit_down_stocks(self, trade_date: str = None) -> pd.DataFrame:
        """Baostock不直接提供涨跌停数据"""
        raise NotImplementedError("Baostock不支持涨跌停数据获取，请使用Akshare")
    
    def get_stock_finance(self, stock_code: str) -> pd.DataFrame:
        """获取季度财务数据"""
        if not self.is_connected:
            self.connect()
        
        code = self._format_stock_code(stock_code, add_market=True).lower()
        rs = bs.query_quarterly_report_data(code=code, year=2023, quarter=4)
        
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        
        df = pd.DataFrame(data_list, columns=rs.fields)
        return df
    
    def get_lhb_data(self, trade_date: str = None) -> pd.DataFrame:
        """Baostock不提供龙虎榜数据"""
        raise NotImplementedError("Baostock不支持龙虎榜数据获取，请使用Akshare")
    
    # ========== Baostock独有接口 ==========
    def get_stock_growth(self, stock_code: str) -> pd.DataFrame:
        """获取成长能力指标（营收增长率、净利润增长率等）"""
        if not self.is_connected:
            self.connect()
        
        code = self._format_stock_code(stock_code, add_market=True).lower()
        rs = bs.query_growth_data(code=code, year=2023, quarter=4)
        
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        
        return pd.DataFrame(data_list, columns=rs.fields)
