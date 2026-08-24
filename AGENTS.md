# AGENTS.md — market

> 适用于 `D:\ai\projects\market`。这是独立 Git 仓库，局部规则优先于工作区通用规则。

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
cd D:\ai\projects\market
python setup.py --name
python -m compileall agency scripts
```

## 硬约束

- 本仓库是公共插件包和市场清单的唯一可编辑权威源；`D:\ai\plugins` 只是限时兼容投影，不得反向覆盖本仓库。
- 根工作区 `.claude/skills`、`.claude/agents` 是本地安装或适配面，不要求与公共分发资产逐文件相同。
- 不提交 `__pycache__/`、`*.egg-info/` 或本地安装产物。
- 修改插件结构时同步验证 `.claude-plugin/marketplace.json` 与目标插件清单。
- 不在结构整理中重命名公开插件、skill、agent 或命令标识符。
