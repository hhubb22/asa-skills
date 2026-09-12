"""Small, dependency-free helpers for this library's deliberately narrow format."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
LINK_RE = re.compile(r"\[[^\]\n]+\]\(([^)\n]+)\)")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_meta(path: Path) -> dict[str, str]:
    """Parse the scalar-only YAML emitted by this project, not arbitrary YAML."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"Missing frontmatter: {path}")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"Unterminated frontmatter: {path}") from exc
    result: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ": " not in line:
            raise ValueError(f"Expected a scalar key/value: {path}: {line}")
        key, raw = line.split(": ", 1)
        if key in result:
            raise ValueError(f"Duplicate frontmatter key: {key}")
        value = json.loads(raw) if raw.startswith('"') else raw
        if not isinstance(value, str):
            raise ValueError(f"Expected a string for {key}")
        result[key] = value
    return result


def tree_hashes(root: Path) -> dict[str, str]:
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"Expected a non-symlink directory: {root}")
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlinks are not allowed in a release: {path}")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = sha256(path.read_bytes())
        elif not path.is_dir():
            raise ValueError(f"Unsupported file type: {path}")
    return result


def skill_names(root: Path = ROOT) -> list[str]:
    """Every skills/<name>/SKILL.md directory; the filesystem is the only catalog."""
    return sorted(p.parent.name for p in (root / "skills").glob("*/SKILL.md"))


def generated_files(root: Path = ROOT) -> dict[Path, bytes]:
    lock = json.loads((root / "upstream.lock.json").read_text(encoding="utf-8"))
    generated: dict[Path, bytes] = {}
    for name in skill_names(root):
        target = root / "skills" / name
        generated[target / "references" / "operating-contract.md"] = (
            root / "shared" / "operating-contract.md").read_bytes()
        if name in {"write-product-spec", "write-tech-spec"}:
            generated[target / "references" / "technical-writing.md"] = (
                root / "shared" / "technical-writing.md").read_bytes()
        generated[target / "LICENSE"] = (root / "LICENSE").read_bytes()
        rows = ["# Sources", "", "此文件由 tools/sync_shared.py 生成。正文为本地改版，参考源不代表运行时依赖。", ""]
        for src in lock["skills"].get(name, []):
            rows += [f"- `{src['repository']}/{src['path']}`", f"  - Git blob: `{src['git_blob_sha']}`",
                     f"  - Source: {src['content_url']}", f"  - Change: {src['relation']}"]
        rows += ["", "使用 MIT 许可，作者声明见同目录 LICENSE。", ""]
        generated[target / "SOURCES.md"] = "\n".join(rows).encode("utf-8")
    return generated


def check(root: Path = ROOT) -> tuple[list[str], dict]:
    errors: list[str] = []
    names = skill_names(root)
    lock = json.loads((root / "upstream.lock.json").read_text(encoding="utf-8"))
    for stale in sorted(set(lock["skills"]) - set(names)):
        errors.append(f"upstream.lock.json lists a skill that no longer exists: {stale}")
    stats = {"skills": len(names), "skill_lines": {}, "description_characters": 0}
    for name in names:
        if not NAME_RE.fullmatch(name) or len(name) > 64:
            errors.append(f"Invalid skill name: {name}")
            continue
        base = root / "skills" / name
        path = base / "SKILL.md"
        try:
            meta = read_meta(path)
            if meta.get("name") != name:
                errors.append(f"Directory/name mismatch: {name}")
            desc = meta.get("description", "")
            if not 1 <= len(desc) <= 1024:
                errors.append(f"Invalid description length: {name}")
            if len(desc) > 200:
                errors.append(f"Description exceeds this library's 200-character budget: {name}")
            if set(meta) - {"name", "description", "license", "compatibility"}:
                errors.append(f"Unexpected host-specific field: {name}")
            if len(meta.get("compatibility", "")) > 500:
                errors.append(f"Compatibility too long: {name}")
            stats["description_characters"] += len(desc)
            lines = len(path.read_text(encoding="utf-8").splitlines())
            stats["skill_lines"][name] = lines
            if lines > 120:
                errors.append(f"SKILL.md exceeds library's 120-line budget: {name}")
            tree_hashes(base)
        except (ValueError, OSError, UnicodeError) as exc:
            errors.append(str(exc))
    for path, data in generated_files(root).items():
        if not path.exists() or path.read_bytes() != data:
            errors.append(f"Generated file drift: {path.relative_to(root)}")
    for path in root.rglob("*.md"):
        if any(x in {".local", "__pycache__", ".git"} for x in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        for link in LINK_RE.findall(text):
            if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", link) or link.startswith("#"):
                continue
            target = (path.parent / link.split("#", 1)[0]).resolve()
            if not target.exists():
                errors.append(f"Broken relative link: {path.relative_to(root)} -> {link}")
            if "skills" in path.relative_to(root).parts:
                rel = path.relative_to(root).parts
                own_skill = (root / "skills" / rel[1]).resolve()
                if not target.is_relative_to(own_skill):
                    errors.append(f"Non-portable skill reference: {path.relative_to(root)} -> {link}")
    for path in root.rglob("*.py"):
        if any(x in {".local", ".git"} for x in path.parts):
            continue
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except (SyntaxError, UnicodeError) as exc:
            errors.append(f"Python syntax: {path}: {exc}")
    return errors, stats
