# 项目惯例

> 所有 Story 的 Context 段引用此文件。新人（新 Agent）打开即懂，不需要老人口头传授。

## 环境

- **OS**: Windows 11 Home China
- **Shell**: Git Bash（路径 `/` 不 `\`），没有 `/tmp`
- **Python**: 3.11 conda 管理，跑前 `source $HOME/anaconda3/etc/profile.d/conda.sh && conda activate`
- **AI 主力**: DeepSeek V4 Pro（编程/推理），MiMo V2.5 Pro（前端/视觉）

## 代码风格

### Python
- `snake_case` 变量/函数，`PascalCase` 类，`UPPER_SNAKE` 常量
- 类型注解必写
- Pydantic 校验所有外部输入
- 显式处理每个错误——不静默吞掉
- 符合现有代码风格，不一致的改自己的

### 文件
- 200-400 行理想，800 行硬上限
- 函数 ≤50 行，参数 ≤5 个，嵌套 ≤4 层
- 按功能组织，不是按文件类型

### Git
- Commit: `<type>: <描述>`（feat/fix/refactor/docs/test/chore/perf）
- Claude 提交加 `[claude]` 前缀
- 不提交 `.env`、证书、二进制

## 常见陷阱

- Windows 路径用 `/` 不 `\`
- 不要硬编码密钥/密码/Token——用环境变量
- 不要 `print()` 调试——用 log
- 不原地修改对象——新建返回
- windows 下文件编码先试 UTF-8 → UTF-16 → GBK

## 模式库

### API 设计
- Contract-First：先定契约再写代码
- 统一错误格式：`{"error": "描述", "code": "ERR_XXX"}`
- 迁移用 Expand-Contract——不直接改表

### 日志
- 关键路径必须有 log：请求入口、外部调用、错误边界、状态变更
- 错误必须有 stack trace
- 不记敏感信息（密码/token/PII）

### 安全
- grep 提交前检查硬编码密钥
- 输入校验在边界处做（类型+范围+长度）
- 错误消息不泄露内部路径/堆栈

### 测试
- TDD 优先：红灯 → 绿灯 → 重构
- curl 能调通才算后端完成
- 三态覆盖：loading / empty / error

## 工作流速查

| 场景 | 走什么 |
|------|--------|
| 新项目 | `source scripts/workflow.sh <stage>` → 从 -1 开始 |
| 改 Bug | quick 模式：读 Story → 改 → 审 → 验 |
| 技术决策 | `/research` 调研再决定 |
| 阶段结束 | `/gate-check` 门控检查 |
| 复盘 | `/retro` |
