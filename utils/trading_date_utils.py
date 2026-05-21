"""A股交易日工具"""
import datetime
from typing import Optional
from chinese_calendar import is_workday, is_holiday

def _is_stock_trading_day(date: datetime.date) -> bool:
    """判断某天是否是A股交易日"""
    # A股交易日 = 周一到周五 且 不是节假日
    # 注意：即使周末调休上班，A股也休市
    return date.weekday() < 5 and not is_holiday(date)

def get_last_trading_date(date: Optional[datetime.date] = None) -> str:
    """
    获取上一个交易日日期
    
    :param date: 基准日期，默认为今天
    :return: 上一个交易日的日期字符串（YYYYMMDD格式）
    """
    if date is None:
        date = datetime.date.today()
    
    current_date = date - datetime.timedelta(days=1)
    while True:
        if _is_stock_trading_day(current_date):
            return current_date.strftime("%Y%m%d")
        
        current_date -= datetime.timedelta(days=1)
        
        if (date - current_date).days > 30:
            raise ValueError("无法找到最近的交易日")

def get_today_trading_date() -> str:
    """
    获取当天日期，如果是交易日则返回日期字符串，否则报错
    
    :return: 交易日日期字符串（YYYYMMDD格式）
    :raises ValueError: 如果今天不是交易日
    """
    today = datetime.date.today()
    date_str = today.strftime("%Y%m%d")
    
    if not _is_stock_trading_day(today):
        if today.weekday() >= 5:
            weekend = "周六" if today.weekday() == 5 else "周日"
            raise ValueError(f"❌ {date_str} 是{weekend}，A股休市")
        elif is_holiday(today):
            raise ValueError(f"❌ {date_str} 是节假日，A股休市")
        else:
            raise ValueError(f"❌ {date_str} 不是交易日")
    
    return date_str

def get_next_trading_date(date: Optional[datetime.date] = None) -> str:
    """
    获取下一个交易日日期
    
    :param date: 基准日期，默认为今天
    :return: 下一个交易日的日期字符串（YYYYMMDD格式）
    """
    if date is None:
        date = datetime.date.today()
    
    current_date = date + datetime.timedelta(days=1)
    while True:
        if _is_stock_trading_day(current_date):
            return current_date.strftime("%Y%m%d")
        
        current_date += datetime.timedelta(days=1)
        
        if (current_date - date).days > 30:
            raise ValueError("无法找到下一个交易日")

if __name__ == "__main__":
    print("[日期工具测试]")
    
    # 测试今天是否是交易日
    try:
        today = get_today_trading_date()
        print(f"[OK] 今天 {today} 是交易日")
    except ValueError as e:
        print(f"[ERROR] {e}")
    
    # 获取上一个交易日
    last_trading = get_last_trading_date()
    print(f"[INFO] 上一个交易日: {last_trading}")
    
    # 获取下一个交易日
    next_trading = get_next_trading_date()
    print(f"[INFO] 下一个交易日: {next_trading}")