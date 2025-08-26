from __future__ import annotations

from typesense.client import Client


def is_v30_or_above(client: Client) -> bool:
    try:
        debug = client.debug.retrieve()
        version = debug.get("version")
        if version == "nightly":
            return True
        try:
            numbered = str(version).split("v")[1]
            return int(numbered) >= 30
        except Exception:
            return False
    except Exception:
        return False


