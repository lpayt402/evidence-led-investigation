# Validation Record

Updated: 2026-09-30

## Verified locally

- Python 3.12 runs the workbench CLI.
- The synthetic example passes scope, source, observation, claim, and review-reference checks.
- Five unit tests pass: synthetic happy path, blank workspace bootstrap, missing source reference, missing alternative, and prevention of agent-authored human dispositions.
- The workbench imports only Python standard-library modules and makes no network request.

## Not established

- No real source URL, target, case, or report was collected or reviewed.
- Tests do not establish source authenticity, reviewer identity, authority, evidence sufficiency, attribution, legal compliance, detector accuracy, or effectiveness.
- Windows/macOS CI and long-term compatibility have not been tested.
- No project license has been selected.

Re-run from the repository root:

```bash
python3 workbench/manage.py doctor
python3 workbench/manage.py validate workbench/examples/synthetic
python3 workbench/manage.py test
```
