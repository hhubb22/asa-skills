# Asa Skills · v0.1.0

一套独立维护、按任务选用的 Agent skills。以 Warp 与 Matt 的工作方法为参考，重新编写中文指令和配套材料；设计文档采用具体场景、真实取舍和可验证约定。没有固定的“需求 → 设计 → 实施”必经流水线。

**用户控制目标、范围和重大决定；Agent 在已有授权内完成必要工作。**work 提供统一入口，各专项 skill 也能独立使用。skill-doctor 根据真实记录提出改进，不自动改写正式规则。

## 第一批能力

| Skill | 来源与首版改造 |
|---|---|
| `work` | Matt 导航与 pstack 入口思路；轻量选路、保留授权，不复制总流水线 |
| `write-product-spec` | Warp；以可观察行为为核心，不编造需求或强制创建工单 |
| `write-tech-spec` | Warp + Rust RFC 论述；先调查，再说明变化、取舍与验证 |
| `implement-specs` | Warp；沿用已有明确依据，在授权范围内连续实施与验证 |
| `research` | Matt 一手证据方法；区分事实、推断和未知，不依赖后台 Agent |
| `code-review` | Matt 双路径审查；明确基线与工作区覆盖，不默认改代码 |
| `wait-what` | Matt；暂停新增操作，重新对齐并纠正可能的误解 |
| `domain-modeling` | Matt；维护术语与重要决定，保留标准/SDK/历史别名 |
| `handoff` | Matt；引用已有产物，保留基线、证据和授权，不复制整段聊天 |
| `to-questionnaire` | Matt；向真正的知情者收集事实与决定，不自动发送 |
| `skill-doctor` | Warp；最小有据改动，移除调用率评分，增加版本与保留样本核查 |

具体上游路径、Git blob 标识和改动说明见 [upstream.lock.json](upstream.lock.json)；许可见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。这不是上游官方分发包。

## 开始使用

正文不需要额外依赖。安装、检查和可选会话整理工具使用 Python 3.10+，只依赖标准库，不调用 API、不安装第三方包。

在解压后的目录运行：

```bash
python3 tools/check.py
python3 tools/install.py --dest "$HOME/.agents/skills"
python3 tools/install.py --dest "$HOME/.agents/skills" --apply
```

第二条只显示计划，第三条才复制。目录里已有同名 skill 时不会覆盖；已管理文件有手工改动时也会拒绝更新。请先核对现有 Warp/Matt 或其他同名来源，不要同时安装两个版本后指望宿主自动合并。

截至本版核验日期，Codex、Pi、Cursor 的本地环境均文档化支持 `~/.agents/skills`。宿主内使用 `$work`（Codex）、`/skill:work`（Pi）、`/work`（Cursor），也可以按宿主的 skill 选择器调用。修改后看不到时重新加载或新建会话。详情与来源见 [宿主说明](docs/HOSTS.md)。

直接调用示例：

```text
使用 work 处理这个特性：先查清现状，只交付设计，不改代码。
按已确认的设计实施，完成必要验证；不提交、不推送。
使用 code-review 检查当前修改，包含未跟踪文件；只报告。
wait-what。你刚刚为什么决定改变接口？先重新说明依据。
skill-doctor：只复盘我指定的这两个会话，提出补丁，不应用。
```

本库不是运行时沙箱。只读、共享设备和发布限制仍应由宿主权限与项目约定落实。安装器不会改你的 AGENTS.md、模型配置或权限设置。

## 安装到项目或只选部分能力

```bash
python3 tools/install.py --dest /path/to/project/.agents/skills --apply
python3 tools/install.py --dest "$HOME/.agents/skills" --only research code-review --apply
```

每个 skills/<name>/ 目录自包含，可以完整复制到宿主支持的位置。共享参考、模板与许可已包含，不能只复制 SKILL.md。只安装 work 不会自动安装它能选择的其他能力。

项目与用户级不要重复安装同名版本；安装器只检查指定目录，不枚举所有宿主搜索路径。离线服务器需要复制完整目录；本机安装不会自动出现在远端或云端。

## 更新与维护

将本目录作为独立仓库维护，日常改 skills/<name>/SKILL.md 和其专属资料。共享约定的唯一编辑源是 shared/；生成副本不手改。

```bash
python3 tools/sync_shared.py
python3 tools/check.py
python3 -m unittest discover -s tests -v
python3 tools/install.py --dest "$HOME/.agents/skills" --update --apply
```

安装更新只替换未被本地改动的受管版本，备份保留在目标 skills 目录的相邻 `.asa-skills-backups/` 下。没有 --update 不替换旧版；没有 --apply 不写入。已编辑安装副本时，先把差异合回独立库，不强制覆盖。

发布前执行 `python3 tools/build_release.py`，在 dist/ 生成 ZIP 和 SHA-256。包中 MANIFEST.sha256 校验逐文件内容；这些校验不等于来源签名。维护约定见 [设计说明](docs/DESIGN.md)。

## 文档与验证

写作模板与示例放在相关 skill 的 assets/、references/。它们不是自动创建的项目文件。已有需求、设计和术语位置优先；没有内容就不创建整套文档。

- [Astra 适配依据](docs/ASTRA-ALIGNMENT.md)
- [skill-doctor 使用与隐私](docs/SKILL-DOCTOR.md)
- [22 个行为试跑案例](evals/README.md)
- [实际验证与尚未验证范围](docs/VALIDATION.md)

本版已进行本地脚本与结构检查，但没有在你的真实 Codex、Pi 或 Cursor 会话里运行，也没有真实 Astra 的触发率、质量或性能数据。案例状态保持 not_run，安装后应使用真实任务核对。
