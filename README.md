# market — Claude Code 插件市场

> **v1 feature-complete / archived.** `master` 保留为五个插件清单的稳定分发协议；仓库归档后不再承诺持续功能开发或固定 Issue 响应时间。

[![CI](https://github.com/Sweetteabittersugar/market/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/Sweetteabittersugar/market/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/Sweetteabittersugar/market)](https://github.com/Sweetteabittersugar/market/releases/tag/v1.0.0)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

这是一个可直接注册到 Claude Code 的公开插件市场。v1.0.0 固化五个可独立安装的插件，并用仓库内验证脚本约束名称、版本、来源、分发分支和本地链接。

## 安装

```bash
claude plugin marketplace add Sweetteabittersugar/market

claude plugin install workflow-core@market
claude plugin install research-kit@market
claude plugin install story-dev@market
claude plugin install agent-personas@market
claude plugin install full-arsenal@market
```

`market` 是 [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json) 声明的 marketplace 名称。安装前可先运行 `claude plugin marketplace list`，避免与本地同名市场混淆。

## 五个插件

| 插件 | 内容 | v1.0.0 规模 |
|---|---|---|
| `workflow-core` | `/spec`、`/gate-check`、`/retro` 与工作流资料 | 3 Skill |
| `research-kit` | `/research` 与调研报告模板 | 1 Skill |
| `story-dev` | `/create-story`、Story 模板与项目惯例 | 1 Skill |
| `agent-personas` | 产品、架构、QA、复盘与代码审查角色 | 5 Agent |
| `full-arsenal` | 上述能力的组合包 | 7 Skill、10 Agent、3 模板 |

每个 Marketplace 条目与对应 `plugins/<name>/.claude-plugin/plugin.json` 的版本均为 `1.0.0`，源码统一来自 `https://github.com/Sweetteabittersugar/market.git` 的 `master` 分支。

## 可移植边界

- 插件读取并服从用户项目自己的规则、运行时和目录结构，不依赖作者机器上的工作区。
- 插件可以约定用户项目自己的 `.context` 文件，但本仓库不分发内部治理记录或私有决策链接。
- 插件中的命令和 Agent 以当前 Claude Code 会话权限运行；安装前应审阅内容，并在项目侧限制文件、Shell 和网络权限。
- 本仓库不包含 API key。需要访问模型或网络服务时，数据会发送到用户选择并配置的服务商。

## 验证

```bash
python scripts/verify.py
git diff --check
```

验证器检查五个插件目录及 manifest、`1.0.0` 版本、canonical source URL、`master` ref、本地 Markdown 链接、公开边界、历史 Python helper 元数据、Python 编译和 Git 差异格式。

## 历史 Python helper

`agency/` 与 `setup.py` 保留早期本地费用/历史记录辅助工具，Python 包名为 `agency-v2`，版本为 `2.0.0`。这是独立的遗留版本号，不是 Marketplace v1.0.0 的插件版本，也不代表 PyPI 发布。

如需本地验证该 helper：

```bash
git clone https://github.com/Sweetteabittersugar/market.git
cd market
python -m venv .venv
python -m pip install -e .
python -m agency.check
```

安全问题请参阅 [SECURITY.md](SECURITY.md)。

## License

MIT © 2026 Sweetteabittersugar
