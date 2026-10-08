# Free AI Coding Agent Rules Starter Pack

Production-oriented starter rules for **Claude Code, Cursor, Codex, Gemini CLI and other coding agents**.

Included:
- `AGENTS.md` — repository-wide engineering guardrails
- `CLAUDE.md` — Claude Code adapter
- `cursor-security.mdc` — Cursor security rule
- `task-spec.md` — task definition template
- `review-this-diff.md` — production review prompt

## Install

### Claude Code / Codex / Gemini CLI

Copy the universal file into your project root:

```bash
curl -L https://raw.githubusercontent.com/lcaladoferreira/lcaladoferreira/main/agent-rules-free/AGENTS.md -o AGENTS.md
```

For Claude Code you can also add:

```bash
curl -L https://raw.githubusercontent.com/lcaladoferreira/lcaladoferreira/main/agent-rules-free/CLAUDE.md -o CLAUDE.md
```

### Cursor

```bash
mkdir -p .cursor/rules
curl -L https://raw.githubusercontent.com/lcaladoferreira/lcaladoferreira/main/agent-rules-free/cursor-security.mdc -o .cursor/rules/security.mdc
```

## What the rules enforce

- smallest-correct-change discipline
- repository-first context gathering instead of guessing
- no unrelated refactors
- explicit verification loops
- secret and credential protection
- destructive-action approval
- MCP/tool output treated as untrusted input
- failure-path testing

## Complete pack

The paid **AI Coding Agent Rules Pack** contains 38 Markdown/MDC/YAML files covering:

- MCP/tool safety
- database migrations
- rollback and release rules
- observability
- TypeScript, Python, Next.js, FastAPI, Docker, Terraform and data engineering
- incident, migration, feature and bugfix templates
- security review and production debugging prompts

**Complete 38-file pack — US$9:**  
https://shop.leandrocaladoferreira.com/?utm_source=github&utm_medium=starter&utm_campaign=agent-rules

## License

The free starter files in this directory are MIT licensed.
