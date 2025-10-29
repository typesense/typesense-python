from __future__ import annotations

from typesense.client import Client


def is_v30_or_above(client: Client) -> bool:
    try:
        debug = client.debug.retrieve()
        version = debug.get("version")
        if version == "nightly":
            return True
        try:
            version_str = str(version)
            if version_str.startswith("v"):
                numbered = version_str.split("v", 1)[1]
            else:
                numbered = version_str
            major_version = numbered.split(".", 1)[0]
            return int(major_version) >= 30
        except Exception:
            return False
    except Exception:
        return False


