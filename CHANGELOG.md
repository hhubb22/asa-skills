# Changelog

## Unreleased — 2026-09-13

转为个人 Git 仓库，安装、更新与移除交给 `npx skills`。删除 tools/install.py、tools/build_release.py、Makefile、MANIFEST.sha256、VERSION、catalog.json 和 docs/TEST-RESULTS.json。

skills/ 下的目录即全部清单：tools/library.py 从 skills/*/SKILL.md 派生 skill 列表，不再检查目录文件漂移，改为检查 upstream.lock.json 是否引用已删除的 skill；没有上游记录的新 skill 也能生成 SOURCES.md。README 与宿主说明改为 `npx skills` 用法。

保留 sync_shared、check、check_docs、prepare_eval 与 skill-doctor 收集器；skill 正文与共享约定未改。

## 0.1.0 — 2026-09-12

首版包含 11 个重写的 skills，中文模板和虚构写作示例。新增离线会话收集、安全复制安装、共享参考同步、结构检查与行为评测准备工具。

权限与路由分开；设计和审查不自动编码；明确的实现授权持续有效。skill-doctor 输出证据与候选补丁，不按调用率评分、不自动修改正式规则。

测试范围与限制见 docs/VALIDATION.md。
