# CLAUDE.md — Agent Product Team Bootstrapper

> **What this file is:** a bootstrapper for Claude. When Claude is run in a directory containing this file and a `project_description.md`, Claude will read the project description and generate a complete multi-agent development team: a design doc, a folder structure, and one sub-`CLAUDE.md` per role, each ready to be instantiated as a Claude Managed Agent.
>
> The team is modeled on Marty Cagan's **empowered product team** (PM + Designer + Engineers) with DevOps practices ("you build it, you run it") baked in. The top of the team is a Product Manager orchestrator; all specialists are reachable from it via `callable_agents`.

---

## How to use this file

Place this `CLAUDE.md` at the root of a new or existing project directory. Create a sibling file named `project_description.md` containing, at minimum:

- What the product does (one paragraph)
- Primary users / customer
- Tech stack constraints (languages, cloud, frameworks — or "open")
- Compliance / regulatory constraints (SOC 2, HIPAA, PCI, GDPR, or none)
- Anticipated scale (internal tool, MVP, production SaaS, etc.)

Then invoke Claude in that directory. Claude will perform the **Bootstrapping Procedure** below.

---

## Bootstrapping Procedure (instructions for Claude)

When you, Claude, are run in a directory containing this `CLAUDE.md` and a `project_description.md`, perform the following steps **in order**. Do not skip steps. Do not ask clarifying questions unless `project_description.md` is missing or blank.

### Step 0 — Pick the right mode (greenfield vs brownfield)

Before Step 1, decide which flow to run:

- **Brownfield** — the working directory already contains a meaningful codebase. Signals include any of: a language manifest (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `Gemfile`, `composer.json`, `pom.xml`, `build.gradle`, etc.), source directories (`src/`, `app/`, `lib/`, `cmd/`, `internal/`, `apps/`, …), CI under `.github/workflows/` or similar, a non-trivial git log, or a pre-existing `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` with project instructions. If `RETROFIT.md` exists at the project root, read it now and follow the **Brownfield Bootstrapping Procedure** defined there instead of the steps below. Do not fall through to greenfield.
- **Greenfield** — the directory is empty (or contains only this `CLAUDE.md`, a stub `project_description.md`, and maybe `examples/` / `README.md` / `HACKING.md` / `.claude/`). In that case, proceed with Step 1 below.

If it's ambiguous, prefer brownfield: a retrofit is additive and safe; a greenfield run will propose folder structure that can silently clash with an existing layout. When the user explicitly says "retrofit", "add the agent team to this existing repo", or references `RETROFIT.md` by name, always run brownfield regardless of other signals.

### Step 1 — Read inputs

1. Read `project_description.md` in full.
2. Read this `CLAUDE.md` in full.
3. If `examples/` exists at the project root, list it and open any files that look like reference output (e.g., `examples/project_description.md`, `examples/agents/**/CLAUDE.md`). Use them as a calibration for the depth, tone, and structure of what you produce — not as content to copy.
4. Gate check — do not proceed past this step unless the user's `project_description.md` has been filled in:
   - If the file is missing, create a stub asking the user to fill it in and stop.
   - If the file exists but still contains the placeholder tokens from the stub (any `<...>` angle-bracket instructions, or the "Claude is waiting on you" header), treat it as not-yet-filled-in. Do not invent content. Tell the user which sections are unfilled and stop.
   - Only once every required section has real content should you continue to Step 2.

### Step 2 — Produce `design-doc.md`

Create a file named `design-doc.md` at the project root containing:

1. **Project summary** (1 paragraph) — your restatement of `project_description.md` in your own words.
2. **Team diagram** — an ASCII diagram matching the shape in the *Reference Architecture* section below, with concrete role names filled in for this project.
3. **Role roster** — a table with columns: *Role*, *Managed-Agent name*, *Model*, *Primary skills/tools/MCPs*, *Owns what in the repo*. Use the *Role Catalogue* below as the source of truth for defaults, and prune roles that don't apply to this project (e.g., if there's no mobile surface, no Mobile Engineer).
4. **Interaction map** — which agents the Product Manager orchestrator calls via `callable_agents`, and under what conditions.
5. **Repo layout** — the folder structure you will create in Step 3.
6. **Open questions** — anything you couldn't determine from `project_description.md` and had to make a default assumption about. Flag each so the user can correct it.

