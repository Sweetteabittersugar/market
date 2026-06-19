# Agent 列表

| Agent | 用途 | 调用 |
|-------|------|------|
| architect | 系统设计、技术选型（只出方案） | `@architect <任务>` |
| coder | 写代码、修 bug | `@coder <任务>` |
| reviewer | 四维度代码审查 | `@reviewer <任务>` |
| debugger | 六步结构化调试 | `@debugger <任务>` |
| explorer | 代码库搜索，只读 | `@explorer <任务>` |
| test-writer | 生成单元/集成测试 | `@test-writer <任务>` |
| devops | CI/CD、Docker、部署 | `@devops <任务>` |
| doc-writer | 文档编写更新 | `@doc-writer <任务>` |
| security-reviewer | 安全审计 | `@security-reviewer <任务>` |

## 自动路由

不需要手动指定 Agent。描述你的任务，系统自动匹配。

详见 `AGENTS.md`。
