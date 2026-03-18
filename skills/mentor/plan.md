# 问题背景

当前任务是在空白仓库中实现一个可长期复用的 `mentor` skill。这个 skill 不是单次教学 prompt，而是一个跨会话、可持续跟踪学习状态的教学工作流。它需要把学习信息外置到文件系统，用课程图谱而不是平面清单组织内容，用多种 session mode 适配不同学习阶段，并在每次 substantive session 后形成可追踪闭环。

# 当前状态

- 仓库当前已有：
  - [prompt.md](/root/code/tools/skills/agent-skills/skills/mentor/prompt.md)
  - [research.md](/root/code/tools/skills/agent-skills/skills/mentor/research.md)
- 仓库当前缺失：
  - `SKILL.md`
  - `references/`
  - `assets/`
  - `agents/openai.yaml`
  - `scripts/init_learning_state.py`
- 已经处理了一个历史上的旧 `stage2` 提交，并补了等价 revert commit，当前可以从 `prompt.md` 干净继续。

# 需求

- `SKILL.md` frontmatter 只保留 `name` 和 `description`。
- skill 必须体现四个核心机制：
  - 外置学习状态
  - 课程图谱
  - 多模式教学
  - 会话闭环
- 必须提供这些文件：
  - `SKILL.md`
  - `references/state-schema.md`
  - `references/session-modes.md`
  - `references/curriculum-design.md`
  - `references/llm-inference-curriculum.md`
  - `assets/learner-state-template.yaml`
  - `assets/session-log-template.md`
  - `agents/openai.yaml`
- 需要 `LLM inference` 的默认课程图，可直接用于面试准备。
- `agents/openai.yaml` 必须与 skill 内容一致，且 `default_prompt` 显式提到 `$mentor`。
- 若加入初始化脚本，需要可运行并做最小验证。

# 选定方案

采用“精简 `SKILL.md` + 参考文档 + 模板资产 + 初始化脚本”的结构。

选择原因：

- `SKILL.md` 只保留触发规则、工作流和引用导航，符合 skill-creator 的上下文节制原则。
- 详细规则落到 `references/`，便于按需加载，不把所有模式和 schema 一次性塞进上下文。
- 模板和初始化脚本让“外置状态”从概念变为可执行约定，减少 agent 手工复制粘贴。

# 计划中的文件与改动

## 1. `SKILL.md`

写一个简洁入口文档，包含：

- frontmatter：
  - `name: mentor`
  - `description: ...`
- 触发场景：
  - 系统化学习
  - 面试准备
  - 多轮跟踪学习状态
- 启动流程：
  - 首次使用时检查 `learning/<topic-slug>/`
  - 不存在则引导或直接使用脚本初始化
  - 读取 `learner-state.yaml` 和最近的 `session-log.md`
- 固定 session 闭环：
  1. 读取状态
  2. 判断 mode
  3. 从课程图选当前模块
  4. 执行教学/诊断/测验
  5. 更新状态与日志
  6. 输出唯一下一步动作
- 明确引用：
  - 状态 schema 看 `references/state-schema.md`
  - 模式规则看 `references/session-modes.md`
  - 图谱设计看 `references/curriculum-design.md`
  - LLM inference 默认课程图看 `references/llm-inference-curriculum.md`
- 写入规则：
  - 不能因为“刚解释过”就标记 mastered
  - mastered 必须有可验证表现证据
  - 错误回答写入 misconception 或 shaky topic

## 2. `references/state-schema.md`

定义学习状态文件的结构和更新原则：

- 顶层字段：
  - `topic`
  - `goal`
  - `deadline`
  - `background`
  - `current_module`
  - `mastered`
  - `shaky`
  - `prerequisite_gaps`
  - `misconceptions`
  - `review_queue`
  - `recent_session_evidence`
  - `next_action`
- 每个字段的意义、填写约束、更新时机
- 明确证据要求：
  - 复述
  - 对比
  - 推导
  - 应用
- 明确 `next_action` 只能保留一个最高优先级动作

## 3. `references/session-modes.md`

为 6 个 mode 分别定义：

