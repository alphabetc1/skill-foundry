你是一个有文件系统读写权限的 coding agent。你的任务是在当前目录实现一个可长期复用的 `teacher` skill，用来支持“跨多轮会话的系统化学习与面试准备”。

目标不是写一个会讲课的 prompt，而是实现一个“有状态的教学工作流 skill”。它必须解决以下问题：

1. 学习内容无法系统化梳理。
2. 每次对话上下文会丢失，模型不知道学习者当前状态。
3. 交互模式单一，无法在概览、讲解、诊断、测验、复习、规划之间切换。

请先检查当前目录已有文件，再在此基础上设计和实现，不要盲目重建。

## 用户场景

用户正在准备大模型相关面试，尤其是 LLM inference。用户希望：

- 能从一个模块的全景图开始，而不是零散问答。
- 能持续记录自己的当前水平、薄弱点、误区、已学内容和下一步建议。
- 能在不同会话中切换模式：
  - 有时要概览
  - 有时要讲解原理
  - 有时要做诊断
  - 有时要做面试问答练习
  - 有时要复习以前学过的内容，避免遗忘
- 每次会话结束后，skill 都能明确“现在学到了哪里、哪里还不稳、下次该学什么”。

## 设计要求

请把 skill 设计成以下结构：

### 1. 外置学习状态

不要依赖聊天记忆。把学习者状态外置到工作区文件。

至少设计：

- `learning/<topic-slug>/learner-state.yaml`
- `learning/<topic-slug>/session-log.md`

需要提供模板文件，并在 `SKILL.md` 中规定何时创建、何时读取、何时更新。

状态中至少要覆盖：

- 学习主题
- 当前目标
- 截止时间或面试时间
- 背景水平
- 当前模块
- 已掌握知识点
- 不稳固知识点
- 前置依赖缺口
- 常见误区
- review queue
- 最近几次 session 的证据
- 下一步唯一推荐动作

### 2. 课程图谱而不是平面清单

把学习路径设计成 curriculum graph，而不是简单 checklist。

每个模块至少应包含：

- 模块名称
- 为什么重要
- 前置依赖
- must-know points
- interview signals
- exit criteria

对于 LLM inference，请给出一个默认课程图，至少覆盖：

- end-to-end request lifecycle
- prefill / decode
- batching / scheduling
- KV cache
- kernels / hardware bottlenecks
- parallelism / distributed serving
- quantization
- decode optimizations
- serving architecture
- reliability / observability

### 3. 多模式教学

至少支持这些 session mode，并写清楚每种模式的输出和使用条件：

- `map`
- `teach`
- `diagnose`
- `drill`
- `recall`
- `plan`

要求：

- 每次只选一个主模式
- 模式切换要有明确触发条件
- 不同模式输出结构应不同

### 4. 会话闭环

在 `SKILL.md` 中明确规定每次 substantive session 的固定循环：

1. 读取 learner state
2. 判断当前 mode
3. 选择课程图中的当前模块
4. 执行教学/诊断/测验
5. 更新 learner state 和 session log
6. 生成下一个明确动作

### 5. 交互质量要求

请把以下规则写进 skill：

- 不要因为“刚解释过”就把某个知识点标记为 mastered。
- mastered 必须基于 learner 的可验证表现，例如复述、比较、推导、应用。
- 对 interview prep，优先强调概念边界与 tradeoff。
- broad overview 结束时必须给出推荐下一课。
- 测验模式下要一题一题地问，不要一次性把答案全给出来。
- 对用户的错误回答，要记录为 misconception 或 shaky topic，而不是直接略过。

## 文件与实现要求

请尽量保持 `SKILL.md` 精简，把详细规则放到 `references/`。

优先实现或更新以下内容：

- `SKILL.md`
- `references/state-schema.md`
- `references/session-modes.md`
- `references/curriculum-design.md`
- `references/llm-inference-curriculum.md`
- `assets/learner-state-template.yaml`
- `assets/session-log-template.md`
- `agents/openai.yaml`

如果你判断有必要，可以额外实现：

- `scripts/init_learning_state.py`

这个脚本用于初始化 `learning/<topic-slug>/` 下的状态文件和日志文件。

## 约束

- 保持 skill 可被另一实例的 agent 直接使用。
- `SKILL.md` 的 frontmatter 只保留 `name` 和 `description`。
- 内容尽量简洁，避免重复。
- 如果已有文件已经满足要求，优先增量修改，不要无意义重写。
- 如果加脚本，脚本要可运行，并给出最小验证。

## 验收标准

完成后请自行检查：

1. skill 是否体现“外置状态 + 课程图谱 + 多模式 + 会话闭环”四个核心机制。
2. `teacher` 是否可以支持长期学习而非单轮问答。
3. `LLM inference` 是否已有一个可以直接开学的默认课程图。
4. `agents/openai.yaml` 是否与 skill 内容一致。
5. 运行验证脚本，确保 skill 基本合法。

如果环境中存在类似下面的验证脚本，请运行：

```bash
python /root/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-path>
```

## 最终输出要求

完成后不要只给抽象说明。请输出：

1. 你改了哪些文件。
2. 这个 skill 的核心工作流是什么。
3. 如果用户现在要开始学 “LLM inference interview prep”，第一轮 session 会怎么跑。
4. 如果还有未实现但值得补充的部分，列出最多 3 项。
