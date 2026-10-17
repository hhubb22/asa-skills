# 设计选择

18 个 skill 是可独立读取的能力。work 给出一条默认主路径，每一步都有跳过条件；叶子能力不回调 work，明确的小任务直接完成。用户自然语言授权有效，调用 skill 本身不产生额外权限。

v0.1 只提供选路表。面向缺少工作流经验的同事推广时，使用者需要先看到"接下来做什么"，再谈灵活选择，因此 v0.2 参考 Matt 的 ask-matt 补上了主路径、快速验证、修 bug 路径和阶段边界。

## 长期文档与任务管理

行为规格、技术设计、ADR 和术语表属于长期工程文档，与代码一起提交。`PROJECT.md` 推荐放在产品仓库 `.agents/PROJECT.md`，让不同机器和 Agent 读取同一份项目约定。没有仓库配置时，继续兼容旧版 `~/.agents/work/<项目>/PROJECT.md`；两份不合并，避免配置漂移。

**local 模式**保留原过程区：默认 `~/.agents/work/<项目>/<特性>/`，`TASKS.md` 与按需生成的 ALIGN、进度及交接文件不进入产品仓库。这满足没有工单平台的项目。

**issue 模式**目前使用 Linear MCP。工单负责任务目标、当前验收条件、依赖、优先级、进度和最终验收；Git 负责长期行为/技术契约、实现、测试及可追溯提交。`to-tasks` 经授权创建工单，`implement-specs` 在许可范围内记录当前任务的实施证据，独立 `code-review` 只出报告，主 Agent 核验后更新完成状态。`HANDOFF.md` 只在有远端或 Git 无法恢复的必要状态时按需生成，不默认创建用户目录文件。MCP 故障不改变既定的任务权威来源。

公司 TR 文档在飞书中、开发环境无法访问，且早于实际开发。TR 作为评审时点快照：开发前作为输入，开发后以仓库中的工程文档为准，偏离通过基线后的变化按约定回报。工程文档通过所属 SR/AR 编号追溯评审要求。

## 核心与扩展

核心 skill 使用通用说法：外部评审文档、上游需求条目、隔离验证环境，例子同时覆盖 Web 服务和网络设备。项目差异由 `PROJECT.md` 声明，不在每个 skill 中硬编码 Baton 或 PICOS；Linear 操作集中在 `issue-tracking`。`write-tr`、`lab-request` 为扩展，项目配置声明后才进入主路径。没有配置时不要求额外创建文档。

## 实验室隔离

开发环境无法直连实验室。lab-request 只说明需要什么：目的、环境要求、验证项与判据、需要的证据和回传格式。执行方式和操作规范属于执行者，由每个人按自己的环境和习惯决定。v0.2.0 曾提供实验室侧的 lab-runner，v0.2.2 曾把执行约束写进需求单，v0.2.3 都已移除。

## 能力边界

每个 skill 只规定自己的产物和判断，不替其他环节规定做法：需求单不规定执行流程，验证判定交回发起的任务，由发起方决定记录在哪里。

## PR/MR 材料

write-pr 以已有差异和验证结果为输入，生成正式 message，按需要增加 HTML 审核说明。项目模板优先，模板路径、语言和说明偏好由 PROJECT.md 指定。材料留在过程区，长期规格保留原位置。两份材料使用同一差异基线；审查发现引用来源，HTML 按需渲染检查。

## 单独安装与一致性

共享行为约定的唯一编辑源在 shared/。构建脚本将其按需复制到每个 skill 的 references/，并把许可和来源带入单独目录。这样单独复制一个 skill 不会丢失根目录参考。生成副本由工具检查字节一致，不人工分别维护。

只有两个写规格的 skill 带技术写作参考，其余能力使用自身的窄输出约定。操作约定仅在当前上下文尚未读取同版时读取，不要求每一轮重新读取。维护资料和测试不会作为日常运行上下文自动注入。

## 提示与强制隔离

SKILL.md 是行为指令，不是安全沙箱。只读需求必须结合宿主文件/命令权限实施；本包不更改这些权限，也不把全套工具权限写进 frontmatter。

核心使用标准 name/description/license/compatibility 字段，不依赖某一宿主的 disable-model-invocation。没有独立目录文件；description 就是触发说明，宿主与 `npx skills` 都直接读取它。所有 skill 都允许宿主根据 description 自动选用，靠 description 写清使用时机来避免误触发。v0.2.0 曾给 7 个 skill 加 Codex 专用的 `agents/openai.yaml` 关闭隐式调用，但 Codex 会把这类 skill 从模型可见的列表中整个隐藏，导致 work 无法衔接 align、to-tasks 等能力；v0.2.4 移除了全部宿主专用文件。

## 文档寿命

行为、设计、词汇、决策、执行状态各有归属，沿用已有路径，不要求每个任务生成固定文件集合。批准来源保持明确；实现偏离既定约定时先判断是缺陷还是需要变更设计。

## 自我维护

skill-doctor 从有出处的任务记录判断是否该改，允许删除规则和不修改。不会把调用频率当质量。收集器只接受显式文件，未知格式报告跳过；它不偷偷调用云端判分。

流程说明可以独立使用；脚本仅提供可机械执行的文件收集、共享同步、结构检查和评测准备，安装与分发交给 `npx skills` 和 Git。行为评价由真实模型/宿主的运行记录支持，不把关键词路由模拟包装成模型测评。

## 提示词与行为验证

参考 OpenAI《Rethinking skills and prompts for GPT-6 Astra》（https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra）与 Anthropic《Equipping agents for the real world with Agent Skills》（https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills）：description 负责触发，根 SKILL.md 留任务路由与必要边界，罕见流程放 references，避免每轮加载全套说明。共有的位置与授权规则只在 shared/ 定义，其余 skill 只规定特定产物。配置切换和远端写入要用真实宿主测试，静态断言不等于验证模型行为。
