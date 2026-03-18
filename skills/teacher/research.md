# 当前状态

当前仓库只有 [prompt.md](/root/code/tools/skills/teacher/prompt.md)，还没有 `SKILL.md`、`references/`、`assets/`、`agents/openai.yaml` 或初始化脚本。也就是说，`teacher` skill 目前尚未成形，需要从零搭建一个可被其他 agent 直接调用的技能目录。

# 问题背景

目标不是做单轮教学 prompt，而是做一个可跨多轮复用的 skill。核心机制有四个：

- 外置学习状态：把学习进度和证据落到 `learning/<topic-slug>/` 文件，而不是依赖聊天记忆。
- 课程图谱：用模块依赖图组织学习路径，尤其要覆盖 LLM inference interview prep。
- 多模式教学：`map`、`teach`、`diagnose`、`drill`、`recall`、`plan` 六种模式要有明确触发条件和输出结构。
- 会话闭环：每次 substantive session 都要读状态、选模式、选模块、执行、写回状态和日志、给出唯一下一步动作。

# 需求梳理

- `SKILL.md` frontmatter 只能保留 `name` 和 `description`。
- `SKILL.md` 保持精简，详细规则下沉到 `references/`。
- 必须提供：
  - `SKILL.md`
  - `references/state-schema.md`
  - `references/session-modes.md`
  - `references/curriculum-design.md`
  - `references/llm-inference-curriculum.md`
  - `assets/learner-state-template.yaml`
  - `assets/session-log-template.md`
  - `agents/openai.yaml`
- 如有必要可增加 `scripts/init_learning_state.py`，并给出最小验证。
- `agents/openai.yaml` 需要与 skill 内容一致，且 `default_prompt` 必须显式提到 `$teacher`。
- 需要运行最相关的验证，优先包括 `quick_validate.py`。

# 实现选项

## 选项 1（推荐）：精简 SKILL.md + 参考文档 + 模板资产 + 初始化脚本

做法：

- 在 `SKILL.md` 中只保留触发条件、固定工作流、何时读取哪些 reference、何时读写状态。
- 在 `references/` 中分别定义状态 schema、模式规则、课程图谱设计、LLM inference 默认课程图。
- 在 `assets/` 中提供状态和 session log 模板。
- 增加 `scripts/init_learning_state.py`，负责初始化 `learning/<topic-slug>/` 目录和模板文件。
- 用生成脚本或手写方式产出一致的 `agents/openai.yaml`。

优点：

- 最符合 `skill-creator` 的渐进披露原则。
- 模板和脚本让 skill 真正可重复使用，而不是纯文档说明。
- 后续扩课程图或增加 topic 时不需要改核心工作流。

缺点：

- 文件数更多，需要保证各文件之间不重复且相互引用清晰。

## 选项 2：单文件重 SKILL.md，少量辅助文件

做法：

- 把大部分规则都写进 `SKILL.md`，参考文件只保留课程图和模板。

优点：

- 实现快，入口集中。

缺点：

- 容易违反“尽量保持 `SKILL.md` 精简”的要求。
- 后续维护会变差，触发后上下文负担更大。

## 选项 3：不加初始化脚本，仅靠文档要求手动创建状态文件

做法：

- 只提供模板和说明，不提供 `scripts/init_learning_state.py`。

优点：

- 代码最少。

缺点：

- 初始化步骤依赖 agent 手工复制模板，重复、易错，也削弱“长期复用”目标。

# 推荐方案

优先采用选项 1。

原因：

- 用户明确要求“外置状态 + 课程图谱 + 多模式 + 会话闭环”四个机制同时成立，而模板加脚本是把这些机制变成可执行工作流的最低成本方式。
- 这个 skill 面向跨多轮、长期学习，状态初始化和追加 session 记录是高频动作，适合用脚本固定化。
- `SKILL.md` 精简、规则拆分到 `references/`，更符合 skill 设计规范。

# 测试策略

## 策略 1（推荐）

- 运行 `python /root/.codex/skills/.system/skill-creator/scripts/quick_validate.py /root/code/tools/skills/teacher`
- 运行 `python scripts/init_learning_state.py --topic "LLM inference interview prep"` 或等价最小命令，验证能创建 `learning/<topic-slug>/learner-state.yaml` 与 `session-log.md`
- 检查生成文件是否与模板一致且路径符合约定

## 策略 2

- 只运行 `quick_validate.py`，再人工检查模板和文档

缺点：

- 无法验证初始化脚本是否真的可运行。

## 策略 3

- 写额外自动化测试

缺点：

- 对当前小型 skill 仓库来说开销偏高，不是最小可行验证。
