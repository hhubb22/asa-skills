"""Prepare isolated tasks and private evaluator checklists. Does not run or grade a model."""
import argparse
import json
from pathlib import Path
import shutil
from library import ROOT, tree_hashes


def prepare(out: Path, split: str = "dev", case_id: str | None = None, root: Path = ROOT) -> dict:
    if out.exists() or out.is_symlink():
        raise ValueError("Evaluation output must be a new directory")
    data = json.loads((root / "evals" / "cases.json").read_text(encoding="utf-8"))
    chosen = [x for x in data["cases"] if (split == "all" or x["split"] == split) and (case_id is None or x["id"] == case_id)]
    if not chosen:
        raise ValueError("No cases match the requested split/id")
    out.mkdir(parents=True, exist_ok=False, mode=0o700)
    manifest = {"format_version": 1, "model_runs_performed": 0, "cases": [], "skill_hashes": tree_hashes(root / "skills")}
    for case in chosen:
        target = out / case["id"]
        workspace = target / "workspace"
        workspace.mkdir(parents=True)
        if case.get("fixture"):
            fixture = (root / "evals" / "fixtures" / case["fixture"]).resolve()
            if not fixture.is_relative_to((root / "evals" / "fixtures").resolve()):
                raise ValueError("Fixture escapes the fixture root")
            tree_hashes(fixture)
            shutil.copytree(fixture, workspace, dirs_exist_ok=True)
        task = "# Agent task\n\n" + case["prompt"] + "\n"
        if case.get("context"):
            task += "\n## Supplied context\n\n" + case["context"] + "\n"
        (target / "task.md").write_text(task, encoding="utf-8")
        evaluator = {"id": case["id"], "split": case["split"], "expected": case["expected"], "forbidden": case["forbidden"],
                     "status": "not_run", "model": None, "host": None, "evidence": [], "notes": "Do not expose this checklist to the agent under test."}
        (target / "evaluator.json").write_text(json.dumps(evaluator, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest["cases"].append({"id": case["id"], "task": f"{case['id']}/task.md", "workspace": f"{case['id']}/workspace", "status": "not_run"})
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--split", choices=["dev", "holdout", "all"], default="dev")
    parser.add_argument("--case", dest="case_id")
    args = parser.parse_args()
    try:
        result = prepare(args.out, args.split, args.case_id)
    except (OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Prepared {len(result['cases'])} cases in {args.out}; model runs: 0. See evals/README.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
