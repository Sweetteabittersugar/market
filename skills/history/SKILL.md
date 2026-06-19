---
name: history
description: "查询 Agent 执行记录——谁做了什么任务、改了哪些文件、花了多少。触发词：/history、执行记录、agent记录"
---

# History — Agent 执行记录

查询 Agent 执行记录。

## 触发
- `/history` — 最近 10 条
- `/history --last 20` — 最近 20 条
- `/history --agent coder` — 按 Agent 筛选
- `/history --today` — 只看今日

## 实现
执行 `python -m agency.history` 并展示结果。
