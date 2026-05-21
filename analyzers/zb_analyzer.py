"""炸板股票分析器"""
from .base_analyzer import BaseStockAnalyzer


class ZBStockAnalyzer(BaseStockAnalyzer):
    """炸板股票分析器

    继承自 BaseStockAnalyzer，实现炸板的专项分析逻辑
    """

    def build_prompt(self, stock_data: str) -> str:
        """构建炸板分析prompt

        :param stock_data: 股票数据描述
        :return: 格式化后的prompt字符串
        """
        return f"""
请在此填写炸板股票分析的 prompt 逻辑。

待分析个股信息：
{stock_data}

提示：炸板通常指涨停板被打开、封板失败的情况，
可分析：炸板原因、主力意图、抛压来源、尾盘走势、后续操作建议等。
"""
