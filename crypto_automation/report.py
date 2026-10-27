from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from typing import Iterable


def event(action: str, detail: str, status: str = "success") -> dict[str, str]:
    return {"timestamp": datetime.now(timezone.utc).isoformat(), "action": action, "status": status, "detail": detail}


def to_json(events: Iterable[dict[str, str]]) -> bytes:
    return json.dumps(list(events), indent=2, ensure_ascii=False).encode("utf-8")


def to_csv(events: Iterable[dict[str, str]]) -> bytes:
    rows = list(events)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["timestamp", "action", "status", "detail"])
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def markdown_report(events: Iterable[dict[str, str]], title: str = "Cryptographic Automation Report") -> bytes:
    rows = list(events)
    lines = [f"# {title}", "", f"Events: {len(rows)}", "", "| Timestamp | Action | Status | Detail |", "|---|---|---|---|"]
    for row in rows:
        detail = row.get("detail", "").replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {row.get('timestamp','')} | {row.get('action','')} | {row.get('status','')} | {detail} |")
    return ("\n".join(lines) + "\n").encode("utf-8")
