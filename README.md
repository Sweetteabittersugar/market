# Agency v2

> Claude Code 个性化增强包——内置工作流、Agent 库、Skill 库、费用追踪。
> 纯对话，零 GUI。安装一条命令，所有功能通过对话触发。

## 安装

```bash
git clone <repo> agency-v2 && cd agency-v2 && bash scripts/install.sh
```

## 快速开始

```
/cost       → 今日/本周/本月费用
/history    → Agent 执行记录
/help       → 查看所有功能
```

## 包含什么

| 层 | 内容 |
|----|------|
| Agent 库 | 9 个 Agent（architect/coder/reviewer/debugger/explorer/test-writer/devops/doc-writer/security-reviewer） |
| Skill 库 | 7 个 Skill（review/debug/cost/history/help/workflow/agent） |
| 工作流引擎 | 9 阶段全栈开发（灵感 → 部署），双模型分工 |
| 费用追踪 | Stop hook 自动记录，`/cost` 查询 |
| 执行记录 | Agent 干了什么、花了多少，`/history` 查询 |
| 说明书 | `/help` 查，功能没文档 = 功能不存在 |

## 架构

```
Agency v2 = Claude Code + 三层增强

指令层（静态）: CLAUDE.md + agents/ + skills/ + docs/
脚本层（按需）: workflow.sh + cost.py + history.py
服务层（静默）: hooks/stop.py → ~/.agency/agency.db
```

## 依赖

- Claude Code（运行时）
- CC Switch（模型切换）
- Python ≥ 3.8（费用追踪）
- DeepSeek V4 Pro + MiMo V2.5 Pro API Key

## 许可

MIT
