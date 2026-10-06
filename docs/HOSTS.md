# 宿主与可移植性

核验日期：2026-09-12。本版只采用标准 SKILL.md 与普通相对引用，不捆绑 MCP、不要求改 Agent 源码，也不依赖宿主专用的任务工具。

| 宿主 | 文档确认的本地共享位置 | 显式调用 |
|---|---|---|
| Codex | ~/.agents/skills；项目 .agents/skills | `$work` 或 skills 选择器 |
| Pi | ~/.agents/skills，也支持 ~/.pi/agent/skills | `/skill:work`；项目需满足宿主信任条件 |
| Cursor | ~/.agents/skills，也支持 ~/.cursor/skills | `/work` 或 skill 选择器 |

来源：[Codex](https://developers.openai.com/codex/skills)、[Pi](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/skills.md)、[Cursor](https://cursor.com/docs/skills)。这张表是文档兼容性核验，不是宿主端集成测试结果。

## 调用与权限分开

核心不使用 disable-model-invocation、mode 或 allowed-tools 等宿主差异较大的 frontmatter 字段。偏向显式调用的能力另带 `agents/openai.yaml`，以 `policy.allow_implicit_invocation: false` 让 Codex 只在显式调用时使用；该文件是 [OpenAI 文档](https://learn.chatgpt.com/docs/build-skills)中的可选元数据，其他宿主是否读取未核验。不要把可自动发现误当成允许自动发送、发布或修改已批准语义。

同名来源可能并存，不能假定合并或覆盖顺序。安装前用 `npx skills list` 检查已装项；只安装一个实际采用的版本。叶子能力可以直接使用，work 只按当前请求选路。

当前宿主明确将某项能力限制为只能手动调用时，路由器给出建议或请用户显式调用，不绕过限制。不存在统一 Skill API 时使用宿主支持的发现和文件读取，不编造工具。

## 本地与远端

本机用户级目录不自动同步到 SSH、云 Agent 或自托管工作节点。需要时在目标环境中重新执行 `npx skills add`，或明确提交项目级 skills。Cursor 的云同步另有目录和授权规则，不能假定 ~/.agents/skills 自动上云。

## 环境要求

标准 Markdown 正文可供任何遵循该格式的 Agent 读取，但本版只核对了上表三种宿主的文档。其他客户端应先确认目录和加载行为；不宣称已验证。

Python 维护工具要求 3.10+，无外部依赖；安装本身只需要 Node.js 以运行 `npx skills`。维护工具已在 Linux/Python 3.13 与 macOS/Python 3 下执行；未在其他 Python 版本中执行。收集器的文件权限在 POSIX 环境下验证；本版不承诺 Windows 的权限隔离效果。
