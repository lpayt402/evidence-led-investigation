# Evidence-Led Online Fraud Investigation

A working method for analyzing public observations about possible online fraud. It keeps claims tied to sources and leaves room for other explanations. It is not a detector or a finding that any person or organization committed a crime.

Start with a narrow question. Record what you saw, where and when you saw it, and how it bears on the question. Keep inference and uncertainty visible. This repository contains no real cases, targets, datasets, or collection code.

## Documents

- [Methodology](METHODOLOGY.md): scope, evidence handling, relationship analysis, review, reporting, and safety boundaries
- [Synthetic example](SYNTHETIC-EXAMPLE.md): a fictional worked example showing the distinction between observations, inferences, hypotheses, and human disposition
- [Workbench](workbench/README.md): local templates and deterministic checks for recording sources, observations, claims, and human review

## Related article and lens

The [task-to-outcome lens](docs/TASK-TO-OUTCOME-LENS.md) pairs with [“The Floor is Falling – Task by Task”](https://www.linkedin.com/pulse/floor-falling-task-lee-payton-ciu4c) (Sept. 13, 2026). It asks which task changed, what the evidence shows, and what still has to happen before an outcome. It connects those questions to this repository’s evidence and review workflow. Capability to Outcome Distance is a question, not a score.

## Try the workbench

The workbench runs offline. A researcher records source references and direct observations. An agent can propose claims that cite those observations; a human reviewer records a separate disposition.

Requires Python 3.10 or newer; no package install, credentials, or network access are needed for the checks:

```bash
python3 workbench/manage.py doctor
python3 workbench/manage.py validate workbench/examples/synthetic
python3 workbench/manage.py status workbench/examples/synthetic --json
python3 workbench/manage.py test
```

`validate` checks required fields, evidence references, and whether each claim's cited observations map to the stated source-lineage assessment. Different lineage IDs do not prove actual independence. A valid result means the records are structurally consistent; it does not confirm the truth of a claim. `status` prints record counts. To create a blank local workspace, use `python3 workbench/manage.py bootstrap ./case-demo`; then fill its templates within an authorized scope. The included example is fictional and uses reserved `.example.com` names.

## Evidence path

The workbench keeps these records separate. Its offline checks validate structure and references; they do not establish source authenticity or claim truth.

```text
Source reference + direct observation
                  |
                  v
       Claim citing observations
                  |
                  v
       Validate fields and links
                  |
                  v
      Human review and disposition
```

## Core principles

- A tip, search hit, or report is a lead, not a finding
- Preserve source, observation time, capture method, and limitations for each material claim
- Separate observation from interpretation, hypothesis, confidence, and disposition
- Shared hosting, templates, certificates, names, or contact details can suggest a relationship but do not establish common control or wrongdoing
- Track source independence, counter-evidence, benign alternatives, missing checks, and uncertainty
- Keep historical activity separate from current state
- Human reviewers control classification and consequential decisions; automated output is advisory only

## Status and limits

This is an early methodology draft with a small workbench prototype, not a validated detector. Eight local tests cover the synthetic example, bootstrap, missing references and alternatives, separation of agent proposals from human disposition, source-lineage consistency, and malformed assessment values. No empirical accuracy claims are made, and no attribution or crime is established.

The method uses public, passive research. It is not permission to access accounts, contact targets or third parties, scan systems, evade controls, submit forms, test credentials, make transactions, intervene, or publish allegations. Follow applicable law, platform rules, and organizational review requirements. The workbench has no collector or account integration; it checks record structure, not the authenticity of a reviewer or the legal sufficiency of an investigation.

No project license is included. Check reuse rights and keep any required third-party attribution.

## Feedback

Reviewers should flag unclear steps, unsupported claims, missing benign explanations, safety concerns, and attribution or licensing questions. Proposed improvements should preserve source traceability, counter-evidence, uncertainty, and human accountability.
