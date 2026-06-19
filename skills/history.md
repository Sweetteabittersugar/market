# History — Agent 执行记录

查询 Agent 执行记录。

## 触发
- `/history` — 最近 10 条
- `/history --last 20` — 最近 20 条
- `/history --agent coder` — 按 Agent 筛选
- `/history --today` — 只看今日

## 实现
执行 `python -m agency.history` 并展示结果。
