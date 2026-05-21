"""股票数据处理工具"""
import akshare as ak
import pandas as pd

# 设置完整显示
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def filter_main_board(df: pd.DataFrame) -> pd.DataFrame:
    """
    统一过滤：剔除ST、只保留沪深主板 60/000/001
    """
    if df.empty:
        return df

    # 剔除ST
    df = df[~df["名称"].str.contains("ST", na=False)]
    # 筛选主板
    cond = (
        df["代码"].str.startswith("60")
        | df["代码"].str.startswith("00")
    )
    df = df[cond].copy()
    return df



def get_zt_stock(date: str) -> pd.DataFrame:
    """
    获取当日涨停股票（已过滤ST/科创/北交所，只留主板）
    :param date: 日期字符串 如 "20260508"
    :return: 涨停DataFrame
    """
    try:
        df = ak.stock_zt_pool_em(date=date)
        # return df
        return filter_main_board(df)
    except Exception as e:
        print(f"获取涨停数据失败: {e}")
        return pd.DataFrame()



def get_zb_stock(date: str) -> pd.DataFrame:
    """
    获取当日炸板股票（已过滤ST/科创/北交所，只留主板）
    :param date: 日期字符串 如 "20260508"
    :return: 炸板DataFrame
    """
    try:
        df = ak.stock_zt_pool_zbgc_em(date=date)
        return filter_main_board(df)
    except Exception as e:
        print(f"获取炸板数据失败: {e}")
        return pd.DataFrame()



def get_yes_zt_today_no_zt(yes_date: str, today_date: str) -> pd.DataFrame:
    """
    获取：获取断板股票
    :param yes_date: 昨日日期
    :param today_date: 今日日期
    :return: 昨日涨停今日非涨停DataFrame
    """
    df_yes = get_zt_stock(yes_date)
    df_today = get_zt_stock(today_date)

    if df_yes.empty:
        return pd.DataFrame()

    yes_code_set = set(df_yes["代码"])
    today_code_set = set(df_today["代码"])

    # 差集：昨日涨停 - 今日涨停
    target_codes = yes_code_set - today_code_set
    df_res = df_yes[df_yes["代码"].isin(target_codes)].copy()
    return df_res



def calculate_limit_price(current_price, limit_ratio=0.1):
    """
    计算涨停/跌停价格
    
    :param current_price: 当前价格
    :param limit_ratio: 涨跌幅限制，默认0.1（10%）
    :return: 涨停价
    """
    return round(current_price * (1 + limit_ratio), 2)

def get_stock_info(stock_code):
    """
    获取股票基本信息
    
    :param stock_code: 股票代码
    :return: 股票信息字典
    """
    try:
        df = ak.stock_individual_info_em(symbol=stock_code)
        if not df.empty:
            return df.set_index('item')['value'].to_dict()
        return {}
    except Exception as e:
        print(f"获取股票信息失败: {e}")
        return {}