"""股票分析器基类模块"""
from abc import ABC, abstractmethod
from typing import Iterator, Any, Dict

from utils.doubao_utils import (
    get_doubao_client,
    print_web_search_cost,
    process_stream_responses,
    process_response_output
)


class BaseStockAnalyzer(ABC):
    """股票分析器基类

    提供统一的分析接口，子类只需实现 build_prompt 方法定义各自的分析逻辑
    """

    def __init__(self):
        self.client = get_doubao_client()
        self.tools = [{"type": "web_search"}]

    @abstractmethod
    def build_prompt(self, stock_data: str) -> str:
        """构建分析prompt（子类必须实现）

        :param stock_data: 股票数据描述
        :return: 格式化后的prompt字符串
        """
        pass

    def analyze(self, stock_data: str, **kwargs) -> Any:
        """执行股票分析

        :param stock_data: 股票数据描述
        :param kwargs: 其他参数（stream=True 时支持流式输出）
        :return: 非流式返回分析结果字符串，流式返回生成器
        """
        prompt = self.build_prompt(stock_data)
        messages_input = [{"role": "user", "content": prompt}]
        response = self.client.responses_doubao(input=messages_input, tools=self.tools, **kwargs)

        print_web_search_cost(response)

        if kwargs.get('stream', False):
            return process_stream_responses(response)

        return process_response_output(response)
