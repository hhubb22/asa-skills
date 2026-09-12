"""Copy selected skills. Dry-run by default; reject unmanaged or locally edited targets."""
import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile
import uuid
from library import ROOT, NAME_RE, catalog, tree_hashes

MARKER = ".asa-skills-install.json"
LOCK = ".asa-skills-install.lock"


def load_manifest(dest: Path) -> dict:
    path = dest / MARKER
    if path.is_symlink():
        raise ValueError("Refusing a symlink install manifest")
    if not path.exists():
        return {"format_version": 1, "skills": {}}
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or obj.get("format_version") != 1 or not isinstance(obj.get("skills"), dict):
        raise ValueError("Unrecognized installation manifest")
    for name, record in obj["skills"].items():
        if not NAME_RE.fullmatch(name) or not isinstance(record, dict) or not isinstance(record.get("hashes"), dict):
            raise ValueError("Invalid manifest entry")
    return obj


def plan(dest: Path, names: list[str], update: bool = False, root: Path = ROOT) -> tuple[list[tuple[str, str]], dict]:
    if dest.is_symlink() or (dest.exists() and not dest.is_dir()):
        raise ValueError("Destination must be a non-symlink directory")
    available = {x["name"] for x in catalog(root)["skills"]}
    if not names or len(names) != len(set(names)) or set(names) - available:
        raise ValueError("Choose unique names from catalog.json")
    manifest = load_manifest(dest)
    actions = []
    for name in names:
        desired = tree_hashes(root / "skills" / name)
        target = dest / name
        if target.is_symlink():
            raise ValueError(f"Refusing symlink target: {name}")
        if not target.exists():
            actions.append((name, "install"))
            continue
        old = manifest["skills"].get(name)
        if old is None:
            raise ValueError(f"Unmanaged destination already exists: {name}. Select another directory or resolve it manually.")
        current = tree_hashes(target)
        if current != old["hashes"]:
            raise ValueError(f"Locally changed installation: {name}. Preserve and reconcile edits before updating.")
        if current == desired:
            actions.append((name, "skip"))
        elif not update:
            raise ValueError(f"Managed older installation: {name}. Re-run with --update after reviewing changes.")
        else:
            actions.append((name, "update"))
    return actions, manifest


def install(dest: Path, names: list[str], *, apply: bool = False, update: bool = False, root: Path = ROOT) -> list[tuple[str, str]]:
    dest = dest.expanduser().absolute()
    actions, manifest = plan(dest, names, update, root)
    if not apply or all(action == "skip" for _, action in actions):
        return actions
    dest.mkdir(parents=True, exist_ok=True)
    fd = os.open(dest / LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    stage = None
    backup = None
    installed: list[Path] = []
    moved: list[tuple[Path, Path]] = []
    try:
        # Recheck after acquiring the process lock; manual concurrent edits remain unsupported.
        actions, manifest = plan(dest, names, update, root)
        stage = Path(tempfile.mkdtemp(prefix=".asa-skills-stage-", dir=dest.parent))
        for name, action in actions:
            if action != "skip":
                shutil.copytree(root / "skills" / name, stage / name)
        for name, action in actions:
            if action == "skip":
                continue
            target = dest / name
            if action == "update":
                if backup is None:
                    backup_store = dest.parent / ".asa-skills-backups"
                    if backup_store.is_symlink():
                        raise ValueError("Refusing symlink backup directory")
                    backup = backup_store / uuid.uuid4().hex
                    backup.mkdir(parents=True, mode=0o700)
                old_path = backup / name
                target.rename(old_path)
                moved.append((old_path, target))
            (stage / name).rename(target)
            installed.append(target)
            manifest["skills"][name] = {"version": catalog(root)["version"], "hashes": tree_hashes(target)}
        manifest["last_package_version"] = catalog(root)["version"]
        temporary_manifest = stage / "manifest.json"
        temporary_manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary_manifest, dest / MARKER)
    except Exception:
        for target in reversed(installed):
            if target.exists():
                shutil.rmtree(target)
        for old_path, target in reversed(moved):
            if old_path.exists():
                old_path.rename(target)
        raise
    finally:
        if stage is not None and stage.exists():
            shutil.rmtree(stage)
        (dest / LOCK).unlink(missing_ok=True)
    if backup is not None:
        print(f"Backup retained outside skill discovery root: {backup}")
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", required=True, type=Path, help="Explicit skill root, for example ~/.agents/skills")
    parser.add_argument("--only", nargs="+", metavar="SKILL", help="Selected names; default: all 11")
    parser.add_argument("--apply", action="store_true", help="Write the planned installation")
    parser.add_argument("--update", action="store_true", help="Permit replacing an unchanged, previously managed installation")
    args = parser.parse_args()
    names = args.only or [x["name"] for x in catalog()["skills"]]
    try:
        actions = install(args.dest, names, apply=args.apply, update=args.update)
        for name, action in actions:
            print(f"{action}: {name}")
        print("Applied requested changes." if args.apply else "Dry run only. Add --apply to write.")
        if "work" in names and len(names) < len(catalog()["skills"]):
            print("Note: work can only call installed skills; this subset may use direct-work fallbacks.")
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
