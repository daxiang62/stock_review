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
        response = self.client.responses_doubao(
            input=messages_input, 
            tools=self.tools,
            **kwargs
            )

        print_web_search_cost(response)

        if kwargs.get('stream', False):
            return process_stream_responses(response)

        return process_response_output(response)
    
    def analyze_batches(self, date_str: str, stock_data, batch_size: int = 10, max_batches: int = 20, limit: int = 0) -> str:
        """使用上下文缓存分批分析股票
        
        :param date_str: 日期字符串 
        :param stock_data: 股票数据（支持 str 或 list）
        :param batch_size: 每次输出的股票数量（默认10只）
        :param max_batches: 最大批次数（防止无限循环，默认20）
        :param limit: 分析数量限制（0表示不限制）
        :return: 合并后的完整分析结果
        """
        all_results = ""
        
        # 计算股票数量
        if isinstance(stock_data, str):
            stock_lines = [line.strip() for line in stock_data.split('\n') if line.strip()]
        else:
            stock_lines = stock_data
        stock_count = len(stock_lines)
        
        # 如果没有股票，直接返回空结果
        if stock_count == 0:
            return all_results
        
        # 计算需要的批次数（向上取整）
        if limit > 0 and limit <= stock_count:
            required_batches = (limit + batch_size - 1) // batch_size
        else:
            required_batches = (stock_count + batch_size - 1) // batch_size
        # 不超过最大批次限制
        actual_batches = min(required_batches, max_batches)
        
        # 第一次：完整提示 + 所有股票
        prompt = self.build_prompt(date_str, stock_data)
        
        response = self.client.responses_doubao(
            input=[{"role": "user", "content": prompt}],
            tools=self.tools,
        )
        all_results += process_response_output(response)
        
        # 后续：只说"请继续"（如果需要多批次）
        for _ in range(1, actual_batches):
            response = self.client.responses_doubao(
                input=[{"role": "user", "content": "请继续"}],
                previous_response_id=response.id
            )
            all_results += process_response_output(response)
        
        return all_results
