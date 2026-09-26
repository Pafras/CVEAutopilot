import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from client import build_stock_request, make_session


def test_request_url():
    assert build_stock_request("A1").url.endswith("/api/stock?sku=A1")


def test_proxy():
    assert make_session("http://proxy:3128").proxies["https"] == "http://proxy:3128"
