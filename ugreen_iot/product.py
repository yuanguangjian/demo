"""产品列表接口（取自 `utils/ugreen_product.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

from typing import Optional

from common.config import env_base_url
from common.http_client import HttpClient


class Product:
    def __init__(self, env: str, country_code: str = "CN") -> None:
        self.env = env
        self.client = HttpClient(env_base_url(env))
        self.country_code = country_code
        self.headers = {
            "content-type": "application/json",
            "x-ugreen-app-system": "ios",
            "language": "zh-Hans",
            "countryCode": country_code,
        }

    def get_product_list(self) -> Optional[dict]:
        return self.client.request_json("GET", "/app/v1/product/model/list_issued_v2", headers=self.headers)

    def get_product_list_v2(self) -> Optional[dict]:
        return self.client.request_json("GET", "/app/v1/product/xxxxx", headers=self.headers)


if __name__ == "__main__":
    product = Product("ces", country_code="us")
    for _ in range(20):
        product.get_product_list()
