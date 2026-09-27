"""Run with Python 3.14: python .scorecard-check/test_appearance.py"""
import re
from html.parser import HTMLParser
from pathlib import Path

from streamlit.testing.v1 import AppTest


class VisibleText(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.hidden = False
        self.parts = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self.hidden = True

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self.hidden = False

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)

    def text(self):
        return re.sub(r"[📊🔍✅🪙⚠🛡️🔎⏸\s]+", "", "".join(self.parts))


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    evidence = root / "acme-platform/remediation/sla-dashboard.html"
    original = evidence.read_bytes()
    app = AppTest.from_file(str(root / "app.py")).run()
    assert app.session_state["appearance"] == "Dark"
    metrics = [(m.label, m.value) for m in app.metric]
    for theme, background in (("Light", "#f5f7fa"), ("Dark", "#101820")):
        app.get("button_group")[0].set_value(theme).run()
        assert not app.exception
        assert f"--cva-bg: {background}" in app.get("html")[0].proto.body
        rendered = app.get("iframe")[0].proto.srcdoc
        assert f"--cva-bg: {background}" in rendered
        assert VisibleText(rendered).text() == VisibleText(original.decode()).text()
        assert [(m.label, m.value) for m in app.metric] == metrics
        app.run()
        assert app.session_state["appearance"] == theme
    assert evidence.read_bytes() == original
    print("PASS: both themes, rerun persistence, unchanged metrics and evidence text/file")
