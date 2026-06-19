# 工作流详解

AI 全栈开发 9 阶段，从灵感到部署。

## 阶段

| # | 阶段 | 做什么 | 模型 |
|---|------|--------|------|
| -1 | 灵感 | 问题表述 | DeepSeek |
| 0 | 需求 | 四维度审查 + 追问 | DeepSeek |
| 1 | Spec | 宪章 + 功能 + 架构 + 验收 | DeepSeek |
| 2 | 技术选型 | 三问分析 + 切换成本 | DeepSeek |
| 3 | API 设计 | 数据建模 + 接口 | DeepSeek |
| 4 | 后端 | 核心逻辑实现 | DeepSeek |
| 5 | 前端 | 界面/内容实现 | MiMo |
| 6 | E2E 联调 | 端到端测试 | DeepSeek |
| 7 | 视觉 | 交互/动画/响应式 | MiMo |
| 8 | 部署 | 环境/发布 | DeepSeek |

## 模型分工

- **DeepSeek V4 Pro**：规划、后端、测试、部署
- **MiMo V2.5 Pro**：前端生成、视觉打磨、交叉审查

## 阶段间协议

每个阶段结束 → Commit → 更新 `.context/handoff.md` → `/compact` → 新会话继续。