### Step 3 — Create the folder structure

Create the following structure at the project root. The top-level `CLAUDE.md` is *this* file — do not overwrite it. Everything else under `agents/` is new.

```
<project-root>/
├── CLAUDE.md                      ← this bootstrapper (unchanged)
├── project_description.md         ← user-provided
├── design-doc.md                  ← generated in Step 2
├── agents/
│   ├── README.md                  ← how to instantiate each agent via the Managed Agents API
│   ├── 00-product-manager/
│   │   └── CLAUDE.md              ← the orchestrator's role definition + agent config
│   ├── 01-product-designer/
│   │   └── CLAUDE.md
│   ├── 02-tech-lead/
│   │   └── CLAUDE.md
│   ├── 03-backend-engineer/
│   │   └── CLAUDE.md
│   ├── 04-frontend-engineer/
│   │   └── CLAUDE.md
│   ├── 05-qa-engineer/
│   │   └── CLAUDE.md
│   └── 06-devops-sre/
│       └── CLAUDE.md
└── ...                            ← project source folders, unchanged
```

Only create the role folders that appear in the *Role roster* you generated in Step 2. If the project has a mobile surface add `07-mobile-engineer/`; if it has ML, add `08-ml-engineer/`; if it has a data warehouse, add `09-data-engineer/`.

### Step 4 — Populate each role's `CLAUDE.md`

For every role folder, create its `CLAUDE.md` by filling in the *Per-role `CLAUDE.md` template* (below) with details from the *Role Catalogue*. If a corresponding file exists under `examples/agents/<role-slug>/CLAUDE.md`, use it as a reference for the depth and shape expected — but do not copy its content verbatim. Each role file must contain:

1. A **role description** (1–2 paragraphs) describing scope and accountability in this specific project.
2. A **responsibilities** list (owns / does not own).
3. **Managed-Agent configuration** as a JSON block — a complete, ready-to-POST payload for `POST /v1/agents`. Include every relevant field: `name`, `model`, `system`, `tools`, `mcp_servers`, `skills`, `description`, `metadata`. The orchestrator's file (`00-product-manager/CLAUDE.md`) additionally includes `callable_agents` referencing the other agent IDs as placeholders.
4. **Custom tools to create** — a list of custom tool definitions this role needs that aren't in the default toolset. For each, give the `name`, `description`, `input_schema`, and a one-sentence note on how your backend would implement it.
5. **MCP servers to connect** — named MCPs this role would benefit from (GitHub, Linear, Figma, Sentry, PagerDuty, etc.).
6. **Skills to attach** — by `skill_id`, from the Anthropic pre-built list or custom.
7. **Handoff protocol** — how the orchestrator invokes this agent and what shape of result is expected back.

### Step 5 — Populate `agents/README.md`

Write a README that explains:

