# Asa Skills

一套独立维护、按任务选用的个人 Agent skills，通过 [`npx skills`](https://github.com/vercel-labs/skills) 安装与更新。以 Warp 与 Matt 的工作方法为参考，重新编写中文指令和配套材料；设计文档采用具体场景、真实取舍和可验证约定。没有固定的“需求 → 设计 → 实施”必经流水线。

**用户控制目标、范围和重大决定；Agent 在已有授权内完成必要工作。**work 提供统一入口，各专项 skill 也能独立使用。skill-doctor 根据真实记录提出改进，不自动改写正式规则。

## 能力一览

| Skill | 来源与改造 |
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
| `write-tr` | 本库新增；按公司 TR1/TR2/TR3 模板起草评审文档，人填字段保留占位，与工程文档共用 SR/AR 编号 |

每个 skill 的 frontmatter `description` 就是它的触发说明；本仓库不维护另一份目录文件。具体上游路径、Git blob 标识和改动说明见 [upstream.lock.json](upstream.lock.json)；许可见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。这不是上游官方分发包。

## 安装

skills 位于 `skills/<name>/`，是 `npx skills` 默认扫描的位置。将仓库推到 Git 远端后：

```bash
# 列出可安装的 skills
npx skills add hhubb22/asa-skills --list

# 安装到当前项目（交互选择 skill 与目标 Agent）
npx skills add hhubb22/asa-skills

# 安装全部到用户级目录，指定 Agent
npx skills add hhubb22/asa-skills --skill '*' -g -a codex -a cursor

# 只装部分
npx skills add hhubb22/asa-skills --skill research --skill code-review
```

也可以从本地检出安装，便于改完立即试用：

```bash
npx skills add /path/to/asa-skills --skill work -g
```

更新、查看与移除同样交给 CLI：`npx skills update`、`npx skills list`、`npx skills remove <name>`。CLI 默认以符号链接接入各 Agent 目录，`--copy` 改为独立复制。

每个 `skills/<name>/` 目录自包含：共享参考、模板与许可已包含在内，不能只复制 SKILL.md。只安装 work 不会自动安装它能选择的其他能力。已经从 Warp/Matt 或其他来源装过同名 skill 时先核对，不要同时保留两个版本后指望宿主自动合并。

宿主内使用 `$work`（Codex）、`/skill:work`（Pi）、`/work`（Cursor），也可以按宿主的 skill 选择器调用。修改后看不到时重新加载或新建会话。详情与来源见 [宿主说明](docs/HOSTS.md)。

直接调用示例：

```text
使用 work 处理这个特性：先查清现状，只交付设计，不改代码。
按已确认的设计实施，完成必要验证；不提交、不推送。
使用 code-review 检查当前修改，包含未跟踪文件；只报告。
wait-what。你刚刚为什么决定改变接口？先重新说明依据。
skill-doctor：只复盘我指定的这两个会话，提出补丁，不应用。
```

本库不是运行时沙箱。只读、共享设备和发布限制仍应由宿主权限与项目约定落实。安装不会改你的 AGENTS.md、模型配置或权限设置。

## 维护

日常改 `skills/<name>/SKILL.md` 和其专属资料。共享约定的唯一编辑源是 `shared/`；各 skill `references/` 下的同名副本、`LICENSE` 和 `SOURCES.md` 由脚本生成，不手改。

```bash
python3 tools/sync_shared.py
python3 tools/check.py
python3 -m unittest discover -s tests -v
```

新增 skill 只需创建 `skills/<name>/SKILL.md`（frontmatter 含 `name`、`description`、`license`），运行 `sync_shared.py` 生成配套文件；有上游参考时在 `upstream.lock.json` 补一条记录。`check.py` 校验 frontmatter、200 字描述预算、120 行正文预算、相对链接自包含和生成文件一致。

维护工具使用 Python 3.10+，只依赖标准库，不调用 API。安装、更新与打包不再由本仓库脚本负责。维护约定见 [设计说明](docs/DESIGN.md)。

## 文档与验证

写作模板与示例放在相关 skill 的 assets/、references/。它们不是自动创建的项目文件。已有需求、设计和术语位置优先；没有内容就不创建整套文档。

- [Astra 适配依据](docs/ASTRA-ALIGNMENT.md)
- [skill-doctor 使用与隐私](docs/SKILL-DOCTOR.md)
- [24 个行为试跑案例](evals/README.md)
- [实际验证与尚未验证范围](docs/VALIDATION.md)

本库已进行本地脚本与结构检查，但没有在真实 Codex、Pi 或 Cursor 会话里做行为 A/B，也没有真实 Astra 的触发率、质量或性能数据。案例状态保持 not_run，安装后应使用真实任务核对。
