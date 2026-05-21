"""每日股票分析自动化脚本"""
import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import get_zt_stock
from analyzers import ZTStockAnalyzer
from reporters import ZTReporter
from utils.trading_date_utils import get_today_trading_date, get_last_trading_date
from utils.log_utils import get_logger

logger = get_logger("daily_analyze")

def generate_report(date_str):
    """生成股票分析报告"""
    logger.info(f"📊 开始分析 {date_str} 涨停股票")
    
    # 获取涨停数据
    zt_df = get_zt_stock(date_str)
    if zt_df.empty:
        logger.error("未获取到涨停数据")
        return None
    
    # 准备分析数据（只取前五支股票）
    stock_info = []
    for _, row in zt_df.head(5).iterrows():
        stock_info.append(f"- {row['代码']} {row['名称']} 涨跌幅:{row['涨跌幅']:.2f}%")
    
    stock_data_text = "\n".join(stock_info)
    
    # 调用豆包分析
    logger.info(f"开始分析 {len(stock_info)} 只股票")
    zt_analyzer = ZTStockAnalyzer()
    result = zt_analyzer.analyze(stock_data_text)
    
    # 使用报告生成器
    reporter = ZTReporter()
    report = reporter.build_report(
        date_str=date_str,
        stock_info=stock_data_text,
        analysis_result=result,
        total_stocks=len(zt_df)
    )
    
    return report

def save_report(report, date_str):
    """保存报告到文件"""
    reporter = ZTReporter()
    md_path = reporter.save_report(report, date_str)
    logger.info(f"✅ 报告已保存: {md_path}")
    return md_path

def main():
    parser = argparse.ArgumentParser(description='每日股票分析')
    parser.add_argument('--today', action='store_true', help='分析今天的数据（默认分析最近交易日）')
    args = parser.parse_args()
    
    # 获取日期
    try:
        if args.today:
            date_str = get_today_trading_date()
            msg = f"分析今天: {date_str}"
        else:
            date_str = get_last_trading_date()
            msg = f"分析最近交易日: {date_str}"
        logger.info(f"📅 {msg}")
    except ValueError as e:
        logger.error(f"❌ 获取日期失败: {e}")
        return
    
    # 生成报告
    report = generate_report(date_str)
    if not report:
        return
    
    # 保存报告
    save_report(report, date_str)
    
    logger.info("🎉 分析任务完成")

if __name__ == "__main__":
    main()
