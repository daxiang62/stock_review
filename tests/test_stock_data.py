"""测试股票数据获取函数"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import akshare as ak
import pandas as pd

from utils import get_zt_stock, get_zb_stock, get_yes_zt_today_no_zt


# ==================== 测试调用示例 ====================
if __name__ == "__main__":
    today   = "20260514"
    yesterday = "20260513"

    # 1. 涨停
    df_zt = get_zt_stock(today)
    print(f"\n==== {today} 主板非ST涨停股票共 {len(df_zt)} 只）====")
    # # 2. 炸板
    # df_zb = get_zb_stock(today)
    # print(f"\n==== {today} 主板非ST炸板股票共 {len(df_zb)} 只）====")
    # # 3. 断板
    # df_yes_no = get_yes_zt_today_no_zt(yesterday, today)
    # print(f"\n==== {today} 断板股票共 {len(df_yes_no)} 只）====")

    print(df_zt)
    #print(df_yes_no[["代码", "名称", "涨跌幅", "所属行业", "成交额", "流通市值", "总市值", "换手率", "封板资金", "炸板次数", "连板数"]])
