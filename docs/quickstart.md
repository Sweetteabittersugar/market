# Agency v2 — 快速上手

## 安装

```bash
git clone <repo> agency-v2 && cd agency-v2
bash scripts/install.sh
```

一条命令完成：pip 安装 + Hook 注册 + 数据库初始化。

## 第一条命令

```
/cost       → 查看费用（会话结束后有数据）
/history    → 查看 Agent 执行记录
/help       → 查看所有功能
```

## 工作原理

每次 Claude Code 会话结束后，Stop hook 自动解析转录，记录费用和 Agent 执行数据到 `~/.agency/agency.db`。

你用 `/cost` `/history` 随时查，默认不打扰。

## 模型切换

Agency 使用双模型：DeepSeek V4 Pro 主力 + MiMo V2.5 Pro 前端/审查。

切模型提醒：`source scripts/workflow.sh <stage>`

实际切换用 CC Switch。
