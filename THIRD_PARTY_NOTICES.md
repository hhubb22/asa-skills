# 来源与许可

这是一套为 Asa 重写的个人 skills 库，不是 Warp、Matt Pocock、Cursor 或 OpenAI 的官方产品，也不是对上游完整仓库的镜像。

基于 Warp common-skills 与 Matt Pocock skills 的工作方法和部分结构进行改写，按其 MIT 许可保留作者声明。脚本、中文模板、示例与测试在本次版本中重新编写。完整许可见 [LICENSE](LICENSE)、[Warp MIT](licenses/warp-MIT.txt) 和 [Matt MIT](licenses/matt-MIT.txt)。每个可独立安装的 skill 都附带相同许可与单独来源说明。

[upstream.lock.json](upstream.lock.json) 保存参考文件的 Git blob SHA、来源与改动性质。blob SHA 能定位参考文本，但不能当成提交 SHA；记录的默认分支头用于后续比对，不用来伪造逐文件的提交关联。

Rust RFC 模板与 pstack 仅作为论述和路由思路的参考，未复制其实现、模板或大段表达。OpenAI 文档只链接并做简短说明，不随包分发全文。更新时核对实际源文件和许可，不盲目覆盖本地改版。
