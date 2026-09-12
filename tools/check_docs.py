"""Check documents that explicitly opt into this library's templates; not design correctness."""
import argparse
from pathlib import Path
import re

REQUIRED = {"product": {"Summary", "Behavior"}, "tech": {"Context", "Proposed changes", "Testing and validation"},
            "adr": {"Context", "Decision", "Consequences"}}
STATUSES = {"draft", "proposed", "approved", "implemented", "accepted", "rejected", "deprecated", "superseded"}


def validate(text: str, kind: str, product: str | None = None) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    headings = set(re.findall(r"^##\s+(.+?)\s*$", text, re.M))
    for heading in sorted(REQUIRED[kind] - headings):
        errors.append(f"Missing required section: {heading}")
    status = re.search(r"^Status:\s*(\S+)", text, re.M)
    if not status or status.group(1) not in STATUSES:
        errors.append("Missing or invalid Status field")
    definitions = re.findall(r"^\s*-\s+(R-\d+)\s*[：:]", text, re.M)
    if len(definitions) != len(set(definitions)):
        errors.append("Duplicate requirement identifiers")
    if kind == "product" and not definitions:
        errors.append("No numbered Behavior requirements")
    if kind == "tech":
        refs = set(re.findall(r"\bR-\d+\b", text))
        if product is not None:
            known = set(re.findall(r"^\s*-\s+(R-\d+)\s*[：:]", product, re.M))
            for missing in sorted(refs - known):
                errors.append(f"Unknown requirement: {missing}")
            for missing in sorted(known - refs):
                warnings.append(f"Requirement has no textual reference in TECH: {missing}; inspect coverage")
        elif refs:
            warnings.append("Requirement references not resolved: supply --product for a paired check")
    warnings.append("Structure only: facts, approval, semantic consistency and test coverage require review.")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=sorted(REQUIRED), required=True)
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--product", type=Path)
    args = parser.parse_args()
    try:
        product = args.product.read_text(encoding="utf-8") if args.product else None
        errors, warnings = validate(args.file.read_text(encoding="utf-8"), args.kind, product)
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"NOTE: {message}")
    print("PASS" if not errors else "FAIL")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
