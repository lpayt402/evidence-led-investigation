# Evidence-Led Investigation Workbench

This folder adds a small offline workbench to the methodology in [`../METHODOLOGY.md`](../METHODOLOGY.md). It keeps source records, direct observations, analytic claims, and human dispositions separate so a reviewer can trace how a conclusion was reached.

The command and provenance design adapts patterns from the author's separate source-compatibility work. No OpenPlant source code, biological data, protocols, images, runtime, or third-party dependencies are included here.

## Quick start

Requires Python 3.10+; no package installation or network access is required.

```bash
python3 manage.py doctor
python3 manage.py inventory --json
python3 manage.py validate examples/synthetic
python3 manage.py status examples/synthetic --json
python3 manage.py test
```

To create a blank local workspace:

```bash
python3 manage.py bootstrap ./case-demo
```

This only copies blank templates. It does not fetch URLs, gather evidence, or create a fraud score.

## What the commands do

- `doctor` checks the local Python version
- `bootstrap` creates a workspace from templates, without network access
- `inventory --json` lists this kit's files and status
- `status CASE_DIR --json` summarizes source, observation, claim, and review counts
- `validate CASE_DIR` checks required fields and references
- `test` runs the local unit tests

A `VALID` result means the records meet the checked schema and references; it does not establish that a source is authentic or a claim is true. Human reviewers make and record consequential dispositions. The validator cannot authenticate reviewers or enforce file permissions.

## Files

- `templates/` contains blank scope, source, observation, claim, review, and report formats
- `examples/synthetic/` is an entirely fictional walkthrough using reserved `.example.com` identifiers
- `skills/evidence-led-investigation/SKILL.md` is portable agent guidance
- `docs/SAMPLE-WORKFLOW.md` shows the source-to-review path
- `docs/PROVENANCE.md`, `docs/PORTFOLIO.md`, and `docs/VALIDATION.md` describe origins, contribution, and test limits

The repository has no selected project license. Do not treat public visibility as a license to reuse its files.
