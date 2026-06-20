---
name: create-story
description: 从 Spec 和 API 设计生成 Story 文件。触发词：/create-story、创建故事、拆分故事、写 story、故事分解。
argument-hint: "<epic-name or story-count>"
category: workflow
---

# Create Story — 故事分解技能

## 何时用

- 阶段 3（API 设计）完成后，进入阶段 3.5
- 用户说 /create-story、创建故事、拆分故事、写 story

## 流程

1. **读 Spec** — 找到项目 Spec 文件（`docs/*-spec.md` 或 `docs/spec/*.md`）
2. **读 API 契约** — 如有 `docs/api/` 目录读端点列表
3. **确认 Epic** — 从 Spec 功能清单提取 Epic，让用户确认优先级
4. **拆 Story** — 每 Epic 拆 2-5 个 Story，每个 Story ≤2 文件变更，垂直切片
5. **生成文件** — 用 `docs/templates/story-template.md` 模板，输出到 `docs/stories/S{XX}-{slug}.md`
6. **更新 sprint.yaml** — 新 Story 加入 `.context/sprint.yaml`，status=backlog

## 规则

- 单人项目 Epic ≤3 个，每 Epic Story ≤5 个
- 垂直切片：每个 Story 是一个完整的小功能（不是"所有 model 层"这种水平拆分）
- Context 段必须填满——agent 打开 Story 文件就能干活，不用翻别的文档
- 依赖标注清楚：哪个 Story 必须先完成
- 命名：`S01-project-setup.md`, `S02-user-auth.md`（数字+slug，可排序可读）

## 模板

使用 `docs/templates/story-template.md`。
