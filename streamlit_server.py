"""Frozen entry point for the bundled Streamlit server."""
from __future__ import annotations
import sys
from pathlib import Path
from streamlit.web.cli import main

def run() -> None:
    if len(sys.argv) < 3:
        raise SystemExit("Expected app.py path and port")
    app_path = str(Path(sys.argv[1]).resolve())
    port = str(sys.argv[2])
    sys.argv = ["streamlit", "run", app_path, "--server.address=127.0.0.1",
                f"--server.port={port}", "--server.headless=true",
                "--browser.gatherUsageStats=false"]
    main()

if __name__ == "__main__":
    run()
