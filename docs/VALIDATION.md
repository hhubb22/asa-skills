# 验证记录

2026-10-06（Linux/Python 3.13.16）：新增 write-tr 后，`check.py` 对 12 个 skills 通过，36 项单元测试通过；测试中的 skill 与案例数量随之更新，upstream.lock.json 改为允许没有上游记录的新增 skill。write-tr 没有在真实宿主中试跑。

最近执行：2026-09-13，macOS 27.0，Python 3.14.7。首版（0.1.0，2026-09-12）在 Linux/Python 3.13.5 下执行过等价检查。

## 实际执行

- `python3 tools/check.py`：11 个 skills 的标准字段、目录名、相对引用、自包含依赖、生成副本、upstream.lock.json 与目录一致性和 Python 语法检查通过。
- `python3 -m unittest discover -s tests -v`：36 项测试通过，覆盖独立复制、引用失效、共享文件漂移、过期 lock 记录、无上游记录的新增 skill、评测准备和收集器行为。
- 收集器测试覆盖可见记录提取、隐藏块跳过、常见凭据脱敏、未知记录计数、截断报告、非法 JSONL、重复/超限输入、目录/符号链接/FIFO 拒绝、私有输出权限。用例是合成材料，不是对真实宿主所有版本的认证。
- 文档示例的结构与 R 编号引用检查通过；这些检查不判断事实、批准状态或设计正确性。
- `npx skills add . --list` 在本地检出上列出全部 11 个 skill 及其 description；这只验证发现，未实际执行安装到宿主目录。

## 未执行或不能据此证明

没有调用真实 Astra、Codex、Pi 或 Cursor 进行行为 A/B，没有访问用户真实项目和历史会话。22 个案例提供后续试跑输入，不包含通过率。

宿主目录和基本调用方式按官方文档核对，未进行端到端宿主安装测试。`npx skills add`/`update`/`remove` 的行为由该 CLI 负责，本库不再验证安装冲突、备份或回滚。

没有在 Windows 或 Python 3.10 中运行。Python 3.10 是实现要求，兼容声明不等于这些环境的运行证据。标准 YAML 采用本库的标量子集；不是任意 YAML 格式转换工具。

上游文件以已读取文本的 Git blob 标识记录；默认分支头单独记录。没有把 blob SHA 冒充 commit，也没有假称本地改写通过了上游测试。
