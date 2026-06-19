# 常见问题

## 费用追踪不工作？

1. 确认 Hook 已注册：检查 `~/.claude/settings.json` 中有 `"agency.hooks.stop"`
2. 确认数据库存在：`ls ~/.agency/agency.db`
3. 检查错误日志：`cat ~/.agency/errors.log`
4. 手动运行：`python -m agency.hooks.stop`（需要 stdin 输入）

## 如何停止费用追踪？

从 `~/.claude/settings.json` 的 `hooks.Stop` 数组中删掉 agency 条目。

## 如何重置数据？

```bash
rm ~/.agency/agency.db
python -c "from agency.db import get_db; get_db()"  # 重新初始化
```

## 支持哪些模型？

DeepSeek V4 Pro + MiMo V2.5 Pro。新增模型改 `agency/cost.py` 中的 PRICING_CNY_PER_M 字典。

## 安装失败？

确认 Python ≥ 3.8，pip 可用。Windows 用 Git Bash 运行 install.sh。
