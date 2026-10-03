---
name: delegate-grunt
description: Delegate mechanical, well-specified "grunt work" to the local `qwen` CLI instead of doing it yourself — boilerplate/scaffolding, repetitive renames across many files, docstring/comment generation, straightforward test stubs, one-off formatting or text-reorganization scripts. Use this whenever a request is repetitive, templated, or fully-specified and doesn't require judgment about this codebase's non-obvious behavior, architecture, or anything security-sensitive — even if the user doesn't say "delegate" or mention qwen by name.
---

# Delegate grunt work to qwen

`qwen` (Qwen Code) is installed locally and runs non-interactively. Use it as
a cheap worker for tasks that are tedious but not hard — so the main model's
effort goes to the parts that actually need judgment.

## When to use this

Good fit: scaffolding a new file from an existing pattern, renaming the same
symbol across many files, writing docstrings/comments, generating a
straightforward test stub, a one-off script to reformat/reorganize text,
anything you could hand to a competent junior dev with a precise spec.

Not a fit: anything needing judgment about *why* this codebase behaves the
way it does, architectural decisions, security-sensitive code, destructive
operations, or multi-step reasoning that depends on context qwen doesn't
have. If you're not sure the task is fully specified, do it yourself instead
— a wrong delegation costs more review time than it saves.

## First use: sanity-check it

Before relying on `qwen` for anything real, confirm it's actually working:

```bash
qwen -p "reply with just the word OK"
```

If this errors out (auth, missing model, etc.) or doesn't respond sensibly,
don't delegate — just do the task yourself and mention the CLI looks broken.

## How to delegate

1. Write a **self-contained prompt**. `qwen` runs in its own process with no
   memory of this conversation, so the prompt must carry everything it
   needs: exact file paths, the relevant existing code/pattern to follow,
   and the precise change wanted. Vague prompts produce vague — or wrong —
   output.
2. Run it with `--approval-mode auto-edit`. Without it, qwen's default
   approval mode requires interactive confirmation for file edits — which
   there's no one to give in non-interactive `-p` mode, so every edit gets
   silently denied and qwen just *describes* the change instead of making
   it. `auto-edit` auto-approves file writes but still asks for shell
   commands, which is the right scope for grunt work (don't reach for
   `--yolo` — that also auto-approves shell commands, more than this needs):
   ```bash
   qwen --approval-mode auto-edit -p "<self-contained prompt>"
   ```
   Give it a reasonable timeout; grunt work shouldn't need more than a
   couple of minutes.
3. **Always review the result yourself** before treating it as done — read
   any file it changed, check the diff makes sense, run it if it's code.
   Treat qwen's output the same way you'd treat a first draft from someone
   you haven't worked with before: likely fine, but unverified until you've
   looked.
4. If it errors, times out, or the output is clearly wrong or incomplete,
   don't retry blindly — just do the task yourself. The point is to save
   effort on the easy cases, not to fight a tool on the hard ones.

## Why this exists

The main model is relatively expensive to run for mechanical work it could
hand off. Routing well-specified, low-risk tasks to a local CLI frees that
effort for the parts of the task that actually need understanding of this
codebase.
