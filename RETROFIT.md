# Retrofitting an existing repository

> **Companion to `CLAUDE.md`.** This file describes the *brownfield* path —
> you already have a working codebase and want to add an agent product team
> architecture *around* it, without restructuring source code or overwriting
> existing conventions. The default procedure in `CLAUDE.md` is *greenfield*;
> follow this one instead whenever the repo already has meaningful content.

---

## When to use this doc

Use the brownfield procedure when any of the following is true of the
working directory:

- Has source code under `src/`, `app/`, `lib/`, language-specific roots
  (`cmd/`, `internal/`, `apps/`, etc.) or otherwise.
- Has a manifest (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`,
  `Gemfile`, `composer.json`, `pom.xml`, `build.gradle`, etc.).
- Has existing CI under `.github/workflows/`, `.gitlab-ci.yml`, `circle.yml`,
  `azure-pipelines.yml`, etc.
- Has a non-trivial git history (more than a handful of commits by real
  authors, not just template setup).
- Has its own `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md` with project-specific
  instructions already written.

If **none** of those are true, fall back to the greenfield procedure in
`CLAUDE.md`.

---

## Prerequisites

1. **Preserve any existing agent-instruction files.** If the repo already
   contains a `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`, do *not* overwrite
   it. Instead, append the bootstrapper content to the existing file as a
   clearly labeled section, or rename the incoming bootstrapper to
   `BOOTSTRAP_ROLES.md` and reference it from the existing agent-instruction
   file.
2. **Start from a clean working tree.** Commit or stash local changes before
   running the retrofit so the diff is reviewable in isolation.
3. **Confirm the Role Catalogue is reachable.** This file references the
   *Role Catalogue*, *Constraints*, *Per-role template*, and *Fallback
   pattern* sections of `CLAUDE.md`. Either keep `CLAUDE.md` at the project
   root as a companion, or copy those four sections into whichever
   agent-instruction file you kept.

---

## Brownfield Bootstrapping Procedure

Perform these steps in order. Do **not** fall through to the greenfield
procedure — it assumes an empty directory and will propose folder renames
that break your build.

### Step B1 — Confirm you are in brownfield mode

Check the *When to use this doc* triggers above. If at least one applies,
proceed. Otherwise, stop and hand back to `CLAUDE.md`'s greenfield flow.

### Step B2 — Survey the repository

Before generating anything, build a factual picture of the repo. Gather:

- **Languages and frameworks.** Read every root-level manifest. Note primary
  runtime versions, major dependencies, and any polyglot surfaces (e.g.,
  Python backend + TypeScript frontend + Go worker).
- **Entrypoints.** Identify the server, CLI, worker, and job entrypoints so
  the Backend / DevOps roles know what they own.
- **Surfaces.** Is there a web frontend? Mobile app? Public API? Internal
  CLI? Each surface maps to a role-inclusion decision.
- **Data layer.** Detect database engines (Postgres / MySQL / SQLite / DynamoDB
  / BigQuery / Snowflake), migration tool, ORM, and any ETL directories.
- **Tests and quality gates.** Test framework, formatter, linter, type
  checker, coverage floor, mutation testing — all from config files, not
  guesses.
- **CI / CD and infra.** Workflow files, deploy scripts, IaC directories
  (`terraform/`, `pulumi/`, `infra/`, `deploy/`), k8s manifests, Dockerfiles.
- **Observability.** Sentry / Datadog / Grafana integrations, log shippers,
  metric libraries.
- **Existing docs.** `README.md`, `ARCHITECTURE.md`, `CONTRIBUTING.md`, ADRs
  under `docs/adr/` or `doc/architecture/decisions/`, runbooks, postmortems.
- **Activity shape.** `git log --pretty=format:"%an" --since=90.days.ago |
  sort -u` to see recent authors; `git log --stat --since=90.days.ago` to see
  which directories are hot. This tells you where the team currently spends
  effort — good context for the PM system prompt.
- **Existing agent-instruction content.** Anything useful in `CLAUDE.md`,
  `AGENTS.md`, `GEMINI.md`, `.cursorrules`, `.github/copilot-instructions.md`
  — inherit constraints from these, don't reinvent them.

Capture the survey as a temporary scratch pad in your head or in a file at
`.retrofit-survey.md` (delete before finishing). Do **not** commit the
survey — it becomes the input to Step B3, not a permanent artifact.

### Step B3 — Draft `project_description.md` from evidence

Instead of asking the user to fill in a blank stub, write
`project_description.md` from what the repo shows you. Rules:

- **Cite evidence.** Every claim in the brief should be attributable to a
  file you read. Example: *"Backend: Python 3.12 (FastAPI — see
  `pyproject.toml`, `app/main.py`)."*
- **Separate inferred from confirmed.** Use a trailing `(inferred)` tag on
  anything you guessed from indirect signals (e.g., compliance posture
  inferred from auth library choice).
- **Leave the user room to correct.** Put a section at the bottom called
  *Assumptions needing confirmation* listing every inferred item. This is
  the brownfield equivalent of *Open questions*.
- **Do not invent primary users.** If the repo doesn't reveal who uses the
  product, say so explicitly and ask. Don't stereotype from the domain.

Write the file, then **pause and present it to the user** for review. Do
not proceed to Step B4 until the user confirms or edits the brief. The
greenfield procedure skips this checkpoint because there's nothing to
reconcile; brownfield cannot.

### Step B4 — Produce `design-doc.md` with integration boundaries

Use the same shape as the greenfield Step 2 design doc, with two additions:

1. **Existing architecture.** A section near the top that diagrams what the
   repo already contains (entrypoints, services, data stores, queues, infra)
   based on the Step B2 survey. Use ASCII or Mermaid. Keep it to one page.
2. **Integration boundaries.** A section explicitly stating what the agent
   team will and will not touch:
   - *Will add:* `agents/`, `design-doc.md`, `docs/adr/`, `docs/runbooks/`,
     `docs/postmortems/`, `docs/decisions/` (only if these don't exist).
   - *Will not touch:* source directories, build scripts, CI config,
     existing documentation, manifest files, the existing agent-instruction
     file. Any change to those requires a human-approved follow-up commit.

The role roster in the design doc must be justified by survey evidence:
"Frontend Engineer: yes — `web/` is a Next.js app with 38k LoC. Mobile
Engineer: no — no iOS/Android surface detected. ML Engineer: yes —
`ml/training/` contains an active training pipeline."

### Step B5 — Create additive structure only

Create only these new paths at the repo root (skipping any that already
exist):

```
<repo-root>/
├── design-doc.md                  ← new
├── project_description.md         ← new (drafted in Step B3)
├── agents/
│   ├── README.md                  ← new
│   ├── 00-product-manager/CLAUDE.md
│   ├── 01-product-designer/CLAUDE.md   (if role is in the roster)
│   ├── 02-tech-lead/CLAUDE.md
│   ├── 03-backend-engineer/CLAUDE.md
│   ├── 04-frontend-engineer/CLAUDE.md  (only if there is a frontend surface)
│   ├── 05-qa-engineer/CLAUDE.md
│   └── 06-devops-sre/CLAUDE.md
└── docs/                          ← only create subdirs that don't exist yet
    ├── adr/
    ├── runbooks/
    ├── decisions/
    └── postmortems/
```

**Do not:**

- Rename existing folders or files.
- Move source code into an `src/` (or any other) layout for consistency.
- Add root-level dependency manifests, lockfiles, or lint configs.
- Delete or rewrite existing documentation.
- Overwrite an existing `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` (see
  Prerequisites).

If the repo already has `docs/adr/` with content, leave it alone — agents
will simply append new ADRs.

### Step B6 — Populate each role's `CLAUDE.md` with repo-specific wiring

Use the *Per-role `CLAUDE.md` template* from `CLAUDE.md`. Each role file
must additionally:

- **List the real paths the role owns in this repo.** Not `src/` defaults —
  the actual paths you found in Step B2. Example for a Python backend:
  *"Owns `app/api/`, `app/services/`, `app/models/`, `migrations/`, and
  backend tests under `tests/unit/` and `tests/integration/`."*
- **Honor existing conventions.** The system prompt should enumerate the
  repo's linter, formatter, test framework, type checker, and commit-message
  style as non-negotiables. Pull these from the actual config files, not
  from role defaults.
- **Point at the right read-at-start docs.** Replace any generic "read the
  README" instruction with the exact set of files that orient someone new
  to the repo: `README.md`, `ARCHITECTURE.md`, `CONTRIBUTING.md`, top three
  or four ADRs, plus any role-relevant runbook. Agents should read all of
  these on session start before taking action.
- **Respect existing agent-instruction content.** If the repo's original
  `CLAUDE.md` or `AGENTS.md` states preferences ("don't use ORM helpers",
  "prefer functional components", "never bypass hooks"), include those
  verbatim in the role system prompts where relevant.

### Step B7 — Reconcile with CI and ownership

- If the repo has a `CODEOWNERS` file, include its contents verbatim as a
  *"Do not bypass these owners"* note in the PM's system prompt. Agents
  should never self-merge across a CODEOWNERS boundary.
- If the repo has required CI checks (branch-protection rules, required
  workflows), note them in the DevOps/SRE role as gates agents must
  respect before claiming work is complete.
- If there is an existing test target (`make test`, `pnpm test`, `pytest`,
  `go test ./...`), wire it into the QA agent's *Success signals* so
  verification matches what humans do locally.

### Step B8 — Summarize with integration caveats

Return a summary that includes:

- The files created (paths only — do not inline their contents).
- The roles included and excluded, with one-line justifications from the
  survey.
- *Assumptions needing confirmation* from the drafted
  `project_description.md` so the user can correct them.
- *What the team cannot do yet* — any existing codebase conventions that
  still need a human decision (e.g., "No decision logged yet on where new
  services should live; the Tech Lead agent will flag this on first use").
- The one-level-delegation and skill-budget constraints inherited from
  `CLAUDE.md`.

---

## Things you must not do in brownfield mode

A short list, called out because these mistakes are cheap to make and
expensive to undo:

1. **Do not** rename or move existing source folders.
2. **Do not** rewrite source code to match role defaults (e.g., don't
   impose an `src/` layout, don't change the ORM, don't reformat files).
3. **Do not** overwrite the repo's existing `CLAUDE.md` / `AGENTS.md` /
   `GEMINI.md`. Append or reference, never replace.
4. **Do not** add root-level dependencies. The agents live above the source,
   not inside it.
5. **Do not** delete or edit existing ADRs, runbooks, or architectural docs.
   Agents can add new documents alongside them.
6. **Do not** guess unknown answers. Every inferred claim in
   `project_description.md` must carry an *(inferred)* tag and reappear in
   *Assumptions needing confirmation*.
7. **Do not** skip Step B3's user-review checkpoint. Brownfield retrofits
   must be confirmed against the actual team's understanding before the
   team gets generated.

---

## What this shares with the greenfield path

The following sections in `CLAUDE.md` apply to brownfield retrofits
unchanged:

- **Role Catalogue** (defaults per role: model, owns, system prompt core,
  tools, MCPs, skills, metadata).
- **Constraints you must respect** (one-level delegation, 20-skill cap,
  shared filesystem / isolated threads, model support, beta header,
  research-preview `callable_agents`).
- **Per-role `CLAUDE.md` template** (section structure each role file
  follows).
- **Orchestrator-specific additions** (PM `callable_agents`, delegation
  rubric, decision log).
- **`agents/README.md` skeleton** (instantiation guide).
- **Fallback — flat pattern without `callable_agents`**.

This file only replaces Steps 1–3 of the greenfield Bootstrapping
Procedure — inputs, design-doc, folder structure — with the brownfield-safe
Steps B1–B5 above. Steps B6–B8 are analogs of the greenfield Steps 4–6,
tightened to cite repo evidence and not to touch existing state.

---

## If the user invokes this procedure explicitly

Users will typically trigger brownfield mode with a prompt like:

- "Retrofit this repo with the agent team architecture."
- "Apply `RETROFIT.md` to the current directory."
- "Run the brownfield bootstrap."

When invoked, confirm the retrofit trigger in one sentence, then begin at
Step B1. Do not ask for permission at every sub-step — ask only at the Step
B3 checkpoint (the drafted `project_description.md`) and at the final Step
B8 summary. Brownfield retrofits that pause on every file become unusable.
