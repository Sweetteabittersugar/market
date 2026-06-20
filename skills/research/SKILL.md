---
name: research
description: 标准化调研。4 步流程 + 4 级来源可信度 + 双门验证。触发词：/research、调研、研究一下、查一下、搜一下。
argument-hint: "<topic or question>"
category: workflow
---

# Research — 标准化调研

> 来源: BMAD research skills + EviBound 双门验证 + Claude Code 4 级来源可信度。
> 不凭训练数据做决策。每一条结论都要有出处。

## 何时用

- 任何需要外部信息的决策：技术选型、定价查询、最佳实践、合规要求
- 用户说 /research、调研、研究一下、查一下
- 阶段 2（技术选型）、阶段 0（需求分析）的调研部分

## 流程

### Step 1: 确认日期 + 分析意图

1. **确认当前日期**（`date`），不能凭训练数据里的日期
2. **分析意图**，选来源策略：

| 意图 | T1（主） | T2（辅） | T3（验） |
|------|---------|---------|---------|
| 技术实现 | 官方文档、OWASP、RFC | 专家博客、Conf 演讲 | GitHub Issues |
| 技术选型 | 官方 docs + benchmark | ThoughtWorks、State of JS | Dev.to 对比 |
| 市场/定价 | 官网定价页、Gartner | TechCrunch、Crunchbase | Reddit |
| 合规 | 政府/标准机构 ONLY | — | — |
| 趋势 | — | 科技媒体、专家博客 | 社区讨论 |

### Step 2: 多角度搜索

- **≥3 个不同搜索词**，中英文混合
- 每个搜索词**含年份或"latest"**（防过期数据）
- 示例：`"BMAD method workflow 2025"` + `"BMAD工作流 最新"` + `"AI agent development workflow standard"`

### Step 3: 交叉验证

- 每条结论至少 **≥2 个独立来源**
- T3 来源（社区）**必须经 T1-2 验证**才能用
- 来源矛盾 → 标注分歧，不强行统一
- 推断 → 标注"推断"，不伪装成事实
- 定价/版本号/配置值 → **优先官方页面**，标注查询日期

### Step 4: 结构化输出

用 `docs/templates/research-report.md` 模板输出报告到 `docs/research/{topic}-{date}.md`。

## 4 级来源可信度

| Tier | 可信度 | 来源 | 用法 |
|------|--------|------|------|
| **T1** | 90-100% | 官方文档、学术论文、ISO/OWASP/NIST、.gov/.edu | 主来源 |
| **T2** | 70-90% | Forbes/TechCrunch、知名专家博客、Gartner、Conf 演讲 | 行业趋势 |
| **T3** | 50-70% | Stack Overflow、Reddit、Medium、GitHub Discussions | 需 T1-2 交叉验证 |
| **T4** | 30-50% | 匿名、无作者、社交帖子 | 避免，或标注"未验证" |

## 规则

1. **WebSearch 不可用就中断** — 告诉用户，不等
2. **定价/版本必须搜最新** — 训练数据滞后 6-18 个月
3. **每条结论有出处** — URL + 日期 + Tier
4. **≥2 来源交叉验证** — 单来源 = 不可靠
5. **推断就标注** — `推断: ...`，不伪造成事实
6. **来源矛盾标出来** — 不强行统一，让用户判断
7. **输出报告存文件** — `docs/research/` 目录，可回溯
