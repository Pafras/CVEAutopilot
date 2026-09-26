import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from renderer import bold, render_badge


def test_badge():
    assert render_badge("New", {"class": "tag"}) == '<span class="tag">New</span>'


def test_bold_escapes():
    assert str(bold("<x>")) == "<b>&lt;x&gt;</b>"
