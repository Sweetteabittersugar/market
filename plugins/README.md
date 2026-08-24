# market 插件目录

这里包含 `market` Marketplace 的五个可安装插件。公开权威源是 [Sweetteabittersugar/market](https://github.com/Sweetteabittersugar/market)，分发分支固定为 `master`。

## 安装

```bash
claude plugin marketplace add Sweetteabittersugar/market

claude plugin install workflow-core@market
claude plugin install research-kit@market
claude plugin install story-dev@market
claude plugin install agent-personas@market
claude plugin install full-arsenal@market
```

## 内容

| 插件 | Skill | Agent | 模板 |
|---|---:|---:|---:|
| `workflow-core` | 3 | 0 | 1 |
| `research-kit` | 1 | 0 | 1 |
| `story-dev` | 1 | 0 | 1 |
| `agent-personas` | 0 | 5 | 0 |
| `full-arsenal` | 7 | 10 | 3 |

所有插件 manifest 与 Marketplace 条目版本统一为 `1.0.0`。插件使用用户项目自己的规则、运行时和目录结构；可以约定用户项目的 `.context`，但不依赖作者工作区、个人绝对路径或私有治理文件。

运行 `python scripts/verify.py` 可检查目录、名称、版本、来源、分支、本地链接与公开边界。
