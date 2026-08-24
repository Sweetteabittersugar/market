# AGENTS.md — market

> 适用于任意位置克隆的 `market` 独立仓库；进入用户项目后，以该项目自己的规则为准。

## 项目定位

- AI 开发装备市场，提供 Claude Code 插件、agents、skills、templates 和兼容安装脚本。
- Python 包名仍包含历史名称 `agency-v2`；目录和对外仓库身份统一称为 `market`。

## 主要结构

- `.claude-plugin/`、`plugins/`：插件市场元数据与插件包。
- `agents/`、`skills/`、`templates/`：可分发资产。
- `agency/`、`scripts/`：传统安装与检查工具。
- `docs/`：设计与使用文档。

## 本地入口

```powershell
cd <clone-path>\market
python setup.py --name
python -m compileall agency scripts
```

## 硬约束

- 本仓库是公共插件包和市场清单的唯一权威源；任何本地安装副本都只是投影，不得反向覆盖源码。
- 用户项目的 `.claude/skills`、`.claude/agents` 和 `.context` 可以按项目约定存在，但不得成为本仓库的机器绑定依赖。
- 仓库自身的 `.context`、治理回执、个人路径和私有仓库链接不得进入公开发布树。
- 不提交 `__pycache__/`、`*.egg-info/` 或本地安装产物。
- 修改插件结构时同步验证 `.claude-plugin/marketplace.json` 与目标插件清单。
- 不在结构整理中重命名公开插件、skill、agent 或命令标识符。
