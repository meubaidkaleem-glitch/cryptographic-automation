from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_streamlit_app_renders_without_exceptions():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(str(app_path), default_timeout=20).run()
    assert len(app.exception) == 0, [item.message for item in app.exception]