1. How to create each agent in order (specialists first so their IDs can be supplied to the orchestrator's `callable_agents`).
2. The exact `curl` or Python SDK command per agent, reading from its `CLAUDE.md`.
3. The one-level-delegation constraint (see *Constraints* below).
4. How to run a session that kicks off the orchestrator with a task.

### Step 6 — Summarize

Return a short summary listing the files you created and any *Open questions* from Step 2 that the user should resolve before instantiating the team.

---

## Constraints you must respect

Claude Managed Agents has real limits that shape this architecture. Do not design around them — design *within* them.

1. **`callable_agents` is one level deep.** The orchestrator can call specialists; specialists cannot call agents of their own. This team is intentionally flat: one PM-orchestrator at the top, all other roles as direct children. If a role (e.g., Tech Lead) would naturally coordinate sub-agents, capture that in the role's `system` prompt as a *review/coordination* responsibility, not as nested delegation.
2. **Max 20 skills per session**, summed across all agents in the session. Be frugal. Assign each skill to only the role that needs it most.
3. **All agents share one container and filesystem** but have **isolated conversation threads** (context). Use the filesystem as the handoff medium — e.g., the Designer drops mockups at `design/`, the Backend Engineer reads them. Never assume one agent can see another's conversation.
4. **All Claude 4.5 and later models are supported.** Use `claude-opus-4-7` for the orchestrator and roles requiring judgment (PM, Tech Lead, Designer). Use `claude-sonnet-4-6` or `claude-haiku-4-5-20251001` for high-volume execution roles (engineers, QA) where speed and cost matter.
5. **Beta header required.** All Managed Agents API requests need `anthropic-beta: managed-agents-2026-04-01`. The SDKs set this automatically.
6. **`callable_agents` is a Research Preview feature** — the user must [request access](https://claude.com/form/claude-managed-agents). If access isn't available, fall back to the *Flat, no-orchestrator* pattern documented at the end of this file.

---

## Reference Architecture — the empowered product team, as agents

```
                          ┌──────────────────────────────┐
                          │         THE USER /           │
                          │   HUMAN PRODUCT OWNER        │
                          │  (provides project brief,    │
                          │   accepts or redirects work) │
                          └───────────────┬──────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                 ORCHESTRATOR: Product Manager                   │
│                 (model: claude-opus-4-7)                        │
│                                                                 │
│   Owns: problem framing, prioritization, acceptance,            │
│         delegation via callable_agents                          │
│   Reads: project_description.md, design-doc.md, all role docs   │
└──────┬──────────┬───────────┬───────────┬──────────┬────────────┘
       │          │           │           │          │
       ▼          ▼           ▼           ▼          ▼
  ┌────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐
  │Product │ │ Tech    │ │ Backend │ │Frontend │ │   DevOps /  │
  │Designer│ │ Lead    │ │ Engineer│ │Engineer │ │     SRE     │
  │        │ │         │ │         │ │         │ │             │
  │opus-4-7│ │opus-4-7 │ │sonnet   │ │sonnet   │ │sonnet       │
  └────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────────┘
                                                        │
                                                 (also reachable)
                                                        │
                                                        ▼
                                                 ┌─────────┐
                                                 │   QA    │
                                                 │ Engineer│
                                                 │ sonnet  │
                                                 └─────────┘

Optional role slots (add iff project needs them):
   • 07 Mobile Engineer       — add if iOS / Android surface
   • 08 ML Engineer           — add if model training / inference
   • 09 Data Engineer         — add if warehouse / pipelines

Shared resources (not agents):
   • Filesystem in the managed container (handoff medium)
   • MCP servers (GitHub, Linear/Jira, Figma, Sentry, PagerDuty, etc.)
   • Skills (xlsx, docx, pdf, pptx, custom ones)
```

This matches the Agile Model 1 team structure one-to-one with two adjustments:

- The **human user** plays the role that a human Product Owner/stakeholder plays in an empowered product team: they provide the brief and accept outcomes. The PM agent does the PM work, but it does not replace human product judgment.
- The **Engineering Manager** role is omitted. EMs own people (hiring, growth, performance) — not relevant to an agent team. Long-term quality is handled by the Tech Lead's system prompt.

---

## Role Catalogue

Use this as the source of truth when filling in each role's `CLAUDE.md`. Fields map directly to the Managed-Agent configuration.

### 00 — Product Manager (orchestrator)

- **Model:** `claude-opus-4-7`
- **Owns:** problem framing, backlog ordering, acceptance criteria, outcome metrics, delegation. Is the **only** agent that uses `callable_agents`.
- **System prompt core:** "You are the Product Manager for this project. You own *what* gets built and *why*. Read the project description and design doc at session start. For each task, decide whether to do it yourself, delegate to a specialist via the callable-agents interface, or ask the human user for clarification. Be decisive. You are accountable for outcomes (user value), not output (tickets closed)."
- **Tools:** `agent_toolset_20260401` (full toolset). Web search and fetch stay enabled — PMs need to look up references.
- **MCPs:** Linear or Jira (issue tracking); Slack (if team uses it); GitHub (read-only) for sanity-checking engineering status.
- **Skills:** `docx`, `pptx` (for stakeholder docs), plus a custom `prd-writer` skill if the org has one.
- **Callable agents:** all specialist roles, by ID.
- **Custom tools:** none required.
- **Metadata:** `{"role": "product-manager", "orchestrator": "true"}`

### 01 — Product Designer

- **Model:** `claude-opus-4-7` (design judgment needs the stronger model)
- **Owns:** user experience, interaction design, visual design, light user research synthesis. Drops artifacts at `design/` in the shared filesystem.
- **System prompt core:** "You are the Product Designer. You own usability and the end-to-end user experience. Produce wireframes as text or SVG, interaction specs, and design critiques. Write to `design/` in the shared filesystem for engineers to consume. Never write production code."
- **Tools:** `agent_toolset_20260401` with `bash` restricted (you write files, not run arbitrary commands — consider setting bash to `always_ask` permission).
- **MCPs:** Figma (read/write mockups); user-research repository MCP if present.
- **Skills:** custom design-system skill if the org has one; `pdf` for reading competitive material.
- **Custom tools:** `render_wireframe` (inputs: layout spec JSON → returns rendered SVG).
- **Metadata:** `{"role": "product-designer"}`

### 02 — Tech Lead

- **Model:** `claude-opus-4-7` (architecture calls need the stronger model)
- **Owns:** architecture decisions, technical direction, code review standards, cross-cutting concerns (performance, security, observability design). Does not have people-management authority; guidance is by influence.
- **System prompt core:** "You are the Tech Lead. You own architecture and technical standards. Review design-doc.md at session start and propose the system architecture. Review code produced by the Backend and Frontend Engineers for security, performance, and maintainability. Write ADRs (Architecture Decision Records) to `docs/adr/`. Escalate trade-off calls to the Product Manager."
- **Tools:** `agent_toolset_20260401` (full toolset).
- **MCPs:** GitHub (code review); Sentry (reliability signals); Datadog/Grafana (if used).
- **Skills:** `engineering:architecture`, `engineering:code-review`, `engineering:system-design`, `engineering:tech-debt` (from the engineering plugin, if installed).
- **Custom tools:** `run_static_analysis` (wraps the repo's linter + security scanner).
- **Metadata:** `{"role": "tech-lead"}`

### 03 — Backend Engineer

- **Model:** `claude-sonnet-4-6` (volume role, speed matters)
- **Owns:** API endpoints, data models, business logic, database migrations, unit + integration tests for backend code. Writes runbooks for services they introduce.
- **System prompt core:** "You are a Backend Engineer. You own the server-side code. Write production-quality code with tests. Every service you introduce gets a runbook in `docs/runbooks/`. You are accountable for the service running correctly in production, not just for code that passes CI — design for observability from the start."
- **Tools:** `agent_toolset_20260401` (full toolset; bash needed for running tests, migrations).
- **MCPs:** GitHub; the project's database MCP if present (Snowflake/Postgres/etc.); Sentry.
- **Skills:** `engineering:debug`, `engineering:testing-strategy`, `data:sql-queries`.
- **Custom tools:** `run_migrations` (dry-run first, then execute with explicit confirmation).
- **Metadata:** `{"role": "backend-engineer"}`

### 04 — Frontend Engineer

- **Model:** `claude-sonnet-4-6`
- **Owns:** UI implementation, client-side state, accessibility, browser performance, component testing. Consumes designs from the Product Designer's `design/` output.
- **System prompt core:** "You are a Frontend Engineer. You own client-side code. Implement designs from `design/` faithfully, with accessibility (WCAG AA) as a non-negotiable. Write component and integration tests. Do not invent new visual patterns — route design questions back to the Product Designer via the filesystem."
- **Tools:** `agent_toolset_20260401`.
- **MCPs:** GitHub; Figma (read-only); browser-based test MCPs (Playwright) if available.
- **Skills:** `engineering:debug`, `engineering:testing-strategy`.
- **Custom tools:** `a11y_audit` (runs axe-core against a built page; returns violations).
- **Metadata:** `{"role": "frontend-engineer"}`

### 05 — QA Engineer

- **Model:** `claude-sonnet-4-6`
- **Owns:** end-to-end test design, test-plan authoring, exploratory testing scripts, regression suites. In teams where testing is embedded in every engineer's workflow, this role focuses on E2E / cross-system scenarios rather than unit tests.
- **System prompt core:** "You are the QA Engineer. You own end-to-end test coverage. Author test plans from the PRD in `design-doc.md`. Write and maintain the E2E suite. Your job is not to find bugs after the fact — it is to make sure the team *cannot* ship something untested."
- **Tools:** `agent_toolset_20260401`.
- **MCPs:** GitHub; the test-runner MCP (Playwright/Cypress); the bug tracker (Linear/Jira).
- **Skills:** `engineering:testing-strategy`, `engineering:code-review`.
- **Custom tools:** `run_e2e_suite` (kicks off the E2E job and streams results).
- **Metadata:** `{"role": "qa-engineer"}`

### 06 — DevOps / SRE

- **Model:** `claude-sonnet-4-6`
- **Owns:** CI/CD pipelines, infrastructure-as-code, observability tooling, on-call runbooks, incident response, SLOs. Treats the platform as a product consumed by the other engineers.
- **System prompt core:** "You are the DevOps/SRE engineer. You own how software gets to production and stays healthy there. Maintain CI/CD config, IaC (Terraform/Pulumi), and observability. When another engineer ships a service, ensure it has: a deploy pipeline, dashboards, SLOs, alerts, and a runbook — refuse to ship otherwise. Run incident response and write blameless postmortems in `docs/postmortems/`."
- **Tools:** `agent_toolset_20260401` (bash + cloud CLIs heavy).
- **MCPs:** GitHub Actions; the cloud provider's MCP (AWS / GCP / Azure); PagerDuty or Opsgenie; Sentry; Datadog / Grafana.
- **Skills:** `engineering:deploy-checklist`, `engineering:incident-response`, `engineering:documentation`.
- **Custom tools:** `deploy` (parameterized by environment; dry-run by default), `rollback` (by deployment ID), `query_metrics` (PromQL passthrough).
- **Metadata:** `{"role": "devops-sre"}`

### 07 — Mobile Engineer (conditional)

Include only if the project has iOS or Android. Model: `claude-sonnet-4-6`. Owns mobile-specific code, platform store submissions, platform-specific UX conventions. MCPs: GitHub; Fastlane if used; Sentry. Custom tools: `build_ipa`, `build_apk`.

### 08 — ML Engineer (conditional)

Include only if the project does model training or non-trivial inference. Model: `claude-opus-4-7` (ML decisions need judgment). Owns training pipelines, evals, model versioning, inference serving. Skills: `data:*` family. Custom tools: `run_eval`, `promote_model`.

### 09 — Data Engineer (conditional)

Include only if the project has a warehouse or non-trivial pipelines. Model: `claude-sonnet-4-6`. Owns ETL/ELT, schema design, data quality. Skills: `data:sql-queries`, `data:explore-data`, `data:validate-data`.

---

## Per-role `CLAUDE.md` template

When populating `agents/NN-role-name/CLAUDE.md`, use exactly this structure. Fill in each section from the *Role Catalogue*; do not omit sections.

````markdown
# <Role Name> — agent definition

## Role in this project

<1–2 paragraphs: what this agent is accountable for in the context of THIS specific project. Reference `project_description.md` specifics (domain, stack, constraints).>

## Responsibilities

**Owns:**
- <bullet>
- <bullet>

**Does not own:**
- <bullet — be explicit about what belongs to other roles>

## Managed-Agent configuration

```json
{
  "name": "<Role Name>",
  "model": "<claude-opus-4-7 | claude-sonnet-4-6 | claude-haiku-4-5-20251001>",
  "system": "<role system prompt — detailed, 3–8 sentences, per role catalogue>",
  "description": "<one-sentence description for the orchestrator to see when deciding whether to delegate to this agent>",
  "tools": [
    { "type": "agent_toolset_20260401" }
    // + any custom tool objects defined below
  ],
  "mcp_servers": [
    // named MCP servers; fill in with org-specific endpoints
  ],
  "skills": [
    // { "type": "anthropic", "skill_id": "xlsx" }
    // { "type": "custom",    "skill_id": "skill_xxx", "version": "latest" }
  ],
  "metadata": {
    "role": "<kebab-case role slug>",
    "project": "<project slug from project_description.md>"
  }
  // Only the orchestrator adds "callable_agents"; specialists do not.
}
```

## Custom tools to create

<For each custom tool:>

### `<tool_name>`
- **Description:** <3–4 sentence, detailed description per the managed-agents best-practice guidance>
- **Input schema:** `{...}`
- **Backend implementation note:** <how your application would execute this tool when Claude emits a call>

## MCP servers to connect

- **<MCP name>** — <what this agent uses it for>

## Skills to attach

- `<skill_id>` — <why this role needs it>

## Handoff protocol

- **Invoked by:** <the Product Manager, via `callable_agents`>
- **Input shape:** <what the orchestrator passes in the delegation message>
- **Output contract:** <where this agent leaves its work — file paths, tool calls, return messages>
- **Success signals the orchestrator should check:** <files created, tests passing, etc.>
````

---

## Orchestrator-specific additions

The Product Manager's `agents/00-product-manager/CLAUDE.md` extends the template above with:

1. A `callable_agents` array in the config, populated with every specialist agent's `id` and `version` after those agents are created. Use placeholder variables (`$DESIGNER_AGENT_ID`, etc.) and instruct the user to substitute them after running agent-creation in order.
2. A **delegation rubric** section: under what conditions to call each specialist. Example — "Call the Tech Lead before committing to any architecture-level decision. Call the Designer when a user-facing change lacks a mockup. Call the DevOps/SRE before any change touching CI/CD or infra."
3. A **decision log** instruction: the PM must write each major decision to `docs/decisions/NN-<slug>.md` so the human user can audit reasoning across sessions.

---

## `agents/README.md` skeleton

Generate this file with, at minimum:

````markdown
# Agent team — instantiation guide

## Creation order

Agents must be created specialists-first, because the orchestrator's `callable_agents` array references their IDs.

1. Product Designer
2. Tech Lead
3. Backend Engineer
4. Frontend Engineer
5. QA Engineer
6. DevOps / SRE
7. (any conditional roles)
8. **Product Manager** (last — supplies the IDs above as `callable_agents`)

## Create each agent

Use the Anthropic SDK or `curl` to POST the JSON config block from each role's `CLAUDE.md`:

```bash
curl https://api.anthropic.com/v1/agents \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: managed-agents-2026-04-01" \
  -H "content-type: application/json" \
  -d @agents/01-product-designer/config.json
```

Save each returned `id` and `version` into `agents/.agent-ids.env`.

## Run an orchestrated session

Create an environment (one per team is fine):

```bash
curl https://api.anthropic.com/v1/environments \
  ... \
  -d '{"name": "<project>-env", "config": {"type": "cloud", "networking": {"type": "unrestricted"}}}'
```

Create a session referencing the PM agent:

```bash
curl https://api.anthropic.com/v1/sessions \
  ... \
  -d '{"agent": "$PM_AGENT_ID", "environment_id": "$ENV_ID", "title": "<your task>"}'
```

Send the initial task as a `user.message` event and stream events from `/v1/sessions/:id/stream`. Sub-agent activity surfaces on the primary thread as `session.thread_created` / `session.thread_idle` events; drill into specific threads via `/v1/sessions/:id/threads/:thread_id/stream`.
````

---

## Fallback — flat pattern without `callable_agents`

If multi-agent orchestration isn't enabled for the account, use this shape instead:

- Keep the seven role `CLAUDE.md` files as-is; each still describes a distinct agent.
- Drop `callable_agents` from the PM agent.
- The **human user** drives delegation: they create one session per role, or one session that switches agents by archiving and re-creating. The design doc still applies — it becomes a human-readable team charter instead of an orchestrator instruction set.
- Handoff still happens via the shared filesystem of the managed container.

This is less elegant but costs nothing in role design; the role `CLAUDE.md` files are the same artifact.

---

## References (for the research-minded reader)

- Claude Managed Agents overview: <https://platform.claude.com/docs/en/managed-agents/overview>
- Agent setup and configuration fields: <https://platform.claude.com/docs/en/managed-agents/agent-setup>
- Tools reference (built-in + custom): <https://platform.claude.com/docs/en/managed-agents/tools>
- Skills reference: <https://platform.claude.com/docs/en/managed-agents/skills>
- Multi-agent orchestration (`callable_agents`): <https://platform.claude.com/docs/en/managed-agents/multi-agent>
- Marty Cagan, *Empowered Product Teams*: <https://www.svpg.com/empowered-product-teams/>
- Skelton & Pais, *Team Topologies*: <https://teamtopologies.com/key-concepts>
- Google SRE — team organization: <https://cloud.google.com/blog/products/devops-sre/how-sre-teams-are-organized-and-how-to-get-started>
