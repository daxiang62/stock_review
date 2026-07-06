"""命令行入口: 用 MyTT/通达信 风格条件语言选股

用法:
    python -m screener "CROSS(MA(C,5), MA(C,10))"
    python -m screener "(C > MA(C,20)) AND (VOL > MA(VOL,5)*2)" --limit 100
"""
import argparse

from . import screen_stocks


def main():
    parser = argparse.ArgumentParser(
        prog="python -m screener",
        description="用 MyTT/通达信 风格的选股条件语言筛选 A 股",
    )
    parser.add_argument("formula", help="选股条件字符串，如 \"CROSS(MA(C,5), MA(C,10))\"")
    parser.add_argument("--limit", type=int, default=None,
                        help="只扫描前 N 只（调试用），默认全部")
    parser.add_argument("--kline-days", type=int, default=120,
                        help="每只股票取最近多少根日线计算指标，默认 120")
    args = parser.parse_args()

    result = screen_stocks(args.formula, limit=args.limit, kline_days=args.kline_days)
    if result.empty:
        print("无符合条件的股票")
    else:
        print(result.to_string(index=False))
        print(f"\n共命中 {len(result)} 只")


if __name__ == "__main__":
    main()
