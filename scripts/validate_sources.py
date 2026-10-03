"""Validate the complete transmission-spectrum subset of the Zenodo archive."""

import hashlib
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"


def main() -> None:
    manifest = json.loads((DATA / "source_manifest.json").read_text(encoding="utf-8"))
    files = sorted((DATA / manifest["product_directory"]).glob("*.csv"))
    if len(files) != manifest["product_count"]:
        raise SystemExit(f"Expected {manifest['product_count']} products; found {len(files)}")
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.name.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
        digest.update(b"\0")
    actual = digest.hexdigest()
    if actual != manifest["product_set_sha256"]:
        raise SystemExit(f"Product-set hash mismatch: expected {manifest['product_set_sha256']}, got {actual}")
    print(f"Verified {len(files)} products from {manifest['record']}")


if __name__ == "__main__":
    main()
