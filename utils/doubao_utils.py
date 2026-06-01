"""豆包API调用工具 - 优化版"""
import os
from typing import Optional, List, Dict, Any, Iterator
from volcenginesdkarkruntime import Ark

# 导入日志工具
from .log_utils import get_logger
logger = get_logger(__name__)





# 尝试加载配置文件
try:
    from dotenv import load_dotenv
    # 查找config/.env文件
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
    env_path = os.path.join(config_dir, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        logger.info(f"已加载配置文件: {env_path}")
    else:
        logger.warning(f"未找到配置文件: {env_path}")
except ImportError:
    logger.warning("未安装 python-dotenv，配置文件将不会被自动加载")

class DoubaoClient:
    """
    豆包API客户端 - 封装了方舟平台的豆包模型调用
    
    支持功能：
    - 文本对话
    - 图片理解（多模态）
    - 流式响应
    - 多模型支持
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None
        ):
        """
        初始化豆包客户端
        
        :param api_key: 豆包API Key，不提供则从环境变量 ARK_API_KEY 获取
        :param base_url: API基础URL，不提供则从环境变量 ARK_BASE_URL 获取
        :param default_model: 默认使用的模型，不提供则从环境变量 ARK_DEFAULT_MODEL 获取
        """
        self.api_key = api_key or os.environ.get("ARK_API_KEY")
        self.base_url = base_url or os.environ.get("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
        self.default_model = default_model or os.environ.get("ARK_DEFAULT_MODEL", "doubao-seed-2-0-pro")
        
        if not self.api_key:
            logger.warning("未配置ARK_API_KEY环境变量，请确保已设置")
        
        self._client = None
    
    @property
    def client(self) -> Ark:
        """获取或创建Ark客户端实例"""
        if self._client is None:
            self._client = Ark(
                base_url=self.base_url,
                api_key=self.api_key,
            )
        return self._client



    def responses_doubao(self, **kwargs) -> Any:
        """
        使用responses API创建响应（支持web_search等工具）

        :param kwargs: responses.create()的参数
        :return: 响应结果
        """
        if not self.api_key:
            raise ValueError("API Key未配置，请设置ARK_API_KEY环境变量或传入api_key参数")

        # 如果用户没有传入model参数，使用默认模型
        if 'model' not in kwargs or kwargs['model'] is None:
            kwargs['model'] = self.default_model

        try:
            return self.client.responses.create(**kwargs)
        except Exception as e:
            logger.error(f"调用豆包responses API失败: {str(e)}")
            raise
        
    
    def chat_doubao(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
        **kwargs
        ) -> Any:
        """
        发送消息给豆包（使用chat.completions API）
        
        :param messages: 消息列表，格式: [{"role": "user", "content": "text"}]
        :param model: 模型名称，默认为default_model
        :param temperature: 温度参数，控制输出随机性，范围0-1
        :param max_tokens: 最大生成token数
        :param stream: 是否启用流式响应
        :param kwargs: 其他可选参数
        :return: 响应结果或流式生成器
        """
        if not self.api_key:
            raise ValueError("API Key未配置，请设置ARK_API_KEY环境变量或传入api_key参数")
        
        model_name = model or self.default_model
        
        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                **kwargs
            )
            
            return response
        
        except Exception as e:
            logger.error(f"调用豆包API失败: {str(e)}")
            raise
    
    def ask_with_image(self, prompt: str, image_url: str, **kwargs) -> str:
        """
        便捷方法：发送图文消息（多模态）
        
        :param prompt: 用户提问
        :param image_url: 图片URL
        :param kwargs: 其他参数
        :return: 回答内容
        """
        messages = [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": prompt}
            ]
        }]
        return self.chat_doubao(messages, **kwargs)
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表（需要平台支持）"""
        return [
            "doubao-seed-2-0-pro",
            "doubao-3",
            "doubao-3-mini",
            "doubao-3-ultra"
        ]
    
# 创建全局实例
_doubao_client = None

def get_doubao_client(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    default_model: Optional[str] = None,
    force_new: bool = False
    ) -> DoubaoClient:
    """
    获取全局豆包客户端实例（单例模式）
    
    :param api_key: API Key
    :param base_url: 基础URL
    :param default_model: 默认模型
    :param force_new: 是否强制创建新实例
    :return: DoubaoClient实例
    """
    global _doubao_client
    
    if base_url is None:
        base_url = os.environ.get("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
    if default_model is None:
        default_model = os.environ.get("ARK_DEFAULT_MODEL", "doubao-seed-2-0-pro")
    
    if force_new or _doubao_client is None:
        _doubao_client = DoubaoClient(api_key, base_url, default_model)
    return _doubao_client

# ==================== 流式输出处理工具函数 ====================

def process_stream_chat(stream_response) -> Iterator[str]:
    """
    处理 chat.completions API 的流式响应
    
    :param stream_response: chat.completions.create(stream=True) 返回的流式响应
    :return: 生成器，逐块返回文本内容
    """
    for chunk in stream_response:
        if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
            delta = chunk.choices[0].delta
            if hasattr(delta, 'content') and delta.content:
                yield delta.content

def process_stream_responses(stream_response) -> Iterator[str]:
    """
    处理 responses API 的流式响应
    
    :param stream_response: responses.create(stream=True) 返回的流式响应
    :return: 生成器，逐块返回文本内容
    """
    for event in stream_response:
        if hasattr(event, 'type'):
            if event.type == 'response.output_text.delta':
                if hasattr(event, 'delta'):
                    yield event.delta
            elif event.type == 'response.completed':
                break

def process_response_output(response) -> str:
    """
    处理 responses API 的非流式响应
    
    :param response: responses.create() 返回的响应对象
    :return: 解析后的文本内容
    """
    result_text = ""
    for item in response.output:
        if hasattr(item, 'content'):
            for part in item.content:
                if hasattr(part, 'text'):
                    result_text += part.text.strip(' ')
    return result_text


def calculate_web_search_cost(response) -> Dict[str, Any]:
    """
    计算联网搜索收费统计
    
    :param response: responses.create() 返回的响应对象
    :return: 包含收费统计信息的字典
    """
    cost_info = {
        "web_search_times": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "search_engine_queries": 0,
        "has_web_search": False
    }
    
    if not hasattr(response, 'usage') or not response.usage:
        return cost_info
    
    usage = response.usage
    cost_info["input_tokens"] = getattr(usage, 'input_tokens', 0)
    cost_info["output_tokens"] = getattr(usage, 'output_tokens', 0)
    cost_info["total_tokens"] = getattr(usage, 'total_tokens', 0)
    
    if hasattr(usage, 'tool_usage') and usage.tool_usage:
        cost_info["web_search_times"] = getattr(usage.tool_usage, 'web_search', 0)
        
    if hasattr(usage, 'tool_usage_details') and usage.tool_usage_details:
        web_search_details = getattr(usage.tool_usage_details, 'web_search', None)
        if web_search_details and isinstance(web_search_details, dict):
            cost_info["search_engine_queries"] = web_search_details.get('search_engine', 0)
    
    cost_info["has_web_search"] = cost_info["web_search_times"] > 0
    return cost_info


def print_web_search_cost(response):
    """
    打印联网搜索收费统计信息

    :param response: responses.create() 返回的响应对象
    """
    cost_info = calculate_web_search_cost(response)
    logger.info(response.usage)
    logger.info(f"[收费统计] web_search工具次数={cost_info['web_search_times']}, "
                f"search_engine实际搜索次数={cost_info['search_engine_queries']}, "
                f"输入Token={cost_info['input_tokens']}, "
                f"输出Token={cost_info['output_tokens']}, "
                f"总Token={cost_info['total_tokens']}")
                