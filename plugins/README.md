# 🛒 AI 开发装备商场

> 不搜索，不翻文档。走进来，挑想要的，拿走。

---

## 🔥 快速安装

```bash
# 1. 注册商场
claude plugin marketplace add Sweetteabittersugar/sweettea-ai-marketplace

# 2. 挑一个装上
claude plugin install workflow-core@Sweetteabittersugar    # 只要工作流
claude plugin install research-kit@Sweetteabittersugar     # 只要调研
claude plugin install story-dev@Sweetteabittersugar        # 只要故事驱动
claude plugin install agent-personas@Sweetteabittersugar   # 只要Agent角色
claude plugin install full-arsenal@Sweetteabittersugar     # 全都要
```

---

## 📦 货架

### 🔧 工作流核心 (`workflow-core`)
**一套结构化 AI 开发流程——从想法到复盘。**

| 包含 | 说明 |
|------|------|
| `/spec` | 需求→Spec 一条龙 |
| `/gate-check` | 阶段门控检查（PASS/CONCERNS/FAIL + 🔴硬门控） |
| `/retro` | 复盘教训提取→写入 memory |
| 12 阶段工作流 | 3 种协作模式（层级式/对话式/流水线式）+ DoR/DoD 双门控 |
| 门控清单 | 4 维度通用 + 每阶段特定 + 硬门控 |

**适合**: 想让 AI 开发有章法的人——不再"凭感觉写代码"。

---

### 📚 调研工具 (`research-kit`)
**标准化调研——不凭训练数据做决策。**

| 包含 | 说明 |
|------|------|
| `/research` | 4 步流程（确认日期→多角度搜索→交叉验证→结构化输出） |
| 4 级来源可信度 | T1 官方/学术 → T4 匿名 |
| 双门验证 | 预执行（WebSearch 不可用就中断）+ 后验证（每条结论 ≥2 来源） |
| 调研报告模板 | 发现→分析→建议→来源表→分歧 |

**适合**: 技术选型前、定价查询、最佳实践调研——任何"需要上网查"的决策。

---

### 📖 故事驱动开发 (`story-dev`)
**借鉴 BMAD：Agent 打开 Story 文件就能干活，不翻架构文档。**

| 包含 | 说明 |
|------|------|
| `/create-story` | Spec→Epic→Story 文件 |
| Story 模板 | Context 段（完整上下文）+ 可观测性段（日志/指标/链路）+ Dev/QA Record |
| 项目惯例 | 环境·风格·陷阱·模式库（新人/新 Agent 必读） |

**适合**: 阶段间上下文丢失的痛点——Story 文件一次性解决问题。

---

### 🤖 Agent 角色包 (`agent-personas`)
**5 个带项目约束的自定义 Agent——开箱即用。**

| Agent | 专长 |
|-------|------|
| `@pm` | 产品经理：需求挑战·故事分解·阶段判断 |
| `@architect` | 架构师：Spec·技术选型（知项目约束） |
| `@qa` | 质量保证：门控检查·功能验证·安全扫描 |
| `@reviewer` | 复盘审查：教训提取·模式识别·记忆写入 |
| `@code-reviewer` | 代码审查：四维度（正确性·简洁性·可维护性·安全性） |

**适合**: 想让 Agent 有角色分工的人——不同的活派不同的 Agent。

---

### 🛒 全家桶 (`full-arsenal`)
**全部装备——完整复制我们的 AI 开发工作方式。**

```
7 Skill + 10 Agent + 3 模板 + 12阶段工作流 + 门控清单 + 项目惯例 + 装备货架
```

**适合**: "我不想挑了——全给我装上。"

---

## 📊 对比

| | workflow-core | research-kit | story-dev | agent-personas | full-arsenal |
|---|---|---|---|---|---|
| Skill | 3 | 1 | 1 | — | 7 |
| Agent | — | — | — | 5 | 10 |
| 模板 | 1 | 1 | 1 | — | 3 |
| 工作流 | ✅ | — | — | — | ✅ |
| 惯例 | — | — | ✅ | — | ✅ |
| 货架 | — | — | — | — | ✅ |

---

## 🔗 来源

本商场所有装备来自 [Sweetteabittersugar/ai](https://github.com/Sweetteabittersugar/ai) 项目的可复用部分。不含密钥、个人路径、项目数据。

工作流方法论借鉴 BMAD (Breakthrough Method of Agile AI-Driven Development) + AutoGen/CrewAI 多 Agent 协作模式 + Scrum DoR/DoD 双门控。

调研标准借鉴 BMAD research skills + EviBound 双门验证 + Claude Code 4 级来源可信度。
