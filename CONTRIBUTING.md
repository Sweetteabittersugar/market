# Contributing

Market v1 已 feature-complete，仓库归档后以只读稳定分发为主。维护采用 best-effort，不承诺固定响应 SLA；安全问题请按 [SECURITY.md](SECURITY.md) 私密报告。

## 本地验证

```bash
git clone https://github.com/Sweetteabittersugar/market.git
cd market
python scripts/verify.py
git diff --check
```

## 变更要求

- 不重命名五个公开插件或把分发 ref 从 `master` 改走。
- 插件版本、Marketplace 条目和 manifest 必须同步。
- 不提交仓库 `.context`、内部治理记录、个人绝对路径、私有仓库链接、密钥或生成产物。
- 用户项目可以有自己的 `.context` 约定，但插件不得依赖作者工作区。
- PR 需说明结果、动机和可复现验证；CI 必须通过。

新增 Agent 或 Skill 时，应同步更新所属插件内容、说明和验证规则。由于 v1 已封版，大规模功能扩张更适合 fork。
