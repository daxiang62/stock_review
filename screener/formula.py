"""MyTT 选股条件语言 解析与求值

把字符串形式的选股条件（MyTT / 通达信 风格）编译成可执行的选股策略。

支持的内容:
- 行情变量(不区分大小写): CLOSE/C, OPEN/O, HIGH/H, LOW/L, VOL/VOLUME/V, AMOUNT/AMO
- 全部 MyTT 函数: MA, EMA, SMA, REF, MACD, KDJ, RSI, BOLL, CROSS, HHV, LLV,
  COUNT, EVERY, EXIST, IF, SUM ... （见 MyTT 库）
- 逻辑运算: AND / OR / NOT （等价于 & | ~），也可直接用 & | ~
- 比较运算: > < >= <= == !=，单个 = 等价于 ==

注意(numpy 运算符优先级):
  & | 的优先级高于比较运算符，组合多个条件时请给每个比较加括号，例如:
      (MA(C,5) > MA(C,10)) AND (C > MA(C,20))

示例:
    "CROSS(MA(C,5), MA(C,10))"                      # 5日线上穿10日线
    "(C > MA(C,20)) AND (VOL > MA(VOL,5)*2)"        # 站上20日线且放量2倍
    "COUNT(C > REF(C,1), 5) >= 4"                   # 近5日至少4天收阳
"""
import re
from typing import Callable

import numpy as np
import pandas as pd
import MyTT

# 缓存 MyTT 全部可调用函数，作为公式可用的函数命名空间
_MYTT_FUNCS = {
    name: getattr(MyTT, name)
    for name in dir(MyTT)
    if not name.startswith("_")
    and callable(getattr(MyTT, name))
    and name not in ("np", "pd")
}

# 行情变量别名 -> K线列名
_VAR_ALIASES = {
    "CLOSE": "close", "C": "close",
    "OPEN": "open", "O": "open",
    "HIGH": "high", "H": "high",
    "LOW": "low", "L": "low",
    "VOL": "volume", "VOLUME": "volume", "V": "volume",
    "AMOUNT": "amount", "AMO": "amount",
}


def _translate(formula: str) -> str:
    """把通达信/MyTT 风格运算符翻译成 Python 可执行表达式"""
    expr = formula
    # 逻辑运算符（整词、忽略大小写）
    expr = re.sub(r"\bAND\b", "&", expr, flags=re.IGNORECASE)
    expr = re.sub(r"\bOR\b", "|", expr, flags=re.IGNORECASE)
    expr = re.sub(r"\bNOT\b", "~", expr, flags=re.IGNORECASE)
    # 单个 = 转 ==（保留 >= <= == != 不变）
    expr = re.sub(r"(?<![<>=!])=(?!=)", "==", expr)
    return expr


def _build_env(df: pd.DataFrame) -> dict:
    """构建公式求值的命名空间：行情变量 + MyTT 函数"""
    env = dict(_MYTT_FUNCS)
    for alias, col in _VAR_ALIASES.items():
        if col in df.columns:
            env[alias] = df[col].values
    return env


def _last_bool(result) -> bool:
    """取求值结果最后一根K线的布尔判定，NaN 视为不满足"""
    arr = np.asarray(result)
    last = arr.reshape(-1)[-1] if arr.ndim else arr.item() if arr.shape == () else arr
    if isinstance(last, (float, np.floating)) and np.isnan(last):
        return False
    return bool(last)


def compile_formula(formula: str) -> Callable[[pd.DataFrame], bool]:
    """把选股条件字符串编译成策略函数: (带指标的K线df) -> 最新一根是否命中
    :raises SyntaxError: 公式语法错误
    """
    if not formula or not formula.strip():
        raise ValueError("选股条件不能为空")

    expr = _translate(formula)
    try:
        code = compile(expr, "<formula>", "eval")
    except SyntaxError as e:
        raise SyntaxError(f"选股条件语法错误: {formula} -> {e}") from e

    def strategy(df: pd.DataFrame) -> bool:
        env = _build_env(df)
        result = eval(code, {"__builtins__": {}}, env)
        return _last_bool(result)

    strategy.__name__ = f"formula[{formula}]"
    return strategy
