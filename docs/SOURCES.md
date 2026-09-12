# 核验来源

核验日期：2026-09-12。网页会变化；可追溯的上游内容标识见 [upstream.lock.json](../upstream.lock.json)。以下文档仅作维护参考，不是每个任务必须读取的上下文。

## 官方格式与模型建议

- [Agent Skills specification](https://agentskills.io/specification)：目录、frontmatter 与渐进读取。
- [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)：2026-09-11 发布。
- [OpenAI model guidance](https://developers.openai.com/api/docs/guides/latest-model)：Astra 的目标延续、写作、委派与验证建议。
- [Codex skills](https://developers.openai.com/codex/skills)：当前跳转至 ChatGPT Learn，核验了本地路径、显式调用与独立 skills。

## 宿主

- [Pi skills](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/skills.md)：本地发现与命令。
- [Cursor skills](https://cursor.com/docs/skills)：本地目录和云端同步边界。

## 参考实现

- [Warp common-skills](https://github.com/warpdotdev/common-skills)：规格、实施、维护。
- [Matt Pocock skills](https://github.com/mattpocock/skills)：路由、协作、调查与审查。
- [Rust RFC template](https://github.com/rust-lang/rfcs/blob/master/0000-template.md)：先举例再精确定义，说明真实取舍与未决问题。
- [pstack poteto-mode](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/SKILL.md)：仅借鉴入口组织概念，不采用其强制编排与操作权限。
