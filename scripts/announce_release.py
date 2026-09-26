"""Announce a distributed app version in app-config.json (the soft-update banner).

Run by .github/workflows/announce-release.yml, only after the release is
installable by every reader of this policy. Just latest_version and update_url
change: raising minimum_version locks users out, so that stays a separate,
deliberate edit.
"""

import json
import os
import re
import sys
from pathlib import Path

CONFIG = Path(__file__).resolve().parent.parent / "app-config.json"
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def parse_version(version: str) -> tuple[int, int, int]:
    match = SEMVER.match(version or "")
    if not match:
        raise ValueError(f"not an X.Y.Z version: {version!r}")
    major, minor, patch = (int(part) for part in match.groups())
    return major, minor, patch


def announce(config: dict, version: str, url: str) -> dict:
    """Return a copy of config announcing version at url; reject unsafe changes."""
    new = parse_version(version)
    current = config.get("latest_version")
    if current and new <= parse_version(current):
        raise ValueError(f"{version} is not newer than the announced {current}")
    if not url.startswith("https://"):
        raise ValueError("update_url must be an https link the audience can open")
    return {**config, "latest_version": version, "update_url": url}


def main() -> int:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    try:
        updated = announce(
            config,
            os.environ.get("LATEST_VERSION", "").strip(),
            os.environ.get("UPDATE_URL", "").strip(),
        )
    except ValueError as error:
        print(f"::error::{error}")
        return 1
    CONFIG.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"app-config.json now announces {updated['latest_version']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
