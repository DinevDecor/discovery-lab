"""CLI entrypoint for the three GitHub Actions job roles Stage 3 needs:
`prepare` (builds the one immutable evidence packet), `claude` / `gpt`
(each independently consumes that packet and produces its own
IndependentAnalysisArtifact), and `merge` (the only step allowed to see
both outputs together, per CONTRACT.md).

Read-only against CA data. Writes only to files the caller names via
--out/--ledger-out - never to any CA/BCA path.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(ROOT)
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from blind_analysis_kernel.dispatch import build_packet, run_claude_analysis, run_gpt_analysis  # noqa: E402
from blind_analysis_kernel.identity import default_run_id  # noqa: E402
from blind_analysis_kernel.ledger import AnalysisLedger  # noqa: E402
from blind_analysis_kernel.models import IndependentAnalysisArtifact  # noqa: E402
from blind_analysis_kernel.packet import EvidencePacket, packet_sha256  # noqa: E402

DEFAULT_CA_ANOMALIES = os.path.join(REPO_ROOT, "constraint-archaeology-agents", "data", "anomalies.json")
DEFAULT_CA_OBSERVATIONS = os.path.join(REPO_ROOT, "constraint-archaeology-agents", "data", "observations.jsonl")
DEFAULT_LEDGER_PATH = os.path.join(ROOT, "data", "analyses.jsonl")


def _load_anomalies(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return {a["anomaly_id"]: a for a in json.load(f)}


def _load_observations(path: str) -> dict:
    by_id = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            o = json.loads(line)
            by_id[o["observation_id"]] = o
    return by_id


def cmd_prepare(args: argparse.Namespace) -> None:
    anomalies = _load_anomalies(args.ca_anomalies_path)
    observations = _load_observations(args.ca_observations_path)
    if args.anomaly_id not in anomalies:
        raise SystemExit(f"anomaly_id {args.anomaly_id!r} not found in {args.ca_anomalies_path}")
    run_id = args.run_id or default_run_id()
    packet = build_packet(anomalies[args.anomaly_id], observations, run_id)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(packet.to_dict(), f, sort_keys=True, ensure_ascii=False, indent=2)
    print(json.dumps({
        "run_id": run_id,
        "anomaly_id": args.anomaly_id,
        "source_case_ids": packet.source_case_ids,
        "packet_sha256": packet_sha256(packet),
        "packet_path": args.out,
    }, indent=2, sort_keys=True))


def _load_packet(path: str) -> EvidencePacket:
    with open(path, encoding="utf-8") as f:
        return EvidencePacket.from_dict(json.load(f))


def cmd_claude(args: argparse.Namespace) -> None:
    packet = _load_packet(args.packet)
    artifact = run_claude_analysis(packet)  # raises loudly if ANTHROPIC_API_KEY missing/transport fails
    _write_artifact(artifact, args.out)


def cmd_gpt(args: argparse.Namespace) -> None:
    packet = _load_packet(args.packet)
    artifact = run_gpt_analysis(packet)  # raises loudly if OPENAI_API_KEY missing/transport fails
    _write_artifact(artifact, args.out)


def _write_artifact(artifact: IndependentAnalysisArtifact, out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(artifact.to_dict(), f, sort_keys=True, ensure_ascii=False, indent=2, default=str)
    print(json.dumps({
        "artifact_id": artifact.artifact_id,
        "provider": artifact.provider,
        "model": artifact.model,
        "run_id": artifact.run_id,
        "source_case_ids": artifact.source_case_ids,
        "input_packet_sha256": artifact.input_packet_sha256,
        "artifact_path": out_path,
    }, indent=2, sort_keys=True))


def cmd_merge(args: argparse.Namespace) -> None:
    with open(args.claude_artifact, encoding="utf-8") as f:
        claude_data = json.load(f)
    with open(args.gpt_artifact, encoding="utf-8") as f:
        gpt_data = json.load(f)
    claude_artifact = IndependentAnalysisArtifact(**claude_data)
    gpt_artifact = IndependentAnalysisArtifact(**gpt_data)

    ledger = AnalysisLedger(args.ledger_out)
    claude_written = ledger.append(claude_artifact)
    gpt_written = ledger.append(gpt_artifact)

    reveal = {
        "run_id": claude_artifact.run_id,
        "claude_artifact_id": claude_artifact.artifact_id,
        "gpt_artifact_id": gpt_artifact.artifact_id,
        "artifact_ids_distinct": claude_artifact.artifact_id != gpt_artifact.artifact_id,
        "source_case_ids_identical": claude_artifact.source_case_ids == gpt_artifact.source_case_ids,
        "input_packet_sha256_claude": claude_artifact.input_packet_sha256,
        "input_packet_sha256_gpt": gpt_artifact.input_packet_sha256,
        "input_packet_sha256_match": claude_artifact.input_packet_sha256 == gpt_artifact.input_packet_sha256,
        "claude_written": claude_written,
        "gpt_written": gpt_written,
        "ledger_path": args.ledger_out,
    }
    print(json.dumps(reveal, indent=2, sort_keys=True))
    # Task §10 STOP boundary: no semantic comparison, no combined
    # conclusion, no lifecycle change happens below this line - the CLI
    # exits here.


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="role", required=True)

    p_prepare = sub.add_parser("prepare", help="build the one immutable evidence packet")
    p_prepare.add_argument("--anomaly-id", default="ANOM-0001")
    p_prepare.add_argument("--run-id", default=None, help="defaults to a fresh generated id; pass github.run_id in CI")
    p_prepare.add_argument("--ca-anomalies-path", default=DEFAULT_CA_ANOMALIES)
    p_prepare.add_argument("--ca-observations-path", default=DEFAULT_CA_OBSERVATIONS)
    p_prepare.add_argument("--out", required=True)
    p_prepare.set_defaults(func=cmd_prepare)

    p_claude = sub.add_parser("claude", help="independent Claude analysis of the packet")
    p_claude.add_argument("--packet", required=True)
    p_claude.add_argument("--out", required=True)
    p_claude.set_defaults(func=cmd_claude)

    p_gpt = sub.add_parser("gpt", help="independent GPT analysis of the packet")
    p_gpt.add_argument("--packet", required=True)
    p_gpt.add_argument("--out", required=True)
    p_gpt.set_defaults(func=cmd_gpt)

    p_merge = sub.add_parser("merge", help="reveal + persist both artifacts (only step that sees both)")
    p_merge.add_argument("--claude-artifact", required=True)
    p_merge.add_argument("--gpt-artifact", required=True)
    p_merge.add_argument("--ledger-out", default=DEFAULT_LEDGER_PATH)
    p_merge.set_defaults(func=cmd_merge)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
