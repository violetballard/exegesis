# Contributors

Exegesis is founded, directed, and owned by Dr. Violet Ballard. The Developer
preview was built with a deliberately AI-native
engineering workflow: Dr. Ballard sets the product direction, research method,
security expectations, and release judgment, while coordinated model workers help
implement, review, integrate, and operate the codebase.

Model output is not treated as independent product ownership. Models are part of
the development apparatus, and all public release decisions remain human-owned.

## Model-Assisted Development Stack

The project has used the following model families across planning, feature work,
review, integration, and local/offline execution:

- GPT 5.3 Codex
- GPT 5.4
- GPT 5.5
- Claude Sonnet 4.6
- Claude Opus 4.7
- Claude Opus 4.8
- Gemini 3.5 Flash
- gpt-oss-35b
- gpt-oss-120b
- qwen3.6-27b
- Gemma 31B

## Workflow Roles

Exegesis is not built by one long-running chatbot session. It uses a structured
multi-model workflow with explicit roles and handoffs.

- Workers implement bounded feature slices from written specs and ownership
  rules.
- Reviewers inspect the slice for correctness, regressions, scope drift, missing
  tests, and security or provenance gaps.
- Fixers repair review findings or failed gates without expanding the feature
  scope.
- Integrators merge accepted work into the main product line, resolve conflicts,
  and preserve the release and demo gates.
- Operators monitor the pipeline, detect stuck lanes, recover failed workers,
  and keep the garden moving without turning normal status checks into hidden
  product edits.

This makes the development process closer to a small, auditable engineering
organization than a single-agent "vibe coding" loop. The detailed internal
automation, packet routing, and lane-control system are not part of the public
Developer preview source, but the public app reflects the same principle:
visible actions, explicit context, review before mutation, and provenance-first
workflow design.

## Why This Matters

Exegesis is high-trust writing software. It is meant for work where sources,
interpretation, confidentiality, and revision history matter. The development
workflow mirrors that product philosophy: human judgment stays central, model
work is bounded and reviewed, and the system is designed to make decisions and
context visible rather than mysterious.
