"""自动更新 mkdocs.yml 导航"""
import os
import sys
import re
from datetime import datetime

# 处理导入：既支持作为包导入，也支持作为脚本直接运行
try:
    from .log_utils import get_logger
except ImportError:
    # 作为脚本运行时，添加项目根目录到路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    from utils.log_utils import get_logger

logger = get_logger(__name__)


class ReportNavUpdater:
    """报告导航更新器"""

    def __init__(self, auto_scan: bool = True, auto_update: bool = True):
        """
        初始化报告导航更新器

        :param auto_scan: 是否自动扫描报告文件，默认为 True
        :param auto_update: 是否自动更新 mkdocs.yml，默认为 True
        """
        self.project_root = os.path.dirname(os.path.dirname(__file__))
        self.docs_reports = os.path.join(self.project_root, 'docs', 'reports')
        self.mkdocs_path = os.path.join(self.project_root, 'mkdocs.yml')
        self.reports = {}
        
        # 类型名称映射
        self.type_map = {
            "zt": "涨停",
            "db": "断板",
            "zb": "炸板"
        }
        
        if auto_scan:
            self.scan_report_files()
            if auto_update:
                self.update_mkdocs_yml()

    def get_report_type_name(self, report_type: str) -> str:
        """获取报告类型对应的中文名称"""
        return self.type_map.get(report_type, report_type)

    def scan_report_files(self):
        """扫描 docs/reports 目录，返回按年月和类型分组的报告文件"""
        self.reports = {}
        
        if not os.path.exists(self.docs_reports):
            logger.warning(f"报告目录不存在: {self.docs_reports}")
            return self.reports
        
        for year_dir in sorted(os.listdir(self.docs_reports), reverse=True):
            year_path = os.path.join(self.docs_reports, year_dir)
            if not os.path.isdir(year_path):
                continue
                
            if year_dir not in self.reports:
                self.reports[year_dir] = {}
                
            for month_dir in sorted(os.listdir(year_path), reverse=True):
                month_path = os.path.join(year_path, month_dir)
                if not os.path.isdir(month_path):
                    continue
                    
                if month_dir not in self.reports[year_dir]:
                    self.reports[year_dir][month_dir] = {}
                    
                for filename in sorted(os.listdir(month_path), reverse=True):
                    if filename.endswith('.md'):
                        # 解析文件名: 20260522_zt_report.md
                        parts = filename.split('_')
                        if len(parts) >= 3:
                            report_type = parts[1]
                            if report_type not in self.reports[year_dir][month_dir]:
                                self.reports[year_dir][month_dir][report_type] = []
                            self.reports[year_dir][month_dir][report_type].append(filename)
        
        logger.info(f"扫描完成，共找到 {len(self.reports)} 年的报告")
        return self.reports

    def generate_nav_section(self):
        """根据报告生成导航配置"""
        if not self.reports:
            return []
            
        nav_lines = []
        
        for year in sorted(self.reports.keys(), reverse=True):
            nav_lines.append(f"      - {year}年:")
            
            for month in sorted(self.reports[year].keys(), reverse=True):
                month_int = int(month)
                
                # 先获取所有报告类型，按 zt -> db -> zb 顺序排列
                report_types = self.reports[year][month].keys()
                # 优先顺序：涨停、断板、炸板
                type_order = ['zt', 'db', 'zb']
                sorted_types = [t for t in type_order if t in report_types] + [t for t in report_types if t not in type_order]
                
                for report_type in sorted_types:
                    type_name = self.get_report_type_name(report_type)
                    nav_lines.append(f"          - {month_int}月每日{type_name}:")
                    
                    for filename in sorted(self.reports[year][month][report_type], reverse=True):
                        date_str = filename.split('_')[0]
                        nav_lines.append(f"              - {date_str}: reports/{year}/{month}/{filename}")
        
        return nav_lines

    def update_mkdocs_yml(self):
        """更新 mkdocs.yml 中的导航配置"""
        if not os.path.exists(self.mkdocs_path):
            logger.error(f"mkdocs.yml 不存在: {self.mkdocs_path}")
            return False
        
        if not self.reports:
            logger.warning("没有扫描到报告文件，跳过更新")
            return False
        
        new_nav = self.generate_nav_section()
        
        with open(self.mkdocs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern = r'(  - 股票分析报告:).*?(  - 每日盘面分析:)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            before = match.group(1)
            after = match.group(2)
            
            new_section = before + '\n' + '\n'.join(new_nav) + '\n' + after
            new_content = content[:match.start()] + new_section + content[match.end():]
            
            with open(self.mkdocs_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info("已更新 mkdocs.yml 导航配置")
            return True
        else:
            logger.warning("未在 mkdocs.yml 中找到股票分析报告导航部分")
            return False


if __name__ == "__main__":
    logger.info(f"开始更新导航 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    ReportNavUpdater(auto_scan=True, auto_update=True)
    logger.info("更新完成")
