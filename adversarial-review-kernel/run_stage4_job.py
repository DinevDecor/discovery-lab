"""CLI entrypoint for the Stage 4 GitHub Actions job roles: `select`
(pulls the two already-persisted IndependentAnalysisArtifact records for
one run out of blind-analysis-kernel's durable Git ledger), `disagree`
(deterministic diff), `claude-falsify` / `gpt-falsify` (each
independently critiques the OTHER provider's analysis), `judge` (the
deterministic decision - no model call), and `persist` (writes both
falsification artifacts and the judgment artifact to their local ledger
files - never calls git itself, exactly like blind-analysis-kernel's own
`persist` subcommand).

Read-only against blind-analysis-kernel's and constraint-archaeology-
agents' data. Writes only to files the caller names via --out/--*-out -
never to any CA/BCA/blind-analysis-kernel path.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(ROOT)
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from adversarial_review_kernel.disagree import extract_disagreements  # noqa: E402
from adversarial_review_kernel.falsify import build_falsifier_packet, run_claude_falsifier, run_gpt_falsifier  # noqa: E402
from adversarial_review_kernel.identity import make_judgment_id  # noqa: E402
from adversarial_review_kernel.judgment import decide  # noqa: E402
from adversarial_review_kernel.ledger import FalsificationLedger, JudgmentLedger  # noqa: E402
from adversarial_review_kernel.models import Disagreement, FalsificationArtifact, PROVIDER_ANTHROPIC, PROVIDER_OPENAI  # noqa: E402

DEFAULT_CA_ANOMALIES = os.path.join(REPO_ROOT, "constraint-archaeology-agents", "data", "anomalies.json")
DEFAULT_CA_OBSERVATIONS = os.path.join(REPO_ROOT, "constraint-archaeology-agents", "data", "observations.jsonl")
DEFAULT_ANALYSES_LEDGER = os.path.join(REPO_ROOT, "blind-analysis-kernel", "data", "analyses.jsonl")
DEFAULT_FALSIFICATION_LEDGER = os.path.join(ROOT, "data", "falsifications.jsonl")
DEFAULT_JUDGMENT_LEDGER = os.path.join(ROOT, "data", "judgments.jsonl")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _dump_json(obj, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, sort_keys=True, ensure_ascii=False, indent=2, default=str)


def cmd_select(args: argparse.Namespace) -> None:
    """Pulls the durably-persisted Claude and GPT IndependentAnalysisArtifact
    rows for one run out of blind-analysis-kernel/data/analyses.jsonl -
    read-only, never rewrites that ledger."""
    claude_row = None
    gpt_row = None
    with open(args.analyses_ledger, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("run_id") != args.run_id:
                continue
            if row.get("provider") == PROVIDER_ANTHROPIC:
                claude_row = row
            elif row.get("provider") == PROVIDER_OPENAI:
                gpt_row = row
    if claude_row is None or gpt_row is None:
        raise SystemExit(f"run_id {args.run_id!r} does not have both a claude and a gpt "
                          f"IndependentAnalysisArtifact in {args.analyses_ledger}")
    _dump_json(claude_row, args.claude_out)
    _dump_json(gpt_row, args.gpt_out)
    print(json.dumps({
        "run_id": args.run_id,
        "claude_artifact_id": claude_row["artifact_id"],
        "gpt_artifact_id": gpt_row["artifact_id"],
        "source_case_ids": claude_row["source_case_ids"],
        "claude_out": args.claude_out, "gpt_out": args.gpt_out,
    }, indent=2, sort_keys=True))


def cmd_disagree(args: argparse.Namespace) -> None:
    claude = _load_json(args.claude_artifact)
    gpt = _load_json(args.gpt_artifact)
    disagreements = extract_disagreements(
        claude["analysis"], gpt["analysis"],
        claude_artifact_id=claude["artifact_id"], gpt_artifact_id=gpt["artifact_id"],
    )
    _dump_json([d.to_dict() for d in disagreements], args.out)
    print(json.dumps({
        "disagreement_count": len(disagreements),
        "fields": [d.field for d in disagreements],
        "out": args.out,
    }, indent=2, sort_keys=True))


def _load_disagreements(path: str) -> list:
    return [Disagreement(**d) for d in _load_json(path)]


def _resolve_anomaly_and_observations(args: argparse.Namespace):
    with open(args.ca_anomalies_path, encoding="utf-8") as f:
        anomalies = {a["anomaly_id"]: a for a in json.load(f)}
    if args.anomaly_id not in anomalies:
        raise SystemExit(f"anomaly_id {args.anomaly_id!r} not found in {args.ca_anomalies_path}")
    observations = {}
    with open(args.ca_observations_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                o = json.loads(line)
                observations[o["observation_id"]] = o
    return anomalies[args.anomaly_id], observations


def cmd_claude_falsify(args: argparse.Namespace) -> None:
    gpt = _load_json(args.gpt_artifact)
    disagreements = _load_disagreements(args.disagreements)
    anomaly, observations = _resolve_anomaly_and_observations(args)
    packet = build_falsifier_packet(anomaly, observations, args.run_id)
    if packet.source_case_ids != gpt["source_case_ids"]:
        raise SystemExit(
            f"packet source_case_ids {packet.source_case_ids!r} do not match the persisted "
            f"gpt artifact's source_case_ids {gpt['source_case_ids']!r} - wrong --anomaly-id?"
        )
    artifact = run_claude_falsifier(packet, gpt["analysis"], gpt["artifact_id"], disagreements)
    _write_falsification(artifact, args.out)


def cmd_gpt_falsify(args: argparse.Namespace) -> None:
    claude = _load_json(args.claude_artifact)
    disagreements = _load_disagreements(args.disagreements)
    anomaly, observations = _resolve_anomaly_and_observations(args)
    packet = build_falsifier_packet(anomaly, observations, args.run_id)
    if packet.source_case_ids != claude["source_case_ids"]:
        raise SystemExit(
            f"packet source_case_ids {packet.source_case_ids!r} do not match the persisted "
            f"claude artifact's source_case_ids {claude['source_case_ids']!r} - wrong --anomaly-id?"
        )
    artifact = run_gpt_falsifier(packet, claude["analysis"], claude["artifact_id"], disagreements)
    _write_falsification(artifact, args.out)


def _write_falsification(artifact: FalsificationArtifact, out_path: str) -> None:
    _dump_json(artifact.to_dict(), out_path)
    print(json.dumps({
        "artifact_id": artifact.artifact_id,
        "critic_provider": artifact.critic_provider,
        "critic_model": artifact.critic_model,
        "target_artifact_id": artifact.target_artifact_id,
        "input_packet_sha256": artifact.input_packet_sha256,
        "finding_count": len(artifact.findings),
        "out": out_path,
    }, indent=2, sort_keys=True))


def cmd_judge(args: argparse.Namespace) -> None:
    claude = _load_json(args.claude_artifact)
    gpt = _load_json(args.gpt_artifact)
    disagreements = _load_disagreements(args.disagreements)
    claude_falsification = FalsificationArtifact.from_dict(_load_json(args.claude_falsification))
    gpt_falsification = FalsificationArtifact.from_dict(_load_json(args.gpt_falsification))

    if claude_falsification.input_packet_sha256 != gpt_falsification.input_packet_sha256:
        raise SystemExit(
            "structural integrity check failed: the two Falsifiers' input_packet_sha256 "
            f"differ ({claude_falsification.input_packet_sha256!r} vs "
            f"{gpt_falsification.input_packet_sha256!r}) - refusing to judge"
        )
    if claude_falsification.target_artifact_id != gpt["artifact_id"]:
        raise SystemExit("claude_falsification.target_artifact_id does not match the gpt artifact - "
                          "the Claude Falsifier must have critiqued GPT's analysis")
    if gpt_falsification.target_artifact_id != claude["artifact_id"]:
        raise SystemExit("gpt_falsification.target_artifact_id does not match the claude artifact - "
                          "the GPT Falsifier must have critiqued Claude's analysis")

    case_ids = claude["source_case_ids"]
    if case_ids != gpt["source_case_ids"]:
        raise SystemExit("structural integrity check failed: source_case_ids differ between "
                          "claude and gpt analyses - refusing to judge")

    judgment = decide(
        judgment_id=make_judgment_id(claude["run_id"]),
        case_id=case_ids[0],
        source_run_id=claude["run_id"],
        claude_artifact_id=claude["artifact_id"],
        gpt_artifact_id=gpt["artifact_id"],
        disagreements=disagreements,
        claude_falsification=claude_falsification,
        gpt_falsification=gpt_falsification,
        created_at=utc_now_iso(),
    )
    _dump_json(judgment.to_dict(), args.out)
    print(json.dumps({
        "judgment_id": judgment.judgment_id,
        "status": judgment.status,
        "reasons": judgment.reasons,
        "material_disagreements": judgment.material_disagreements,
        "schema_ambiguities": judgment.schema_ambiguities,
        "out": args.out,
    }, indent=2, sort_keys=True))


def cmd_persist(args: argparse.Namespace) -> None:
    claude_falsification = FalsificationArtifact.from_dict(_load_json(args.claude_falsification))
    gpt_falsification = FalsificationArtifact.from_dict(_load_json(args.gpt_falsification))
    from adversarial_review_kernel.models import JudgmentArtifact
    judgment = JudgmentArtifact.from_dict(_load_json(args.judgment))

    falsification_ledger = FalsificationLedger(args.falsification_ledger_out)
    claude_written = falsification_ledger.append(claude_falsification)
    gpt_written = falsification_ledger.append(gpt_falsification)

    judgment_ledger = JudgmentLedger(args.judgment_ledger_out)
    judgment_written = judgment_ledger.append(judgment)

    print(json.dumps({
        "claude_falsification_id": claude_falsification.artifact_id,
        "gpt_falsification_id": gpt_falsification.artifact_id,
        "claude_falsification_written": claude_written,
        "gpt_falsification_written": gpt_written,
        "judgment_id": judgment.judgment_id,
        "judgment_written": judgment_written,
        "status": judgment.status,
        "any_new_content": claude_written or gpt_written or judgment_written,
        "falsification_ledger_path": args.falsification_ledger_out,
        "judgment_ledger_path": args.judgment_ledger_out,
    }, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="role", required=True)

    p_select = sub.add_parser("select", help="pull the two persisted IndependentAnalysisArtifacts for one run")
    p_select.add_argument("--run-id", required=True)
    p_select.add_argument("--analyses-ledger", default=DEFAULT_ANALYSES_LEDGER)
    p_select.add_argument("--claude-out", required=True)
    p_select.add_argument("--gpt-out", required=True)
    p_select.set_defaults(func=cmd_select)

    p_disagree = sub.add_parser("disagree", help="deterministic diff of the two analyses")
    p_disagree.add_argument("--claude-artifact", required=True)
    p_disagree.add_argument("--gpt-artifact", required=True)
    p_disagree.add_argument("--out", required=True)
    p_disagree.set_defaults(func=cmd_disagree)

    common_falsify = dict(
        anomaly_id=("--anomaly-id", {"required": True}),
        run_id=("--run-id", {"required": True}),
        ca_anomalies_path=("--ca-anomalies-path", {"default": DEFAULT_CA_ANOMALIES}),
        ca_observations_path=("--ca-observations-path", {"default": DEFAULT_CA_OBSERVATIONS}),
    )

    p_cf = sub.add_parser("claude-falsify", help="Claude critiques GPT's analysis")
    p_cf.add_argument("--gpt-artifact", required=True)
    p_cf.add_argument("--disagreements", required=True)
    p_cf.add_argument("--out", required=True)
    for flag, kwargs in common_falsify.values():
        p_cf.add_argument(flag, **kwargs)
    p_cf.set_defaults(func=cmd_claude_falsify)

    p_gf = sub.add_parser("gpt-falsify", help="GPT critiques Claude's analysis")
    p_gf.add_argument("--claude-artifact", required=True)
    p_gf.add_argument("--disagreements", required=True)
    p_gf.add_argument("--out", required=True)
    for flag, kwargs in common_falsify.values():
        p_gf.add_argument(flag, **kwargs)
    p_gf.set_defaults(func=cmd_gpt_falsify)

    p_judge = sub.add_parser("judge", help="deterministic judgment (no model call)")
    p_judge.add_argument("--claude-artifact", required=True)
    p_judge.add_argument("--gpt-artifact", required=True)
    p_judge.add_argument("--disagreements", required=True)
    p_judge.add_argument("--claude-falsification", required=True)
    p_judge.add_argument("--gpt-falsification", required=True)
    p_judge.add_argument("--out", required=True)
    p_judge.set_defaults(func=cmd_judge)

    p_persist = sub.add_parser("persist", help="write falsification + judgment artifacts locally (no git call)")
    p_persist.add_argument("--claude-falsification", required=True)
    p_persist.add_argument("--gpt-falsification", required=True)
    p_persist.add_argument("--judgment", required=True)
    p_persist.add_argument("--falsification-ledger-out", default=DEFAULT_FALSIFICATION_LEDGER)
    p_persist.add_argument("--judgment-ledger-out", default=DEFAULT_JUDGMENT_LEDGER)
    p_persist.set_defaults(func=cmd_persist)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
