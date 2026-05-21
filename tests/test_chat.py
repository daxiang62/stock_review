"""测试 chat_doubao 和 responses_doubao 的流式输出和非流式输出"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from utils import get_doubao_client, process_stream_chat, process_stream_responses

def test_non_stream():
    """测试 chat_doubao 非流式输出"""
    print("=" * 50)
    print("测试 chat_doubao 非流式输出")
    print("=" * 50)
    
    client = get_doubao_client()
    
    prompt = "简单介绍一下人工智能"
    
    response = client.chat_doubao(
        messages=[{"role": "user", "content": prompt}],
        stream=False
    )
    
    result = ""
    if hasattr(response, 'choices') and len(response.choices) > 0:
        choice = response.choices[0]
        if hasattr(choice, 'message'):
            result = choice.message.content
    
    print(f"问题: {prompt}")
    print(f"回答: {result}")
    print()

def test_stream_chat():
    """测试 chat_doubao 流式输出"""
    print("=" * 50)
    print("测试 chat_doubao 流式输出")
    print("=" * 50)
    
    client = get_doubao_client()
    
    prompt = "简单介绍一下机器学习"
    
    print(f"问题: {prompt}")
    print("回答: ", end='', flush=True)
    
    # 直接调用 chat_doubao，然后使用工具函数处理流式响应
    stream_response = client.chat_doubao(
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    
    for chunk in process_stream_chat(stream_response):
        print(chunk, end='', flush=True)
    
    print()
    print()

def test_responses_doubao():
    """测试 responses_doubao（支持 web_search）"""
    print("=" * 50)
    print("测试 responses_doubao（带 web_search）")
    print("=" * 50)
    
    client = get_doubao_client()
    
    tools = [{
        "type": "web_search",
    }]
    
    prompt = "蔚蓝锂芯今天为什么涨停"
    
    response = client.responses_doubao(
        input=[{"role": "user", "content": prompt}],
        tools=tools,
    )
    
    print(f"问题: {prompt}")
    print("回答:", end=' ')
    for item in response.output:
        if hasattr(item, 'content'):
            for content in item.content:
                if hasattr(content, 'text'):
                    print(content.text, end='')
    print()
    print()

def test_stream_responses():
    """测试 responses_doubao 流式输出"""
    print("=" * 50)
    print("测试 responses_doubao 流式输出")
    print("=" * 50)
    
    client = get_doubao_client()
    
    prompt = "简单介绍一下云计算"
    
    print(f"问题: {prompt}")
    print("回答: ", end='', flush=True)
    
    # 直接调用 responses_doubao，然后使用工具函数处理流式响应
    stream_response = client.responses_doubao(
        model="doubao-seed-2-0-pro-260215",
        input=[{"role": "user", "content": prompt}],
        stream=True
    )
    
    for chunk in process_stream_responses(stream_response):
        print(chunk, end='', flush=True)
    
    print()
    print()

def main():
    # 测试 chat_doubao 非流式输出
    # test_non_stream()
    
    # 测试 chat_doubao 流式输出
    # test_stream_chat()
    
    # 测试 responses_doubao（带 web_search）
    test_responses_doubao()
    
    # 测试 responses_doubao 流式输出
    test_stream_responses()

if __name__ == "__main__":
    main()
