# claude-codex-sync

`claude-codex-sync` 是一个在 Claude Code 与 Codex 之间做 best-effort 配置同步的 skill。

它会尽量同步这些内容：

- `CLAUDE.md` 和 `AGENTS.md`
- 用户级与仓库级的 skills
- Codex 对 `CLAUDE.md` 的 project doc fallback 配置
- 无法直接映射的平台专有配置，会转成 notes 保留下来

## 架构图

```mermaid
flowchart TD
    user["用户 / Agent"]
    entry["skill 入口<br/>$claude-codex-sync / /claude-codex-sync"]
    wrapper["scripts/claude-codex-sync.py<br/>检测当前平台并加载 CLI"]
    cli["claude-codex-sync/cli.py"]

    subgraph core["CLI Core"]
        parser["命令解析<br/>status / doctor / sync / import / export"]
        resolver["上下文解析<br/>repo_root / scope / direction"]
        planner["同步计划生成<br/>instruction / skills / config / notes"]
        validator["apply 前校验<br/>未托管目标需 --force"]
        applier["执行器<br/>backup + write_text + copy_tree"]
    end

    subgraph claude["Claude Side"]
        claude_docs["CLAUDE.md"]
        claude_cfg[".claude/settings*.json"]
        claude_rules[".claude/rules"]
        claude_skills[".claude/skills/*"]
        claude_agents[".claude/agents"]
    end

    subgraph codex["Codex Side"]
        codex_docs["AGENTS.md"]
        codex_cfg[".codex/config.toml"]
        codex_rules[".codex/rules"]
        codex_skills["~/.agents/skills/*<br/>以及 repo/.agents/skills/*"]
        codex_notes["claude-codex-sync/unsupported/*"]
    end

    user --> entry --> wrapper --> cli
    cli --> parser --> resolver --> planner
    planner --> claude_docs
    planner --> claude_cfg
    planner --> claude_rules
    planner --> claude_skills
    planner --> claude_agents
    planner --> codex_docs
    planner --> codex_cfg
    planner --> codex_rules
    planner --> codex_skills
    planner --> codex_notes
    planner --> validator --> applier

    classDef core fill:#FEF3C7,stroke:#D97706,color:#78350F,stroke-width:1.5px;
    classDef edge fill:#EFF6FF,stroke:#2563EB,color:#1E3A8A,stroke-width:1.3px;
    classDef store fill:#F8FAFC,stroke:#475569,color:#0F172A,stroke-width:1.2px;

    class entry,wrapper,cli,parser,resolver,planner,validator,applier core;
    class user edge;
    class claude_docs,claude_cfg,claude_rules,claude_skills,claude_agents,codex_docs,codex_cfg,codex_rules,codex_skills,codex_notes store;
```

## 流程图

```mermaid
flowchart TD
    start([开始]) --> invoke["调用 skill 或脚本"]
    invoke --> parse["解析子命令与参数"]
    parse --> branch{命令类型}

    branch -->|status| status["收集 Claude / Codex 快照"]
    status --> status_out["输出状态 JSON"]

    branch -->|doctor| doctor["收集快照并生成支持/不支持项报告"]
    doctor --> doctor_out["输出诊断 JSON"]

    branch -->|sync / import / export| resolve["解析 repo_root / scope / direction"]
    resolve --> collect["收集源端 instruction / skills / config / rules"]
    collect --> plan["构建 Operation 列表<br/>write_text / copy_tree / notes"]
    plan --> apply_q{是否 --apply}
    apply_q -->|否| diff["渲染 diff 计划"]
    diff --> done([结束])

    apply_q -->|是| validate["校验目标目录<br/>未托管 skill 需 --force"]
    validate --> backup["创建 backup_root 并备份已有目标"]
    backup --> write["执行写入与目录复制"]
    write --> summary["输出 apply 结果摘要"]
    summary --> done

    classDef action fill:#FEF3C7,stroke:#D97706,color:#78350F,stroke-width:1.5px;
    classDef output fill:#ECFDF3,stroke:#16A34A,color:#166534,stroke-width:1.5px;

    class invoke,parse,resolve,collect,plan,validate,backup,write action;
    class status_out,doctor_out,diff,summary,done output;
```

## 安装

在本仓库根目录执行：

```bash
./install.sh claude-codex-sync
./install.sh claude-codex-sync both --mode link
```

如果只想安装到 Claude 或只安装到 Codex：

```bash
./install.sh claude-codex-sync claude --scope project --project-dir /path/to/repo
./install.sh claude-codex-sync codex
```

## 使用

推荐先看 diff，再决定是否 apply：

```bash
python3 skills/claude-codex-sync/scripts/claude-codex-sync.py sync --from claude --to codex --scope all
python3 skills/claude-codex-sync/scripts/claude-codex-sync.py sync --from claude --to codex --scope all --apply
```

其他常用命令：

```bash
python3 skills/claude-codex-sync/scripts/claude-codex-sync.py sync --from codex --to claude --scope all
python3 skills/claude-codex-sync/scripts/claude-codex-sync.py status --scope all
python3 skills/claude-codex-sync/scripts/claude-codex-sync.py doctor --scope all
```
