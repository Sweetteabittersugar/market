# Workflow — 工作流

AI 全栈开发 9 阶段工作流。

## 阶段
```
-1  灵感捕捉     → 问题表述
 0  需求分析     → 四维度审查
 1  Spec 定稿    → 宪章 + 功能 + 架构 + 验收
 2  技术选型     → 三问分析 + 切换成本
 3  数据/API设计 → 数据建模 + 接口
 4  后端实现     → 核心逻辑
 5  前端实现     → 界面/内容
 6  E2E 联调     → 端到端测试
 7  视觉打磨     → 交互/动画/响应式
 8  部署上线     → 环境/发布
```

## 模型分工
- 规划层（-1~3, review, rescue）→ DeepSeek V4 Pro
- 前端/视觉（5, 7, cross-review）→ MiMo V2.5 Pro

提醒切换：运行 `source scripts/workflow.sh <stage>`
