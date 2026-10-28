"""Bootstrap and invoke pinned shared tools, never copy or fork their implementation.

Readiness requires more than files existing: an immutable clean checkout, a
current content-bound template contract, and an explicitly assigned method lane
must all pass.  A successful preflight never authorizes a weekly slot.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TEMPLATE = ROOT / ".work/template"


def _pin() -> dict:
    from scripts.audit_shared_template import load_pin
    return load_pin(ROOT / "registry/template.json")


def bootstrap() -> None:
    """Materialize the immutable pin; update only a clean regenerable checkout."""
    pin = _pin()
    template = ROOT / ".work/template"
    if not template.exists():
        template.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", "--no-checkout", "https://github.com/" + pin["repository"] + ".git", str(template)],
            check=True,
        )
    if not (template / ".git").is_dir():
        raise SystemExit("Shared template path exists but is not a git checkout")
    if subprocess.check_output(["git", "-C", str(template), "status", "--porcelain"], text=True).strip():
        raise SystemExit("Shared template has modifications; no private fork permitted")
    actual = subprocess.check_output(["git", "-C", str(template), "rev-parse", "HEAD"], text=True).strip()
    if actual != pin["commit"]:
        # The cache may contain an earlier immutable pin. Fetch and detach at the
        # reviewed commit; never merge or edit shared source locally.
        subprocess.run(["git", "-C", str(template), "fetch", "origin", pin["commit"]], check=True)
        subprocess.run(["git", "-C", str(template), "checkout", "--detach", pin["commit"]], check=True)
    actual = subprocess.check_output(["git", "-C", str(template), "rev-parse", "HEAD"], text=True).strip()
    if actual != pin["commit"]:
        raise SystemExit("Template commit mismatch; refusing execution")
    if subprocess.check_output(["git", "-C", str(template), "status", "--porcelain"], text=True).strip():
        raise SystemExit("Shared template has modifications; no private fork permitted")


def preflight() -> dict:
    from scripts.audit_shared_template import AUDITED_RUNTIME_ASSETS, verify_contract_for_preflight

    pin = _pin()
    needed = [ROOT / rel for rel in AUDITED_RUNTIME_ASSETS]
    lane = pin.get("method_lane")
    lane_valid = isinstance(lane, str) and bool(lane.strip())
    missing = [str(path.relative_to(ROOT)) for path in needed if not path.is_file()]
    contract = verify_contract_for_preflight(
        ROOT,
        ROOT / ".work/template",
        pin,
        ROOT / "registry/template_contract.json",
    )
    ready = lane_valid and not missing and contract["passed"]
    return {
        "lane": lane,
        "lane_assigned": lane_valid,
        "missing": missing,
        "template_repository": pin["repository"],
        "template_commit": pin["commit"],
        "template_contract": contract,
        "ready_for_shared_tools": ready,
        "ok_to_submit": False,
        "scope": "Input, lane, immutable checkout and shared-tool contract readiness only; not scientific validation or slot selection.",
    }


def _run_audit(args: list[str]) -> int:
    from scripts.audit_shared_template import main as audit_main

    old = sys.argv
    try:
        sys.argv = ["audit_shared_template.py", *args]
        return audit_main()
    finally:
        sys.argv = old


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["bootstrap", "audit", "preflight", "evaluate", "write"])
    parser.add_argument("args", nargs=argparse.REMAINDER)
    opts = parser.parse_args()
    if opts.command == "bootstrap":
        bootstrap()
        return 0
    if opts.command == "audit":
        bootstrap()
        return _run_audit(opts.args)
    report = preflight()
    if opts.command == "preflight":
        print(json.dumps(report, indent=2))
        return 0 if report["ready_for_shared_tools"] else 1
    if not report["ready_for_shared_tools"]:
        raise SystemExit("BLOCKED: lane / cached inputs / shared contract not ready. " + json.dumps(report))
    bootstrap()
    target = "evaluate_holdout.py" if opts.command == "evaluate" else "submission_writer.py"
    env = dict(
        os.environ,
        GEMS_DATA_DIR=str(ROOT / ".cache/gems_data"),
        GEMS_WORK_DIR=str(ROOT / ".cache/gems_work"),
    )
    subprocess.run([sys.executable, str(ROOT / ".work/template/scripts" / target), *opts.args], env=env, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
