"""Function Calling 最小演示：让 LLM 学会用计算器"""
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 1. 定义工具（告诉 LLM 有哪些工具可用）
#    注意：这里只是"描述"，不是真的函数实现
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式，如 15*0.3、2**10",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

# 2. 工具的真实实现（你的代码真正执行的逻辑）
def calculator(expression: str) -> str:
    """执行数学表达式计算（安全版：只用 eval 白名单）"""
    # 只允许数字和运算符，防止恶意代码
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expression):
        return "错误：表达式包含非法字符"
    try:
        result = eval(expression)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {e}"


def main():
    client = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
        base_url="https://api.deepseek.com"
    )

    # 3. 第一轮：发用户问题 + 工具列表
    messages = [
        {"role": "user", "content": "你的名字叫什么"}
    ]

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=TOOLS,          # ← 关键：把工具列表传给 LLM
        tool_choice="auto",   # ← 让 LLM 自己决定要不要用工具
    )

    msg = resp.choices[0].message

    # 4. 检查 LLM 是否想调用工具
    if msg.tool_calls:
        print("=== LLM 请求调用工具 ===")
        for tc in msg.tool_calls:
            print(f"工具名: {tc.function.name}")
            print(f"参数: {tc.function.arguments}")

            # 5. 你的代码执行工具
            if tc.function.name == "calculator":
                args = json.loads(tc.function.arguments)
                result = calculator(args["expression"])
                print(f"执行结果: {result}")

                # 6. 把工具结果喂回给 LLM
                messages.append(msg)  # 加上 LLM 的"调用请求"
                messages.append({
                    "role": "tool",   # 工具结果的角色是 tool
                    "tool_call_id": tc.id,
                    "content": result
                })

        # 7. LLM 基于工具结果生成最终回答
        resp2 = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=TOOLS,
        )
        print("\n=== 最终回答 ===")
        print(resp2.choices[0].message.content)
    else:
        # LLM 没调用工具，直接回答
        print("=== 直接回答 ===")
        print(msg.content)


if __name__ == "__main__":
    main()