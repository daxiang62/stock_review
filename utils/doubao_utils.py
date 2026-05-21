"""豆包API调用工具 - 优化版"""
import os
from typing import Optional, List, Dict, Any, Iterator

# 导入日志工具
from .log_utils import get_logger
logger = get_logger(__name__)

try:
    from volcenginesdkarkruntime import Ark
except ImportError:
    raise ImportError("请安装 volcenginesdkarkruntime: pip install volcenginesdkarkruntime")

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



def analyze_stock_data(stock_data: str, **kwargs) -> str:
    """
    便捷函数：让豆包分析股票数据
    
    :param stock_data: 股票数据描述
    :param kwargs: 其他参数
    :return: 分析结果
    """
    prompt = f"""请分析以下股票数据并给出投资建议：

    {stock_data}

    请从以下几个方面进行分析：
    1. 涨停股票的行业分布
    2. 连板情况分析
    3. 潜在投资机会
    4. 风险提示
    """
    client = get_doubao_client()
    tools = [{
    "type": "web_search",
    }]
    messages_input = [{"role": "user", "content": prompt}]
    response = client.chat_doubao(messages_input, **kwargs)
    # 解析响应
    if hasattr(response, 'choices') and len(response.choices) > 0:
        choice = response.choices[0]
        if hasattr(choice, 'message'):
            return choice.message.content
    return str(response)


def analyze_zt_stock(stock_data: str, **kwargs):
    """
    便捷函数：让豆包分析股票数据
    
    :param stock_data: 股票数据描述
    :param kwargs: 其他参数（stream=True 时支持流式输出）
    :return: 非流式返回分析结果字符串，流式返回生成器
    """
    prompt = f"""
    你是资深A股专业分析师，可结合全网最新公告、行业政策、题材热点、盘面资金流向、龙虎榜数据、舆情热度、业绩预告等公开信息，做客观、有数据支撑的分析，观点需充分详实，拒绝空泛表述。
    请对下方多只个股逐一拆解：涨停逻辑、利空风险、未来想象空间精细评级，按未来想象空间从大到小统一排序。。

    待分析个股信息：
    {stock_data}

    严格遵守规则，搜索网络信息要全面、禁止开场白、禁止搜索过程、禁止多余废话、禁止主观吹票、禁止空泛表述：
    1.  首先对所有股票进行分类统计，个股可出现在多个分类中，分类方法包括但不限于：行业赛道、核心题材、概念热点、重组摘帽、超跌反弹、涨停逻辑相似度80%以上（需简要说明相似点）；分类需明确，每个分类标注核心共性，不模糊、不笼统。
    2.  每只股票单独独立分析，不交叉混淆，每部分分析均需结合具体信息，观点有支撑、有依据，不凭空判断。
    3.  未来想象空间固定分为5档：极高 / 很高 / 中等 / 偏低 / 极低，必须严格从这五档里选一个；评级理由需具体，结合题材级别、业绩弹性、资金强度、政策持续性，拒绝“题材好”“有潜力”等空泛表述。
    4.  每只个股固定三块结构输出，整体按未来想象空间从高到低排序：
    【未来想象空间评级】
    给出对应档位，并列3-5条核心理由；每条理由需结合具体信息（如：政策层面→某行业最新扶持政策、资金层面→龙虎榜机构净买入、题材层面→属于当前主线且有持续催化），明确说明“为什么是这个档位”。

    【涨停逻辑分析】
    梳理当日涨停核心驱动，列3-5条关键逻辑；每条逻辑需落地到具体细节（如：题材催化→特朗普访华稀土管制放松，直接利好公司稀土出口业务；资金流向→主力资金净流入XX亿，封单量XX万手；板块共振→所属稀土板块当日涨幅X%，板块内XX只个股涨停），不笼统表述“受题材带动”。

    【利空风险分析】
    梳理潜在利空，列3-5条核心风险；每条风险需具体、可落地（如：减持风险→公司股东计划减持XX万股，占总股本X%，减持窗口临近；业绩隐患→公司一季度净利润同比下滑X%，核心业务营收不及预期；题材风险→当前题材属于短期炒作，无实质业绩支撑，退潮风险较高），拒绝“有减持风险”“估值偏高”等空泛表述。

    5.  全部个股分析完毕后，单独起一行：按未来想象空间从高到低排序，只罗列股票名称+对应评级；
    6.  分析要全面,不渲染情绪、只做客观逻辑拆解，每条要点直击核心，既有观点，又有具体支撑依据。
    """
    client = get_doubao_client()
    tools = [{
    "type": "web_search",
    }]
    input = [{"role": "user", "content": prompt}]
    response = client.responses_doubao(input=input, tools=tools, **kwargs)
    
    # 打印 web_search 收费统计
    print_web_search_cost(response)
    print(response.usage)
    
    # 检查是否流式输出
    if kwargs.get('stream', False):
        return process_stream_responses(response)
    
    # 非流式输出：解析响应
    return process_response_output(response)
