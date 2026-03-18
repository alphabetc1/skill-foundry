# Launch Checklist

Use this file as the minimum launch playbook for Forge.

## Before You Post

- Create a `v0.1.0` tag and GitHub release using `docs/releases/v0.1.0.md`
- Add GitHub topics such as `codex`, `claude`, `ai-coding`, `developer-tools`, `agent-workflow`, and `prompt-engineering`
- Upload a social preview image that shows the five-stage flow
- Enable GitHub Discussions so user questions and success stories have a home
- Pin one issue or discussion that asks for real-world examples and feedback
- Verify the example folders in `examples/` render well on GitHub

## Distribution Order

1. Publish the GitHub release
2. Post the launch thread on X and LinkedIn
3. Share the repo in relevant Reddit, Hacker News, and Discord communities
4. Submit the repo to community lists such as awesome agent or Claude directories
5. Follow up with one short post per example from `examples/`

## Positioning

Lead with the problem, not the implementation:

- AI coding often jumps into code before the task is clear
- Forge forces prompt, research, plan, build, and review into explicit artifacts
- Every stage is resumable and git-backed
- Stage 5 blocks completion until review says no blocking issues remain

## English Launch Post

```text
Forge is a staged skill for Codex and Claude that turns a fuzzy coding request into shipped, reviewed code.

Flow:
prompt.md -> research.md -> plan.md -> build -> review.md

Why I built it:
- AI coding agents often skip clarification and planning
- repo research disappears inside chat history
- review is easy to forget

What Forge does:
- runs end to end by default unless you ask it to stop after a stage
- stores each stage in files you can review
- keeps the workflow resumable and revertable with git
- ends with a blocking-issue review loop

Repo:
https://github.com/alphabetc1/skill-foundry/tree/main/skills/forge
```

## Chinese Launch Post

```text
我做了一个给 Codex 和 Claude 用的 staged workflow skill: Forge。

它解决的问题很直接:
- AI coding 很容易在需求还没澄清时就开始写代码
- 调研过程经常散落在聊天记录里
- review 往往不是默认动作

Forge 会把任务强制推进成这 5 个阶段:
prompt.md -> research.md -> plan.md -> build -> review.md

特点:
- 默认一次调用直接跑到完成，除非你明确要求停在某个阶段
- 每个阶段都落到文件里，便于 review
- 每个阶段都可以继续和回退
- 最后必须经过 blocking issue review loop

仓库:
https://github.com/alphabetc1/skill-foundry/tree/main/skills/forge
```

## Follow-Up Post Ideas

- Post one screenshot or copyable snippet from each example folder
- Compare a raw user request with the resulting `prompt.md`
- Show the exact git commit sequence created by a full run
- Share one blocking issue that stage 5 caught before release

## Metrics To Watch

- README views to clone ratio
- Clone to install ratio
- Open issues or discussions asking how to adapt Forge
- Traffic from community directories versus direct social posts
