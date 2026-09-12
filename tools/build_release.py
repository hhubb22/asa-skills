"""Build a deterministic ZIP, file manifest and archive checksum after structural checks."""
import argparse
import hashlib
from pathlib import Path
import zipfile
from library import ROOT, check

EXCLUDED = {".git", ".local", "dist", "__pycache__", ".venv"}


def release_files(root: Path) -> list[Path]:
    result = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in EXCLUDED for part in rel.parts) or path.suffix in {".pyc", ".pyo"}:
            continue
        if path.name in {".DS_Store", "MANIFEST.sha256"}:
            continue
        if path.is_symlink():
            raise ValueError(f"Release cannot include a symlink: {rel}")
        if path.is_file():
            result.append(path)
    return result


def build(out: Path, root: Path = ROOT) -> tuple[Path, str]:
    resolved_out = out.resolve()
    resolved_root = root.resolve()
    if resolved_out.is_relative_to(resolved_root) and not resolved_out.is_relative_to(resolved_root / "dist"):
        raise ValueError("An in-repository release directory must be under dist/ to avoid archiving prior outputs")
    errors, _ = check(root)
    if errors:
        raise ValueError("Structural checks failed:\n" + "\n".join(errors))
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    prefix = f"asa-skills-v{version}"
    files = release_files(root)
    manifest = "".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(root).as_posix()}\n" for p in files)
    manifest_path = root / "MANIFEST.sha256"
    manifest_path.write_text(manifest, encoding="utf-8")
    out.mkdir(parents=True, exist_ok=True)
    archive = out / f"{prefix}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for path in files + [manifest_path]:
            info = zipfile.ZipInfo(f"{prefix}/{path.relative_to(root).as_posix()}", date_time=(2026, 9, 12, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            package.writestr(info, path.read_bytes())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (out / f"{prefix}.zip.sha256").write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    return archive, digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    try:
        archive, digest = build(args.out)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(archive)
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
