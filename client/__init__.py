"""股票数据源客户端包
统一封装各类股票数据源，提供一致的调用接口
支持数据源:
- Akshare: 开源免费，涨跌停、龙虎榜等特色数据全
- Baostock: 开源免费，财务数据稳定准确
- MooTDX: 通达信行情接口，速度极快，支持实时/分钟K线
- Tushare: 数据最全，部分接口需要积分

各数据源依赖库按需安装：只有在实际使用某个数据源时才会导入其依赖，
因此缺少某个可选库不会影响其他数据源的使用。
"""
import importlib
from .base_client import BaseStockClient

# 数据源类型 -> (模块路径, 类名)
_CLIENT_REGISTRY = {
    "akshare": (".akshare_client", "AkshareClient"),
    "baostock": (".baostock_client", "BaostockClient"),
    "mootdx": (".mootdx_client", "MootdxClient"),
    # "tushare": (".tushare_client", "TushareClient"),  # 后续扩展直接加
}
# 类名 -> 模块路径，用于按属性名懒加载
_CLASS_TO_MODULE = {cls: mod for mod, cls in _CLIENT_REGISTRY.values()}


def get_client(client_type: str = "akshare", **kwargs) -> BaseStockClient:
    """获取数据源客户端实例（按需导入对应依赖）
    :param client_type: 数据源类型，支持 akshare/baostock/mootdx
    :param kwargs: 客户端初始化参数
    :return: 对应的数据源客户端实例
    """
    if client_type not in _CLIENT_REGISTRY:
        raise ValueError(
            f"不支持的数据源类型: {client_type}, 支持的类型: {list(_CLIENT_REGISTRY.keys())}"
        )
    module_path, class_name = _CLIENT_REGISTRY[client_type]
    module = importlib.import_module(module_path, __name__)
    return getattr(module, class_name)(**kwargs)


def __getattr__(name: str):
    """PEP 562 懒加载：访问 AkshareClient/BaostockClient/MootdxClient 时才导入其模块"""
    if name in _CLASS_TO_MODULE:
        module = importlib.import_module(_CLASS_TO_MODULE[name], __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "BaseStockClient",
    "AkshareClient",
    "BaostockClient",
    "MootdxClient",
    "get_client",
]
