# 维护这个 skills 库

本文件仅用于开发本库，不安装到消费项目中。日常使用从 README 或具体 SKILL.md 开始。安装、更新与移除由 `npx skills` 负责，本库不再维护安装器、打包脚本或独立目录文件；skills/ 下的目录就是全部清单。

编辑共享约定时修改 shared/，再运行 `python3 tools/sync_shared.py`；不要手改 skills/*/references 中的同名生成副本或各 skill 的 LICENSE/SOURCES.md。

改动 skill 时同步必要的模板、work 路由表、upstream.lock.json 及评测案例。新增规则写清所防止的问题，优先删除或替换。保持源码与安装产物的相对引用自包含，不依赖宿主未确认的字段或工具名。

完成改动后运行 `python3 tools/check.py` 和 `python3 -m unittest discover -s tests -v`。脚本改变需测试异常路径、覆盖保护和输入处理；行为改变需更新真实试跑计划，不把静态测试说成模型评测。

原始会话、密钥、公司代码和真实评测输出不提交。本库默认只有合成测试材料；不要为了补案例读取用户全部历史。
