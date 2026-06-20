# 🛒 market — AI 开发装备商场

> 不搜索，不翻文档。走进来，挑想要的，拿走。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-12-blue)]()
[![Agents](https://img.shields.io/badge/agents-15-green)]()
[![Plugins](https://img.shields.io/badge/plugins-5-orange)]()

---

## 🔥 两种安装方式

### 方式一：Claude Code 插件（推荐）

```bash
# 注册商场
claude plugin marketplace add Sweetteabittersugar/market

# 挑一个装上
claude plugin install workflow-core@Sweetteabittersugar/market    # 工作流
claude plugin install research-kit@Sweetteabittersugar/market     # 调研
claude plugin install story-dev@Sweetteabittersugar/market        # 故事驱动
claude plugin install agent-personas@Sweetteabittersugar/market   # Agent 角色
claude plugin install full-arsenal@Sweetteabittersugar/market     # 全都要
```

### 方式二：一键安装（传统）

```bash
git clone https://github.com/Sweetteabittersugar/market.git
cd market && bash scripts/install.sh
python -m agency.check   # 验证
```

安装后对话里直接用：`/spec` `/research` `/gate-check` `/retro` `/create-story` `/cost` `/help`

---

## 📦 货架

### 🔧 workflow-core — 工作流核心
**结构化 AI 开发流程：从想法到复盘。**

| 包含 | 说明 |
|------|------|
| `/spec` | 需求→Spec 一条龙 |
| `/gate-check` | 阶段门控检查 + 🔴硬门控 |
| `/retro` | 复盘教训提取→写入 memory |
| 工作流文档 | 12 阶段 + 3 种协作模式 + DoR/DoD |
| 门控清单 | 4 维度通用 + 每阶段特定 |

---

### 📚 research-kit — 调研工具
**不凭训练数据做决策。**

| 包含 | 说明 |
|------|------|
| `/research` | 4 步流程 × 4 级来源 × 双门验证 |
| 调研模板 | 发现→分析→建议→来源表→分歧 |

---

### 📖 story-dev — 故事驱动开发
**借鉴 BMAD：Agent 打开 Story 文件就能干活。**

| 包含 | 说明 |
|------|------|
| `/create-story` | Spec→Epic→Story 文件生成 |
| Story 模板 | Context 段 + 可观测性段 + Dev/QA Record |
| 项目惯例 | 环境·风格·陷阱·模式库 |

---

### 🤖 agent-personas — Agent 角色包
**5 个带项目约束的自定义 Agent。**

| Agent | 专长 |
|-------|------|
| `@pm` | 需求挑战·故事分解·阶段判断 |
| `@architect` | Spec·技术选型（知项目约束） |
| `@qa` | 门控检查·功能验证·安全扫描 |
| `@reviewer` | 复盘·教训提取·记忆写入 |
| `@code-reviewer` | 四维度代码审查 |

---

### 🛒 full-arsenal — 全家桶
**全都要——12 Skill + 15 Agent + 3 模板 + 工作流 + 惯例 + 货架。**

---

## 📊 对比

| | workflow-core | research-kit | story-dev | agent-personas | full-arsenal |
|---|---|---|---|---|---|
| Skill | 3 | 1 | 1 | — | 12 |
| Agent | — | — | — | 5 | 15 |
| 模板 | 1 | 1 | 1 | — | 3 |
| 工作流 | ✅ | — | — | — | ✅ |
| 惯例 | — | — | ✅ | — | ✅ |
| 费用追踪 | — | — | — | — | ✅ |

---

## 📁 目录

```
market/
├── skills/         12 个 Skill（源码）
├── agents/         15 个 Agent 定义
├── templates/      3 个模板
├── docs/           工作流·惯例·装备货架
├── plugins/        5 个可安装套装
├── scripts/        安装脚本
├── src/            实现（Python）
└── .claude-plugin/ 商场注册表
```

---

## ❓ 常见问题

| 问题 | 解决 |
|------|------|
| 和 BMAD 什么关系？ | 工作流借鉴 BMAD 的故事驱动 + 角色分工理念，但完全独立实现 |
| 需要什么环境？ | Claude Code + Python ≥ 3.8 + DeepSeek API Key |
| 能单独用某个 Skill 吗？ | 能——直接复制 `skills/` 下对应目录到 `.claude/skills/` |
| 插件和 skills/ 什么关系？ | `plugins/` 是打包好的套装，`skills/` 是散件——挑着用 |

---

## 📄 License

MIT © 2026 Sweetteabittersugar
