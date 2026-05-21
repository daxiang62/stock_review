"""同步报告到 docs 目录的脚本"""
import os
import shutil
from datetime import datetime


def sync_reports_to_docs():
    """将 reports 目录下的报告同步到 docs/reports 目录"""
    reports_src = os.path.join(os.path.dirname(__file__), 'reports')
    docs_reports = os.path.join(os.path.dirname(__file__), 'docs', 'reports')

    if not os.path.exists(reports_src):
        print(f"源目录不存在: {reports_src}")
        return

    os.makedirs(docs_reports, exist_ok=True)

    for filename in os.listdir(reports_src):
        if filename.endswith('.md'):
            src_path = os.path.join(reports_src, filename)

            date_str = filename.split('_')[0]
            year = date_str[:4]
            month = date_str[4:6]

            year_dir = os.path.join(docs_reports, year, month)
            os.makedirs(year_dir, exist_ok=True)

            dst_path = os.path.join(year_dir, filename)
            shutil.copy2(src_path, dst_path)
            print(f"已同步: {filename} -> {year}/{month}/")


def update_daily_stats():
    """更新每日盘面数据统计"""
    print("TODO: 从数据源获取并更新每日盘面统计数据")


if __name__ == "__main__":
    print(f"开始同步报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sync_reports_to_docs()
    print("同步完成")