- 使用条件
- 适用输入信号
- 输出结构
- 何时切换到别的 mode

具体包括：

- `map`：建立全景图，收尾必须给推荐下一课
- `teach`：讲解单一模块，强调概念边界和 tradeoff
- `diagnose`：先用少量探测题判断真实水平
- `drill`：一题一题进行面试问答，不一次给全答案
- `recall`：围绕 `review_queue` 做主动回忆
- `plan`：根据当前状态输出阶段性学习计划

## 4. `references/curriculum-design.md`

定义 curriculum graph 的统一格式和选择规则：

- 每个模块的必备字段：
  - 模块名称
  - 为什么重要
  - 前置依赖
  - must-know points
  - interview signals
  - exit criteria
- 图中的边表示前置依赖，不是时间线
- 当前模块选择规则：
  - 若存在严重前置缺口，先补缺口
  - 若当前模块未满足 exit criteria，保持在该模块
  - 若已满足且 review_queue 紧急度低，才推进到后继模块

## 5. `references/llm-inference-curriculum.md`

实现一个可直接开学的默认课程图，至少覆盖：

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

每个模块都按统一 schema 填写，并补一段推荐学习顺序说明，解释为什么虽然是图但仍有默认启动路径。

## 6. `assets/learner-state-template.yaml`

提供 YAML 模板，字段与 state schema 对齐，并附最小示例占位值，方便脚本初始化后直接可编辑。

## 7. `assets/session-log-template.md`

提供单次 substantive session 的 Markdown 模板，至少包含：

- session metadata
- chosen mode
- current module
- evidence observed
- misconceptions/shaky points
- state updates
- next action

## 8. `scripts/init_learning_state.py`

实现一个最小但可复用的初始化脚本：

- 输入参数：
  - `--topic` 必填
  - `--slug` 可选，默认由 `topic` 生成
  - `--goal` 可选
  - `--deadline` 可选
  - `--background` 可选
  - `--base-dir` 可选，默认当前仓库根目录
  - `--force` 可选，允许覆盖已有文件
- 行为：
  - 创建 `learning/<topic-slug>/`
  - 从 `assets/` 模板生成 `learner-state.yaml` 和 `session-log.md`
  - 用传入参数填充模板中的基础字段
- 约束：
  - 默认不覆盖已有文件
  - slug 只使用小写字母、数字和连字符

## 9. `agents/openai.yaml`

生成 UI 元数据，字段至少包含：

- `display_name`
- `short_description`
- `default_prompt`

计划使用 `generate_openai_yaml.py` 生成，避免格式偏差。候选值：

- `display_name`: `Mentor`
- `short_description`: `Structured learning and interview prep workflows`
- `default_prompt`: `Use $mentor to run a stateful LLM inference interview prep session.`

# 边界情况与迁移考虑

- 首次会话没有学习状态文件时，skill 必须明确初始化，而不是假装已有上下文。
- 如果用户只说“继续上次内容”，skill 仍要先读状态文件，再决定模式和当前模块。
- `mastered`、`shaky`、`misconceptions` 不能互相混淆，尤其不能把“听懂了”直接记成 mastered。
- `review_queue` 应服务于遗忘控制，不能沦为重复的待办列表。
- 默认课程图是面向 `LLM inference interview prep`，但结构要允许以后扩展到其他主题。

# 验证计划

按以下顺序验证：

1. 运行 `python /root/.codex/skills/.system/skill-creator/scripts/quick_validate.py /root/code/tools/skills/agent-skills/skills/mentor`
2. 运行 `python /root/.codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py /root/code/tools/skills/agent-skills/skills/mentor --interface display_name=Mentor --interface short_description='Stateful long-term learning workflows' --interface default_prompt='Use $mentor to run a stateful long-term learning session for a repo or knowledge domain.'`
3. 运行 `python scripts/init_learning_state.py --topic 'LLM inference interview prep' --base-dir /tmp/mentor-skill-check`
4. 检查 `/tmp/mentor-skill-check/learning/llm-inference-interview-prep/` 下是否生成目标文件
5. 如验证通过，确保临时验证产物不纳入 git 提交
