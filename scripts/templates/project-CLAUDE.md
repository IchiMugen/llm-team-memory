# {{PROJECT_NAME}} — Project Contract
> Inherits from: {{VAULT_PATH}}/CLAUDE.md (read that first)

## What this project is
{{PROJECT_DESC}}

## Stack
- Language:
- Framework:
- Key dependencies:

## Vault reference
- Context: `{{VAULT_PATH}}/wiki/projects/{{PROJECT_SLUG}}/context.md`
- Decisions: `{{VAULT_PATH}}/wiki/decisions/` (filter by #{{PROJECT_SLUG}})
- Tasks: `{{VAULT_PATH}}/wiki/tasks.md` (filter by #{{PROJECT_SLUG}})

## Project-specific rules
<!-- Override or extend master contract rules here -->

## Architecture notes
<!-- Key patterns, constraints, non-obvious decisions -->

## Resume trigger
`"Read CLAUDE.md then continue"` →
1. Read `{{VAULT_PATH}}/CLAUDE.md`
2. Read this file
3. Read `{{VAULT_PATH}}/wiki/projects/{{PROJECT_SLUG}}/context.md`
4. Read `{{VAULT_PATH}}/wiki/tasks.md` (filter #{{PROJECT_SLUG}})
5. Continue
