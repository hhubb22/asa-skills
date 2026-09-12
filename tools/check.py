"""Validate skill structure, local budgets, links, generated files and Python syntax."""
import argparse
import json
from library import ROOT, check


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors, stats = check(ROOT)
    if args.json:
        print(json.dumps({"ok": not errors, "errors": errors, "stats": stats}, ensure_ascii=False, indent=2))
    else:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"{'PASS' if not errors else 'FAIL'}: {stats['skills']} skills; "
              f"{stats['description_characters']} description characters (not tokens)")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
