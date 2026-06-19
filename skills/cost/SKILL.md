---
name: cost
description: "查询 Claude Code 费用——今日/本周/本月/按模型。触发词：/cost、费用、花了多少"
---

# Cost — 费用查询

查询 Agency 费用：今日/本周/本月/按模型。

## 触发
- `/cost` — 默认汇总
- `/cost --days 7` — 最近 7 天
- `/cost --month` — 本月明细

## 实现
执行 `python -m agency.cost` 并展示结果。
