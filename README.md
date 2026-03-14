# Forge

Turn a fuzzy coding request into shipped, reviewed code.

`prompt.md -> research.md -> plan.md -> build -> review.md`

Forge is a staged skill for Codex and Claude. Invoke it explicitly with `$forge` or `/forge` when you want this workflow; it should not auto-trigger just because a task looks like a fit. It pushes a non-trivial coding task through a git-backed workflow that runs end to end by default while staying easy to review, resume, and revert.

## Why Forge

| Common failure mode with AI coding | What Forge changes |
| --- | --- |
| The agent starts coding before the task is clear | Stage 1 rewrites the request into `prompt.md` before any implementation |
| Research disappears inside chat history | Stage 2 stores repository findings in `research.md` |
| Plans are vague or skipped | Stage 3 produces an implementation-ready `plan.md` |
| Rework is hard after requirements change | Each stage is resumable and downstream commits can be reverted safely |
| Review happens only if the user remembers to ask | Stage 5 forces a blocking-issue review loop before the task is done |

## Who It Is For

- Developers shipping non-trivial changes with Codex or Claude
- Teams that want reviewable artifacts before implementation
- Repositories where resumable artifacts and reviewable stage commits matter

## Not For

- One-line edits where a staged workflow would be overkill
- Repositories without git history
- Users who want the agent to freestyle instead of following an explicit process

## 30-Second Demo

1. Install the skill.
2. Start with a plain-language task.
3. Resume by mentioning a stage file only when you need to restart from the middle.
4. Ask it to stop after a stage only when you want an intermediate checkpoint.

```text
Codex  : $forge Add CSV and JSON export for invoices
Codex  : $forge Continue from research.md
Codex  : $forge Continue from research.md but stop after plan.md
```

You end up with:

- `prompt.md`
- `research.md`
- `plan.md`
- implementation changes
- `review.md`
- one git commit per stage

## Example Workflows

These examples make the workflow easy to share in docs, release notes, and social posts.

| Example | What it shows | Folder |
| --- | --- | --- |
| New export feature | A product-facing feature request that becomes an implementation plan | [`examples/new-export-feature`](examples/new-export-feature) |
| Auth refactor | A risky internal change that benefits from staged research and review | [`examples/auth-refactor`](examples/auth-refactor) |
| Webhook bugfix | A debugging task that still needs structure and a final review loop | [`examples/payment-webhook-bugfix`](examples/payment-webhook-bugfix) |

## Architecture

```mermaid
flowchart LR
    user([User request]) --> s1["1 Prompt<br/>prompt.md"]
    s1 --> s2["2 Research<br/>research.md"]
    s2 --> s3["3 Plan<br/>plan.md"]
    s3 --> s4["4 Build<br/>implementation"]
    s4 --> s5["5 Review<br/>review.md"]

    s5 --> gate{Blocking issues?}
    gate -->|Yes| fix["Fix"]
    fix --> s5
    gate -->|No| done([Done])

    shared["Every stage:<br/>resume + revert"]
    shared -.-> s1
    shared -.-> s2
    shared -.-> s3
    shared -.-> s4
    shared -.-> s5

    classDef stage fill:#FFF4E5,stroke:#D97706,color:#7C2D12,stroke-width:1.5px;
    classDef decision fill:#FEF2F2,stroke:#DC2626,color:#991B1B,stroke-width:1.5px;
    classDef action fill:#F5F3FF,stroke:#7C3AED,color:#5B21B6,stroke-width:1.5px;
    classDef note fill:#EFF6FF,stroke:#2563EB,color:#1E3A8A,stroke-width:1.5px;
    classDef done fill:#ECFDF3,stroke:#16A34A,color:#166534,stroke-width:1.5px;

    class s1,s2,s3,s4,s5 stage;
    class gate decision;
    class fix action;
    class shared note;
    class done done;
```

Quick read:

- No stage file mentioned means start at stage 1 and continue through `review.md` by default.
- Mention `prompt.md`, `research.md`, `plan.md`, or `review.md` to resume from that starting point.
- Ask to stop after a specific stage only when you want an intermediate checkpoint.
- Every stage supports revert before continuing.
- Stage 5 is the only self-loop.

## Install

### macOS / Linux

```bash
./install.sh both
```

### Windows PowerShell

```powershell
./install.ps1 -Target both
```

Install only one tool if needed:

```bash
./install.sh codex
./install.sh claude
./install.sh claude --scope project --project-dir /path/to/repo
```

By default the installer copies the skill into:

- Codex: `${CODEX_HOME:-~/.codex}/skills/forge`
- Claude personal: `~/.claude/skills/forge`
- Claude project: `<repo>/.claude/skills/forge`

Use `--mode link` or `-Mode link` if you want a live symlink during development.

## Use

Start a new session after installing.

Forge is intended for explicit invocation only. Do not rely on the agent inferring Forge from the task shape alone.

```text
Codex  : $forge 帮我实现一个新的导出功能
Claude : /forge 帮我实现一个新的导出功能
```

## Stages

| Stage | Trigger | Output |
| --- | --- | --- |
| 1 | no stage file mentioned | `prompt.md` |
| 2 | mention `prompt.md` | `research.md` |
| 3 | mention `research.md` | `plan.md` |
| 4 | mention `plan.md` | implementation |
| 5 | mention `review.md` | `review.md` plus fixes for blocking issues |

These triggers select the starting stage. Forge continues into later stages by default unless the user explicitly asks it to stop early.

Rules that matter:

- Mentioning the file name explicitly selects the starting stage for resume.
- If you do not add another constraint, Forge continues from that starting stage through stage 5 in one invocation.
- Ask to stop after `prompt.md`, `research.md`, `plan.md`, or implementation only when you want an intermediate pause.
- Stages 1-3 only write docs. No implementation before stage 4.
- Stage 5 loops inside one session until `review.md` says no blocking issues remain.
- Each stage ends with its own git commit.

## Resume Examples

```text
$forge 帮我设计一个新的权限系统
$forge 请基于 prompt.md 继续到结束
$forge 请基于 research.md 继续，但只生成 plan.md
$forge 请基于 plan.md 继续实现并 review 到完成
```

## Promotion Assets

- [`examples/`](examples) contains shareable case studies you can link in posts and release notes.
- [`docs/launch.md`](docs/launch.md) contains a launch checklist plus English and Chinese post copy.
- [`docs/releases/v0.1.0.md`](docs/releases/v0.1.0.md) contains a first release draft you can paste into GitHub Releases.

## Included

- `SKILL.md` - the Forge workflow itself
- `scripts/revert_stage_commits.py` - revert downstream stage commits safely
- `agents/openai.yaml` - Codex skill metadata

## License

Apache-2.0
