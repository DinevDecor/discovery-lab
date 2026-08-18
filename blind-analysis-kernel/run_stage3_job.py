"""CLI entrypoint for the GitHub Actions job roles Stage 3/3B need:
`prepare` (builds the one immutable evidence packet), `claude` / `gpt`
(each independently consumes that packet and produces its own
IndependentAnalysisArtifact), `merge` (the only step allowed to see both
outputs together - verifies structural integrity and refuses to proceed
on a mismatch, per CONTRACT.md), and `persist` (Stage 3B: the ONLY
subcommand any workflow step may call with `contents: write` - durably
appends both artifacts plus a run manifest to Git-tracked files).

Read-only against CA data. `prepare`/`claude`/`gpt`/`merge` write only to
files the caller names via --out/--ledger-out - never to any CA/BCA path,
never to Git. `persist` writes to --ledger-out/--manifest-out only (the
calling workflow step is responsible for `git add`/`commit`/`push` of
exactly those paths - this script never invokes git itself).
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

from blind_analysis_kernel.dispatch import build_packet, run_claude_analysis, run_gpt_analysis  # noqa: E402
from blind_analysis_kernel.identity import default_run_id  # noqa: E402
from blind_analysis_kernel.ledger import AnalysisLedger  # noqa: E402
from blind_analysis_kernel.manifest import RunManifestLedger, build_run_manifest  # noqa: E402
from blind_analysis_kernel.models import IndependentAnalysisArtifact  # noqa: E402
from blind_analysis_kernel.packet import EvidencePacket, packet_sha256  # noqa: E402

DEFAULT_CA_ANOMALIES = os.path.join(REPO_ROOT, "constraint-archaeology-agents", "data", "anomalies.json")
DEFAULT_CA_OBSERVATIONS = os.path.join(REPO_ROOT, "constraint-archaeology-agents", "data", "observations.jsonl")
DEFAULT_LEDGER_PATH = os.path.join(ROOT, "data", "analyses.jsonl")
DEFAULT_MANIFEST_PATH = os.path.join(ROOT, "data", "runs.jsonl")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class StructuralIntegrityError(SystemExit):
    """Raised (as a SystemExit subclass, so it exits the process with a
    non-zero code and a clear message) when the two providers'
    artifacts disagree on something that must always match. Both
    `merge` and `persist` use this - `merge` so a broken run is caught
    immediately after reveal, `persist` so it is never possible to
    durably write a structurally-inconsistent pair to Git even if
    `persist` is ever invoked without `merge` having run first."""

    def __init__(self, message: str):
        super().__init__(f"structural integrity check failed: {message}")


def _check_structural_integrity(claude_artifact: IndependentAnalysisArtifact,
                                 gpt_artifact: IndependentAnalysisArtifact) -> None:
    if claude_artifact.artifact_id == gpt_artifact.artifact_id:
        raise StructuralIntegrityError("claude and gpt artifact_id collided")
    if claude_artifact.input_packet_sha256 != gpt_artifact.input_packet_sha256:
        raise StructuralIntegrityError(
            f"input_packet_sha256 mismatch: claude={claude_artifact.input_packet_sha256!r} "
            f"gpt={gpt_artifact.input_packet_sha256!r}")
    if claude_artifact.source_case_ids != gpt_artifact.source_case_ids:
        raise StructuralIntegrityError(
            f"source_case_ids mismatch: claude={claude_artifact.source_case_ids!r} "
            f"gpt={gpt_artifact.source_case_ids!r}")
    if claude_artifact.run_id != gpt_artifact.run_id:
        raise StructuralIntegrityError(
            f"run_id mismatch: claude={claude_artifact.run_id!r} gpt={gpt_artifact.run_id!r}")


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

    # Verify BEFORE writing anything - a structurally broken pair must
    # never reach the ledger, local or Git. This is the "merge-reveal
    # verifies structural integrity" gate Stage 3B's persist step relies
    # on running first (persist re-checks independently too - see
    # _check_structural_integrity's docstring).
    _check_structural_integrity(claude_artifact, gpt_artifact)

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
    # exits here. Stage 3B's durable Git persistence is a SEPARATE
    # subcommand (`persist`, below), run by a separate job with its own
    # `contents: write` permission - this job/subcommand never touches git.


def cmd_persist(args: argparse.Namespace) -> None:
    """Stage 3B. The only subcommand that a `contents: write` workflow
    step may call. Writes to --ledger-out/--manifest-out ONLY - never
    calls git itself; the calling workflow step owns `git add`/`commit`/
    `push` (see .github/workflows/stage3-blind-dispatch.yml's
    `persist-to-git` job) so this script's own behavior stays fully
    testable offline, exactly like every other subcommand here.
    """
    with open(args.claude_artifact, encoding="utf-8") as f:
        claude_data = json.load(f)
    with open(args.gpt_artifact, encoding="utf-8") as f:
        gpt_data = json.load(f)
    claude_artifact = IndependentAnalysisArtifact(**claude_data)
    gpt_artifact = IndependentAnalysisArtifact(**gpt_data)

    # Re-checked independently of `merge` (defense in depth - this
    # subcommand must never durably write a broken pair to Git even if
    # invoked on its own).
    _check_structural_integrity(claude_artifact, gpt_artifact)

    ledger = AnalysisLedger(args.ledger_out)
    claude_written = ledger.append(claude_artifact)
    gpt_written = ledger.append(gpt_artifact)

    manifest = build_run_manifest(
        claude_artifact, gpt_artifact,
        workflow_run_id=args.workflow_run_id,
        head_sha=args.head_sha,
        created_at=utc_now_iso(),
    )
    manifest_ledger = RunManifestLedger(args.manifest_out)
    manifest_written = manifest_ledger.append(manifest)

    print(json.dumps({
        "run_id": claude_artifact.run_id,
        "workflow_run_id": args.workflow_run_id,
        "head_sha": args.head_sha,
        "claude_artifact_id": claude_artifact.artifact_id,
        "gpt_artifact_id": gpt_artifact.artifact_id,
        "claude_written": claude_written,
        "gpt_written": gpt_written,
        "manifest_id": manifest.manifest_id,
        "manifest_written": manifest_written,
        "any_new_content": claude_written or gpt_written or manifest_written,
        "ledger_path": args.ledger_out,
        "manifest_path": args.manifest_out,
    }, indent=2, sort_keys=True))


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

    p_merge = sub.add_parser("merge", help="reveal both artifacts + verify structural integrity (only step that sees both)")
    p_merge.add_argument("--claude-artifact", required=True)
    p_merge.add_argument("--gpt-artifact", required=True)
    p_merge.add_argument("--ledger-out", default=DEFAULT_LEDGER_PATH)
    p_merge.set_defaults(func=cmd_merge)

    p_persist = sub.add_parser("persist", help="Stage 3B: durable Git persistence (contents: write step only)")
    p_persist.add_argument("--claude-artifact", required=True)
    p_persist.add_argument("--gpt-artifact", required=True)
    p_persist.add_argument("--ledger-out", default=DEFAULT_LEDGER_PATH)
    p_persist.add_argument("--manifest-out", default=DEFAULT_MANIFEST_PATH)
    p_persist.add_argument("--workflow-run-id", required=True)
    p_persist.add_argument("--head-sha", required=True)
    p_persist.set_defaults(func=cmd_persist)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
