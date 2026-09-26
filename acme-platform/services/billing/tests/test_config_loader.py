import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config_loader import load_invoice_rules, load_tax_table


def test_invoice_rules(tmp_path):
    p = tmp_path / "rules.yaml"
    p.write_text("currency: USD\nnet_days: 30\n")
    assert load_invoice_rules(str(p)) == {"currency": "USD", "net_days": 30}


def test_tax_table():
    assert load_tax_table("ID: 0.11\nSG: 0.09\n") == {"ID": 0.11, "SG": 0.09}
