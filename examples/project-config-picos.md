# 项目配置：PICOS

示例。复制到 `~/.agents/work/picos/PROJECT.md`，按实际情况修改。

## 外部评审文档

飞书 TR1 场景分析、TR2 特性设计、TR3 概要设计。开发环境无法访问飞书，需要时由用户导出 Markdown 后粘贴，保存为过程区的 `TR<n>.md` 快照。起草和回报偏离用 `write-tr`。

## 需求编号

- SR：`SR.<IR编码>.<分类>.<NNN>`，分类取 FUNC、PERF、DFX、NM、TEST、SEC。
- AR：`AR.<SR编码>.<进程缩写>.<NNN>`。
- PRODUCT.md 的 R 条目标注所属 SR，TECH.md 的设计条目标注所属 AR。

## 验证环境

- 开发机：单元测试与 Linux 内核协议栈替身。
- 实验室：开发机无法直连。上机验证用 `lab-request` 生成请求单，执行方式由个人决定。

## 长期文档位置

`specs/<特性>/PRODUCT.md`、`TECH.md`，与代码同一提交。

## 术语与约定

- 公司没有工单系统；任务状态只记录在过程区的 TASKS.md。
- 仓库提交管理较传统：过程文件一律不进入仓库。
