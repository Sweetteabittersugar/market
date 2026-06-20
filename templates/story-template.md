# Story S{XX}: {标题}

> 一个 agent 打开这个文件就能干活，不用翻任何其他文档。

| Field | Value |
|-------|-------|
| Story ID | S{XX} |
| Epic | {epic-name} |
| Status | backlog |
| Agent | {recommended-agent} |
| 协作模式 | {层级式 / 对话式 / 流水线式} |
| Depends On | {S{XX} or none} |

## What & Why

{一句话：解决什么问题，为什么重要}

## Context

Agent 需要的所有参考资料——不翻文档，直接看这里。

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

每个 Story ≤2 个文件变更。

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
- [ ] 代码已 commit
- [ ] sprint.yaml 已更新
- [ ] 可以进入阶段 {N+1}
