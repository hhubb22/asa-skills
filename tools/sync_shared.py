"""Materialize shared references, attribution and licenses into standalone skills."""
import argparse
from library import generated_files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report drift without writing")
    args = parser.parse_args()
    changed = []
    for path, data in generated_files().items():
        if not path.exists() or path.read_bytes() != data:
            changed.append(path)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
    print(f"{'Drift' if args.check else 'Updated'}: {len(changed)} file(s)")
    for path in changed:
        print(path)
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
