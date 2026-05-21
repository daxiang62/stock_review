import os
from volcenginesdkarkruntime import Ark

# To obtain the api key from your environment variables, see: https://www.volcengine.com/docs/82379/1820161


client = Ark(
    base_url='https://ark.cn-beijing.volces.com/api/v3',
    api_key="ark-1a06c418-7b4d-4ed6-88d1-9eb047a25733-7e3b4",
)

tools = [{
    "type": "web_search",
    "max_keyword": 2,  
}]

# Create a conversation request
response = client.responses.create(
    model="doubao-seed-2-0-pro-260215",
    input=[{"role": "user", "content": "今天有什么热点新闻？"}],
    tools=tools,
)

print(response)