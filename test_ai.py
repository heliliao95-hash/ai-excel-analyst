import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("DASHSCOPE_API_KEY")
base_url = os.getenv("DASHSCOPE_BASE_URL")
model = os.getenv("DASHSCOPE_MODEL", "qwen-plus")

if not api_key:
	raise ValueError("没有读取到 DASHSCOPE_API_KEY，请检查 .env 文件")

client = OpenAI(
	api_key=api_key,
	base_url=base_url,
)

response = client.chat.completions.create(
	model=model,
	messages=[
		{"role": "system", "content": "你是一个专业的数据分析助手。"},
		{"role": "user", "content": "请用一句话介绍你自己。"},
	],
)

print("AI 调用成功！")
print(response.choices[0].message.content)
