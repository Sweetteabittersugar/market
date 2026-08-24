# Story S{XX}: {标题}

> Story 提供最小充分上下文；执行者仍必须读取适用的 `AGENTS.md` 和关联任务契约。

| Field | Value |
|-------|-------|
| Story ID | S{XX} |
| Epic | {epic-name} |
| Status | backlog |
| Persona Hint | {recommended-persona or none} |
| Task Contract | `.context/tasks/{task-id}.yaml` |
| Orchestration Hint | {single / manager_workers / evaluator_optimizer} |
| Depends On | {S{XX} or none} |

## What & Why

{一句话：解决什么问题，为什么重要}

## Context

只列完成本 Story 必需的精确资料；不要复制整份文档或会话历史。

- **项目惯例**: `docs/conventions.md`（命名/模式/陷阱——新人必读）
- **Spec**: `docs/{spec}.md#section`
- **API 契约**: `docs/api/{resource}.md`（或内联下方）
- **设计决策**: `.context/decisions/{topic}.md`
- **参考代码**: `path/to/similar/feature.py`

## Acceptance Criteria

可自动验证，不是"用户体验好"。

- [ ] Given {前置条件}, When {操作}, Then {预期结果}
- [ ] Given {前置条件}, When {操作}, Then {预期结果}

## Files to Create/Modify

保持可独立验收的最小范围；真正允许写入的边界以任务契约 `allowed_paths` 为准。

| File | Action | Notes |
|------|--------|-------|
| `path/to/new.py` | Create | 新建，描述用途 |
| `path/to/old.py` | Modify | 修改点说明 |

## Technical Notes

- **模式参考**: {已有代码中类似的实现}
- **约束**: {不要改什么}
- **陷阱**: {容易踩的坑}

## Observability

> AI 代码最大盲区是运行时。本 Story 必须暴露以下信号。

- **日志**: {关键路径 log 点——请求入口/外部调用/错误边界/状态变更}
- **指标**: {需要暴露的 counter/gauge——请求量/延迟/错误率/队列深度}
- **链路**: {需要传递 trace context 的跨服务调用——如适用}

---

## Dev Record

> 实现完成后由 coder 填写。**这是下一阶段的交接文件——别留空。**

### 实际变更
| File | Action | 说明 |
|------|--------|------|
| `path/to/file.py` | Created/Modified | 实际做了什么 |

### 与计划的偏差
- {无 / 有：具体偏差 + 原因}

### 遇到的问题
- {无 / 有：问题描述 + 怎么解决的}

### 留给下一阶段
- {需要验证的点 / 已知限制 / 未完成的部分}

### 教训
- {下次注意什么，为什么}

---

## QA Record

> 验证完成后由 qa 填写。**决定能否进入下一阶段。**

### 门控结论: PASS / CONCERNS / FAIL

- **风险等级**: R0 / R1 / R2 / R3
- **独立复核**: {required / not-required / completed}

### 验收标准验证
- [x] / [!] / [ ] AC-01: {描述} — {证据：curl输出/截图/测试日志}
- [x] / [!] / [ ] AC-02: ...

### 发现的问题
| # | 严重度 | 描述 | 文件:行号 | 修复建议 |
|---|--------|------|----------|---------|
| 1 | 高/中/低 | ... | ... | ... |

### 遗留风险
- {无 / 有：风险描述 + 缓解措施}

### 下一阶段准入
- [ ] 阻塞问题已清零
- [ ] CONCERNS 已按风险策略接受，或不存在 CONCERNS
- [ ] 任务状态与必要交接材料已更新
- [ ] 如任务明确授权提交，commit 已完成；否则标记为不适用
- [ ] 可以进入阶段 {N+1}
