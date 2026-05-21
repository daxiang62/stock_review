"""通用数据处理工具"""
import pandas as pd

def format_date(date_str):
    """
    格式化日期字符串
    
    :param date_str: 日期字符串，格式 YYYYMMDD
    :return: 格式化后的日期字符串，格式 YYYY-MM-DD
    """
    if len(date_str) == 8:
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    return date_str

def deduplicate_by_column(df, column_name):
    """
    根据指定列去重
    
    :param df: DataFrame
    :param column_name: 列名
    :return: 去重后的DataFrame
    """
    return df.drop_duplicates(subset=column_name, keep='first')

def sort_by_multiple_columns(df, columns, ascending=True):
    """
    根据多列排序
    
    :param df: DataFrame
    :param columns: 列名列表
    :param ascending: 是否升序
    :return: 排序后的DataFrame
    """
    return df.sort_values(by=columns, ascending=ascending)

def save_to_excel(df, file_path, sheet_name='Sheet1'):
    """
    保存DataFrame到Excel文件
    
    :param df: DataFrame
    :param file_path: 文件路径
    :param sheet_name: 工作表名称
    """
    try:
        df.to_excel(file_path, sheet_name=sheet_name, index=False)
        print(f"数据已保存到: {file_path}")
    except Exception as e:
        print(f"保存文件失败: {e}")

def load_from_excel(file_path, sheet_name='Sheet1'):
    """
    从Excel文件加载DataFrame
    
    :param file_path: 文件路径
    :param sheet_name: 工作表名称
    :return: DataFrame
    """
    try:
        return pd.read_excel(file_path, sheet_name=sheet_name)
    except Exception as e:
        print(f"加载文件失败: {e}")
        return pd.DataFrame()
