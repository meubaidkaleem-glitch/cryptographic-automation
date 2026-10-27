"""AutoCrypt Windows desktop launcher."""
from __future__ import annotations
import os, socket, subprocess, sys, time, threading, urllib.request
from pathlib import Path
import webview

def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])

def main() -> None:
    root = app_root()
    app_file = root / "app.py"
    if not app_file.exists():
        import tkinter as tk
        from tkinter import messagebox
        window = tk.Tk()
        window.withdraw()
        messagebox.showerror("AutoCrypt", f"Could not find app.py in:\n{root}")
        return
    port = free_port()
    url = f"http://127.0.0.1:{port}"
    env = os.environ.copy()
    env.update({
        "STREAMLIT_BROWSER_GATHER_USAGE_STATS": "false",
        "STREAMLIT_SERVER_HEADLESS": "true",
        "STREAMLIT_SERVER_ADDRESS": "127.0.0.1",
        "STREAMLIT_SERVER_PORT": str(port),
        "STREAMLIT_SERVER_ENABLE_CORS": "false",
        "STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION": "true",
        "PYTHONUTF8": "1",
    })
    # The release workflow includes the Python runtime separately so the
    # Streamlit server can run while this executable hosts the desktop window.
    if getattr(sys, "frozen", False):
        python = root / "runtime" / "python.exe"
        command = [str(python), "-m", "streamlit", "run", str(app_file),
                   "--server.address=127.0.0.1", f"--server.port={port}",
                   "--server.headless=true", "--browser.gatherUsageStats=false"]
    else:
        command = [sys.executable, "-m", "streamlit", "run", str(app_file),
                   "--server.address=127.0.0.1", f"--server.port={port}",
                   "--server.headless=true", "--browser.gatherUsageStats=false"]
    process = subprocess.Popen(command, cwd=str(root), env=env, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    def wait_until_ready() -> None:
        deadline = time.time() + 90
        while time.time() < deadline and process.poll() is None:
            try:
                with urllib.request.urlopen(url, timeout=1) as response:
                    if response.status < 500:
                        return
            except Exception:
                pass
            time.sleep(0.4)
    threading.Thread(target=wait_until_ready, daemon=True).start()
    try:
        webview.create_window("AutoCrypt", url, width=1440, height=900, min_size=(1000, 650))
        webview.start()
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()

if __name__ == "__main__":
    main()
