"""报告生成器基类模块"""
from abc import ABC, abstractmethod
import os

from utils.log_utils import get_logger

logger = get_logger(__name__)


class BaseReporter(ABC):
    """报告生成器基类

    提供统一的报告生成接口，子类只需实现 build_report 方法定义各自的报告格式
    """

    report_type: str = "report"

    def __init__(self, report_dir: str = None):
        if report_dir is None:
            self.report_dir = os.path.join(os.path.dirname(__file__), '..', 'docs', 'reports')
        else:
            self.report_dir = report_dir
        os.makedirs(self.report_dir, exist_ok=True)

    @abstractmethod
    def build_report(self, date_str: str, stock_info: str, analysis_result: str, **kwargs) -> str:
        """构建报告内容（子类必须实现）

        :param date_str: 日期字符串
        :param stock_info: 股票信息列表
        :param analysis_result: 分析结果
        :param kwargs: 其他参数
        :return: 格式化后的报告内容
        """
        pass

    def save_report(self, report_content: str, date_str: str) -> str:
        """保存报告到文件

        :param report_content: 报告内容
        :param date_str: 日期字符串
        :return: md_path 文件路径
        """
        year = date_str[:4]
        month = date_str[4:6]
        
        # 构建目录路径
        year_dir = os.path.join(self.report_dir, year)
        target_dir = os.path.join(year_dir, month)
        
        # 检查并创建年份目录
        if not os.path.exists(year_dir):
            os.makedirs(year_dir, exist_ok=True)
            logger.info(f"【新的一年】已创建年份目录: {year_dir}")
        else:
            # 年份目录已存在，无需创建
            logger.debug(f"年份目录已存在: {year_dir}")
        
        # 检查并创建月份目录
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            logger.info(f"【新的一月】已创建月份目录: {target_dir}")
        else:
            # 月份目录已存在，无需创建
            logger.debug(f"月份目录已存在: {target_dir}")
        
        md_path = os.path.join(target_dir, f"{date_str}_{self.report_type}_report.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        logger.info(f"报告已保存: {md_path}")
        return md_path
