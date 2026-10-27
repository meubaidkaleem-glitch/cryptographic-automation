from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .crypto import hash_file
from .detect import detect_sample


@dataclass
class Job:
    id: str
    action: str
    input: str
    algorithm: str = "sha256"
    output: str = ""


def load_jobs(path: str | Path) -> list[Job]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Job(**item) for item in payload.get("jobs", [])]


def save_jobs(path: str | Path, jobs: list[Job]) -> None:
    Path(path).write_text(json.dumps({"jobs": [asdict(job) for job in jobs]}, indent=2), encoding="utf-8")


def run_job(job: Job) -> dict[str, Any]:
    if job.action == "hash":
        digest = hash_file(job.input, job.algorithm)
        if job.output:
            Path(job.output).write_text(digest + "\n", encoding="utf-8")
        return {"id": job.id, "status": "completed", "digest": digest, "output": job.output}
    if job.action == "detect":
        sample = Path(job.input).read_text(encoding="utf-8")
        results = [asdict(item) for item in detect_sample(sample)]
        if job.output:
            Path(job.output).write_text(json.dumps(results, indent=2), encoding="utf-8")
        return {"id": job.id, "status": "completed", "results": results}
    if job.action == "inspect-file":
        p = Path(job.input)
        return {"id": job.id, "status": "completed", "file": str(p), "size": p.stat().st_size}
    raise ValueError(f"Unsupported job action: {job.action}")


def run_jobs(jobs: list[Job]) -> list[dict[str, Any]]:
    results = []
    for job in jobs:
        try:
            results.append(run_job(job))
        except Exception as exc:
            results.append({"id": job.id, "status": "failed", "error": str(exc)})
    return results
