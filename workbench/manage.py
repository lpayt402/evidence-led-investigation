#!/usr/bin/env python3
"""Offline evidence-led investigation workspace helper."""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"

class WorkbenchError(Exception):
    pass


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkbenchError(f"cannot read valid JSON at {path}: {exc}") from exc


def read_csv(path: Path):
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))
    except OSError as exc:
        raise WorkbenchError(f"cannot read CSV at {path}: {exc}") from exc


def read_jsonl(path: Path):
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise WorkbenchError(f"cannot read JSONL at {path}: {exc}") from exc
    output = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            output.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise WorkbenchError(f"{path}:{number}: invalid JSON: {exc}") from exc
    return output


def doctor(as_json=False):
    payload = {"ok": sys.version_info >= (3, 10), "python": sys.version.split()[0], "network_access": "not used by this prototype"}
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Python {payload['python']}: {'OK' if payload['ok'] else 'requires 3.10+'}")
        print("Network: not used by this prototype")
    return 0 if payload["ok"] else 1


def init(destination: Path):
    destination = destination.expanduser().resolve()
    if destination.exists() and not destination.is_dir():
        raise WorkbenchError(f"destination is not a directory: {destination}")
    if destination.exists() and any(destination.iterdir()):
        raise WorkbenchError(f"destination is not empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    for source in TEMPLATES.iterdir():
        if source.is_file():
            shutil.copy2(source, destination / source.name)
    print(f"Created blank workspace: {destination}")
    return 0


def validate(case_dir: Path, as_json=False):
    case_dir = case_dir.expanduser().resolve()
    errors = []
    try:
        scope = read_json(case_dir / "scope.json")
        sources = read_csv(case_dir / "sources.csv")
        observations = read_csv(case_dir / "observations.csv")
        claims = read_jsonl(case_dir / "claims.jsonl")
        reviews = read_csv(case_dir / "reviews.csv")
    except WorkbenchError as exc:
        errors.append(str(exc))
        _print_validation(case_dir, errors, as_json)
        return 1

    for key in ("case_id", "question", "authority_basis", "scope_start", "scope_end", "exclusions", "prohibited_actions", "stop_condition"):
        if not scope.get(key):
            errors.append(f"scope.json: required value missing: {key}")
    if scope.get("collection_mode", "public-passive") != "public-passive":
        errors.append("scope.json: prototype supports public-passive mode only")

    def unique_ids(rows, field, label):
        ids = [row.get(field, "").strip() for row in rows]
        if any(not value for value in ids):
            errors.append(f"{label}: blank {field}")
        if len(ids) != len(set(ids)):
            errors.append(f"{label}: duplicate {field}")
        return set(ids)

    source_ids = unique_ids(sources, "source_id", "sources.csv")
    source_lineages = {row.get("source_id", ""): row.get("lineage_id", "").strip() for row in sources}
    observation_ids = unique_ids(observations, "observation_id", "observations.csv")
    claim_ids = unique_ids(claims, "claim_id", "claims.jsonl")
    for row in sources:
        for field in ("source_type", "url_or_reference", "observed_at", "capture_method", "locator", "limitations", "lineage_id"):
            if not row.get(field, "").strip():
                errors.append(f"source {row.get('source_id','?')}: missing {field}")
    for row in observations:
        for field in ("direct_observation", "observed_at", "limitations"):
            if not row.get(field, "").strip():
                errors.append(f"observation {row.get('observation_id','?')}: missing {field}")
        if row.get("source_id", "") not in source_ids:
            errors.append(f"observation {row.get('observation_id','?')}: unknown source_id {row.get('source_id','')}")
    reviewed_claims = set()
    for row in claims:
        cid = row.get("claim_id", "?")
        evidence = row.get("evidence_ids", [])
        counter = row.get("counter_evidence_ids", [])
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"claim {cid}: needs evidence_ids")
            evidence = []
        if not isinstance(counter, list):
            errors.append(f"claim {cid}: counter_evidence_ids must be a list")
            counter = []
        for ref in evidence + counter:
            if ref not in observation_ids:
                errors.append(f"claim {cid}: unknown observation_id {ref}")
        independence = row.get("independence_assessment")
        if not isinstance(independence, str) or independence not in {"one_lineage", "multiple_lineages", "not_assessed"}:
            errors.append(f"claim {cid}: independence_assessment must be one_lineage, multiple_lineages, or not_assessed")
        else:
            evidence_sources = {
                observation.get("source_id", "")
                for observation in observations
                if observation.get("observation_id", "") in evidence
            }
            lineages = {source_lineages.get(source_id, "") for source_id in evidence_sources}
            lineages.discard("")
            if independence == "multiple_lineages" and len(lineages) < 2:
                errors.append(f"claim {cid}: multiple_lineages requires supporting observations from at least two source lineages")
            if independence == "one_lineage" and len(lineages) > 1:
                errors.append(f"claim {cid}: one_lineage conflicts with supporting observations from multiple source lineages")
        if not row.get("alternatives") or not isinstance(row.get("alternatives"), list):
            errors.append(f"claim {cid}: needs at least one alternative explanation")
        if row.get("confidence") not in {"low", "moderate", "high", "not_assessed"}:
            errors.append(f"claim {cid}: confidence must be qualitative or not_assessed")
        if row.get("author_type") == "agent-proposal" and row.get("state") != "proposed":
            errors.append(f"claim {cid}: agent output must remain proposed")
        if "human_disposition" in row:
            errors.append(f"claim {cid}: human_disposition belongs in reviews.csv, not a claim proposal")
        if row.get("state") not in {"proposed", "reviewed", "rejected", "unresolved"}:
            errors.append(f"claim {cid}: invalid state")
    for row in reviews:
        cid = row.get("claim_id", "").strip()
        if cid not in claim_ids:
            errors.append(f"review: unknown claim_id {cid}")
        if not row.get("reviewer", "").strip() or not row.get("reviewed_at", "").strip() or not row.get("rationale", "").strip():
            errors.append(f"review for {cid or '?'}: reviewer, reviewed_at, and rationale are required")
        if row.get("disposition") not in {"accepted_for_report", "rejected", "unresolved", "return_for_more_review"}:
            errors.append(f"review for {cid or '?'}: invalid human disposition")
        if cid:
            reviewed_claims.add(cid)
    for row in claims:
        if row.get("state") in {"reviewed", "rejected", "unresolved"} and row.get("claim_id") not in reviewed_claims:
            errors.append(f"claim {row.get('claim_id','?')}: state implies review but no human review record exists")

    _print_validation(case_dir, errors, as_json)
    return 1 if errors else 0


