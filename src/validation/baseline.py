from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASELINE_PATH = Path("artifacts/baseline.json")


def save_baseline(
    profile: dict[str, Any],
) -> None:
    BASELINE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    BASELINE_PATH.write_text(
        json.dumps(
            profile,
            indent=2,
        )
    )


def load_baseline() -> dict[str, Any]:
    if not BASELINE_PATH.exists():
        raise RuntimeError("Baseline not found. Run capture_baseline first.")

    return json.loads(BASELINE_PATH.read_text())


def delete_baseline() -> None:
    BASELINE_PATH.unlink(missing_ok=True)
