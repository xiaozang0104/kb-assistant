# Agent Architecture - kb-assistant

> Mermaid 图，GitHub 自动渲染。可在 https://mermaid.live 预览。

```mermaid
graph TD
    U[用户问题] --> A[LLM 思考<br/>DeepSeek deepseek-chat]
    A -->|答案在知识文档| S[search_kb<br/>检索 Chroma 知识库]
    A -->|答案在数据库| D[query_documents_db<br/>查 MySQL 只读 SELECT]
    A -->|需要数学计算| C[calculator<br/>白名单表达式计算]
    A -->|都不需要| F[直接生成回答]
    S --> O[观察工具结果]
    D --> O
    C --> O
    O -->|信息不足 继续思考| A
    O -->|信息足够| F
    F --> R[最终回答 + 工具调用记录]
```

## 流程说明

- Agent 用 Function Calling + ReAct 循环（思考→行动→观察），最多 10 轮
- LLM 根据工具 description 决定调用哪个工具；工具结果以 role=tool 加回对话
- SQL 工具只允许 SELECT（防注入/防破坏）；计算器有字符白名单
- 轮数上限作为安全阀，防止死循环无限消耗 API
```

