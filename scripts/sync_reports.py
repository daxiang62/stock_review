"""自动更新 mkdocs.yml 导航"""
import os
import re
from datetime import datetime


def scan_report_files():
    """扫描 docs/reports 目录，返回按年月分组的报告文件"""
    project_root = os.path.dirname(os.path.dirname(__file__))
    docs_reports = os.path.join(project_root, 'docs', 'reports')
    
    reports = {}
    
    if not os.path.exists(docs_reports):
        return reports
    
    for year_dir in sorted(os.listdir(docs_reports), reverse=True):
        year_path = os.path.join(docs_reports, year_dir)
        if not os.path.isdir(year_path):
            continue
            
        if year_dir not in reports:
            reports[year_dir] = {}
            
        for month_dir in sorted(os.listdir(year_path), reverse=True):
            month_path = os.path.join(year_path, month_dir)
            if not os.path.isdir(month_path):
                continue
                
            if month_dir not in reports[year_dir]:
                reports[year_dir][month_dir] = []
                
            for filename in sorted(os.listdir(month_path), reverse=True):
                if filename.endswith('.md'):
                    reports[year_dir][month_dir].append(filename)
    
    return reports


def generate_nav_section(reports):
    """根据报告生成导航配置"""
    nav_lines = []
    
    for year in sorted(reports.keys(), reverse=True):
        nav_lines.append(f"      - {year}年:")
        
        for month in sorted(reports[year].keys(), reverse=True):
            month_int = int(month)
            nav_lines.append(f"          - {month_int}月每日涨停:")
            
            for filename in sorted(reports[year][month], reverse=True):
                date_str = filename.split('_')[0]
                nav_lines.append(f"              - {date_str}: reports/{year}/{month}/{filename}")
    
    return nav_lines


def update_mkdocs_yml():
    """更新 mkdocs.yml 中的导航配置"""
    project_root = os.path.dirname(os.path.dirname(__file__))
    mkdocs_path = os.path.join(project_root, 'mkdocs.yml')
    
    if not os.path.exists(mkdocs_path):
        print(f"mkdocs.yml 不存在: {mkdocs_path}")
        return
    
    reports = scan_report_files()
    new_nav = generate_nav_section(reports)
    
    with open(mkdocs_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'(  - 股票分析报告:).*?(  - 每日盘面分析:)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        before = match.group(1)
        after = match.group(2)
        
        new_section = before + '\n' + '\n'.join(new_nav) + '\n' + after
        new_content = content[:match.start()] + new_section + content[match.end():]
        
        with open(mkdocs_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("已更新 mkdocs.yml 导航配置")
    else:
        print("警告：未在 mkdocs.yml 中找到股票分析报告导航部分")


if __name__ == "__main__":
    print(f"开始更新导航 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    update_mkdocs_yml()
    print("更新完成")
