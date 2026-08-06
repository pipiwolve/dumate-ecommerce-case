"""Execute one repeatable scheduled-update cycle for the demo."""

from __future__ import annotations

import json

from shopflow.reporting import simulate_push


if __name__ == "__main__":
    print(json.dumps(simulate_push(), ensure_ascii=False, indent=2))

