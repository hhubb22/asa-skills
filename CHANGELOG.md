# Changelog

## 0.2.1 — 2026-10-06

核心与领域分层，不拆仓库。

- 核心 skill 改用通用说法：外部评审文档、上游需求条目、隔离验证环境；切片例子同时给出 Web 服务和网络设备。
- 新增项目配置：过程区的 `PROJECT.md` 声明评审文档、需求编号、验证环境、文档位置和术语，由任务边界规定读取方式；work 附带模板，examples/ 提供 PICOS 示例。
- work 中的评审材料和隔离验证步骤只在项目配置声明后出现。
- diagnose-bugs 的回路清单按通用、服务端与前端、网络设备分组，补回 HTTP 脚本和浏览器自动化。
- README 与使用指南分为核心与扩展两组安装命令，指南增加"开始前准备"。

## 0.2.0 — 2026-10-06

面向团队推广的版本。

- work 重写为主路径：对齐 → 行为规格 → 技术设计 → 拆分 → 实施 → 审查，每步写明跳过条件；新增快速验证、修 bug 路径和阶段边界。
- 新增 align（结构化复述，问题限于阻塞项，最多 2 轮每轮 5 个）、to-tasks（纵向切片，输出到过程区）、diagnose-bugs（反馈回路优先）、lab-request 与 lab-runner（隔离实验室的请求单与执行）。
- 共享约定：授权规则集中到 operating-contract；定义长期文档与过程区位置；加入对真实产物验证、追根因、解释数字三条验证原则。技术写作加入量化默认值。
- 行为规格与技术设计改为通过标注所属 SR/AR 与 TR 追溯；write-tr 同步调整。
- 全部 description 补充使用时机，正文改为正向表述；显式调用的 skill 增加 `agents/openai.yaml` 关闭 Codex 隐式调用。
- 新增使用指南、6 个行为案例和 100 条触发测试。

## 0.1.1 — 2026-10-06

新增 write-tr：按公司 TR1 场景分析、TR2 特性设计、TR3 概要设计模板起草飞书评审文档。TR 视为评审时点快照：开发前作为工程文档的输入，开发后由仓库中的 PRODUCT/TECH 作为权威来源，偏离通过基线后变更记录回报。人填字段保留占位，SR/AR 编号与工程文档共用。work 路由表、README 与评测案例同步更新。

## Unreleased — 2026-09-13

转为个人 Git 仓库，安装、更新与移除交给 `npx skills`。删除 tools/install.py、tools/build_release.py、Makefile、MANIFEST.sha256、VERSION、catalog.json 和 docs/TEST-RESULTS.json。

skills/ 下的目录即全部清单：tools/library.py 从 skills/*/SKILL.md 派生 skill 列表，不再检查目录文件漂移，改为检查 upstream.lock.json 是否引用已删除的 skill；没有上游记录的新 skill 也能生成 SOURCES.md。README 与宿主说明改为 `npx skills` 用法。

保留 sync_shared、check、check_docs、prepare_eval 与 skill-doctor 收集器；skill 正文与共享约定未改。

## 0.1.0 — 2026-09-12

首版包含 11 个重写的 skills，中文模板和虚构写作示例。新增离线会话收集、安全复制安装、共享参考同步、结构检查与行为评测准备工具。

权限与路由分开；设计和审查不自动编码；明确的实现授权持续有效。skill-doctor 输出证据与候选补丁，不按调用率评分、不自动修改正式规则。

测试范围与限制见 docs/VALIDATION.md。