def _print_validation(case_dir, errors, as_json):
    payload = {"case_dir": str(case_dir), "valid": not errors, "errors": errors}
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        if errors:
            print("INVALID")
            for error in errors:
                print(f"- {error}")
        else:
            print("VALID: schema and references pass; this does not validate the truth of any claim")


def status(case_dir: Path, as_json=False):
    case_dir = case_dir.expanduser().resolve()
    counts = {}
    for name, filename, reader in (
        ("sources", "sources.csv", read_csv),
        ("observations", "observations.csv", read_csv),
        ("claims", "claims.jsonl", read_jsonl),
        ("reviews", "reviews.csv", read_csv),
    ):
        counts[name] = len(reader(case_dir / filename))
    payload = {"case_dir": str(case_dir), "counts": counts}
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Workspace: {case_dir}")
        for key, value in counts.items():
            print(f"{key:14} {value}")
    return 0


def inventory(as_json=False):
    manifest = read_json(ROOT / "manifest.json")
    items = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or any(part in {"__pycache__", ".git"} for part in path.parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative == "manifest.json":
            continue
        items.append(relative)
    payload = {"kit": manifest["name"], "status": manifest["status"], "files": items}
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"{payload['kit']} ({payload['status']})")
        for item in items:
            print(f"- {item}")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="Offline evidence-led investigation workspace helper")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("doctor"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("bootstrap", aliases=["init"]); p.add_argument("destination", type=Path)
    p = sub.add_parser("validate"); p.add_argument("case_dir", type=Path); p.add_argument("--json", action="store_true")
    p = sub.add_parser("status"); p.add_argument("case_dir", type=Path); p.add_argument("--json", action="store_true")
    p = sub.add_parser("inventory"); p.add_argument("--json", action="store_true")
    sub.add_parser("test")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.command == "doctor": return doctor(args.json)
        if args.command in {"bootstrap", "init"}: return init(args.destination)
        if args.command == "validate": return validate(args.case_dir, args.json)
        if args.command == "status": return status(args.case_dir, args.json)
        if args.command == "inventory": return inventory(args.json)
        if args.command == "test":
            import unittest
            suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
            result = unittest.TextTestRunner(verbosity=2).run(suite)
            return 0 if result.wasSuccessful() else 1
    except WorkbenchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
