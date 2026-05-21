"""股票豆包专用函数分析测试脚本"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from utils import get_zt_stock, get_doubao_client, process_stream_chat, process_stream_responses
from analyzers import ZTStockAnalyzer
from utils import get_today_trading_date, get_last_trading_date



def test_analyze_zt_stock():
    """测试 ZTStockAnalyzer 涨停分析器"""
    print("=" * 50)
    print("测试 ZTStockAnalyzer 涨停分析器")
    print("=" * 50)
    print("\n1. 获取交易日日期...")
    trading_date = get_today_trading_date()
    print(f"   今天 {trading_date} 是交易日")
    
    print("\n2. 获取涨停股票数据...")
    zt_df = get_zt_stock(trading_date)
    if zt_df.empty:
        print("   未获取到涨停数据")
        return
    print(f"   共 {len(zt_df)} 只主板非ST涨停股票")

    # 准备分析数据
    stock_info = []
    for _, row in zt_df.head(3).iterrows():  # 只取前3只
        stock_info.append(f"- {row['代码']} {row['名称']} 涨跌幅:{row['涨跌幅']}%") 
    stock_data_text = "\n".join(stock_info)
    print(f"\n3. 分析数据已准备，共 {len(stock_info)} 只股票")
    zt_analyzer = ZTStockAnalyzer()
    print(zt_analyzer.analyze(stock_data_text))

     # 调用豆包分析（使用流式响应） 
    # for chunk in zt_analyzer.analyze(stock_data_text, stream=True):
    #     print(chunk, end='', flush=True)
    

if __name__ == "__main__":
    test_analyze_zt_stock()
