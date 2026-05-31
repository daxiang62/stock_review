"""日志工具模块"""
import logging
import sys
import os
from datetime import datetime

def setup_logger(name: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    配置并获取日志记录器
    
    :param name: 日志记录器名称，默认为 None（根记录器）
    :param level: 日志级别，默认为 logging.INFO
    :return: 配置好的日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(
        "%(asctime)s【%(levelname)s】%(filename)s:%(lineno)d:%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # 创建日志目录
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建文件处理器 - 按日期命名
    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # 添加处理器到记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # 设置 propagate 为 False 防止日志重复输出
    logger.propagate = False
    
    return logger

# 创建默认日志记录器
logger = setup_logger(__name__)

def get_logger(name: str = None) -> logging.Logger:
    """
    获取日志记录器，如果不存在则创建新的

    :param name: 日志记录器名称
    :return: 日志记录器
    """
    if name is None:
        return logger
    return setup_logger(name)


if __name__ == "__main__":
    print("[日志工具测试]")
    
    test_logger = get_logger("test_logger")
    
    test_logger.debug("这是 DEBUG 级别日志")
    test_logger.info("这是 INFO 级别日志")
    test_logger.warning("这是 WARNING 级别日志")
    test_logger.error("这是 ERROR 级别日志")
    
    default_logger = get_logger()
    default_logger.info("使用默认日志记录器")
    
    print("[日志工具测试完成]")