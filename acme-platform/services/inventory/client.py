import requests

SUPPLIER_API = "https://supplier.example.com/api/stock"


def make_session(proxy_url=None):
    s = requests.Session()
    if proxy_url:
        s.proxies = {"https": proxy_url}
    return s


def build_stock_request(sku):
    return requests.Request("GET", SUPPLIER_API, params={"sku": sku}).prepare()
