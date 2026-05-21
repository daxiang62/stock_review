"""断板股票分析器"""
from .base_analyzer import BaseStockAnalyzer


class DBStockAnalyzer(BaseStockAnalyzer):
    """断板股票分析器

    继承自 BaseStockAnalyzer，实现断板的专项分析逻辑
    """

    def build_prompt(self, stock_data: str) -> str:
        """构建断板分析prompt

        :param stock_data: 股票数据描述
        :return: 格式化后的prompt字符串
        """
        return f"""
请在此填写断板股票分析的 prompt 逻辑。

待分析个股信息：
{stock_data}

提示：断板通常指股票从涨停板跌落或未能继续封板的情况，
可分析：断板原因、当日走势、资金博弈情况、后续操作建议等。
"""
