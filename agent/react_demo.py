"""ReAct 循环演示：Agent 循环调用工具直到给出最终回答"""
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ---- 工具声明 ----
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前日期时间",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

# ---- 工具实现 ----
def calculator(expression: str) -> str:
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expression):
        return "错误：非法字符"
    try:
        return f"计算结果: {eval(expression)}"
    except Exception as e:
        return f"计算错误: {e}"

def get_current_time() -> str:
    from datetime import datetime
    return f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# 工具注册表：名字 → 函数（分发的关键）
TOOL_FUNCTIONS = {
    "calculator": calculator,
    "get_current_time": get_current_time,
}

def main():
    client = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
        base_url="https://api.deepseek.com"
    )

    question = input("请输入问题（试试：今天是几号？100天后的日期？）：")
    messages = [{"role": "user", "content": question}]

    # ReAct 循环：最多循环 5 次，防止死循环
    for round_num in range(5):
        print(f"\n--- 第 {round_num+1} 轮 ---")
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=TOOLS,
        )
        msg = resp.choices[0].message

        # 情况1：LLM 想调用工具 → 执行，把结果加回对话，继续循环
        if msg.tool_calls:
            print(f"Agent 思考: 需要调用 {len(msg.tool_calls)} 个工具")
            messages.append(msg)
            for tc in msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                print(f"  → 调用 {name}({args})")
                # 从注册表找到函数并执行
                result = TOOL_FUNCTIONS[name](**args)
                print(f"  → 观察结果: {result}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })
            continue  # 继续循环，让 LLM 看结果后再决定

        # 情况2：LLM 直接给出最终回答 → 结束循环
        else:
            print("\n=== 最终回答 ===")
            print(msg.content)
            break
    else:
        print("\n达到最大循环次数，强制结束")

if __name__ == "__main__":
    main()