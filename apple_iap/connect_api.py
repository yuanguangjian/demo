"""App Store Connect API 客户端（原 `apple/appstoreconnect.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import json
from typing import Any, Dict, List, Optional

from common.http_client import HttpClient
from common.logger import get_logger

from .token import AppleToken

_logger = get_logger(__name__)

API_BASE = "https://api.appstoreconnect.apple.com"
_DEFAULT_APP_ID = "6499123394"


class ConnectApiClient:
    def __init__(self, app_id: str = _DEFAULT_APP_ID, *, token: Optional[AppleToken] = None) -> None:
        self.app_id = app_id
        self.token = token or AppleToken()
        self.client = HttpClient(API_BASE)

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": "Bearer " + self.token.get_connect_token(),
            "Content-Type": "application/json",
        }

    def get_in_app_purchase_products(self) -> List[Dict[str, Any]]:
        """非订阅内购列表。"""
        resp = self.client.get(f"/v1/apps/{self.app_id}/inAppPurchasesV2", headers=self._headers)
        payload = resp.json() if resp.content else {}
        products: List[Dict[str, Any]] = []
        for item in payload.get("data") or []:
            attrs = item.get("attributes") or {}
            products.append(
                {
                    "type": item.get("type"),
                    "id": item.get("id"),
                    "name": attrs.get("name"),
                    "productId": attrs.get("productId"),
                    "inAppPurchaseType": attrs.get("inAppPurchaseType"),
                    "state": attrs.get("state"),
                }
            )
        _logger.info(json.dumps(products, indent=4, ensure_ascii=False))
        return products

    def get_subscription_groups(self) -> List[Dict[str, str]]:
        resp = self.client.get(f"/v1/apps/{self.app_id}/subscriptionGroups", headers=self._headers)
        payload = resp.json() if resp.content else {}
        return [
            {"name": item["attributes"]["referenceName"], "id": item["id"]}
            for item in payload.get("data") or []
        ]

    def get_products_by_group(self) -> List[Dict[str, Any]]:
        """每个订阅组及其下的订阅产品。"""
        groups = self.get_subscription_groups()
        result: List[Dict[str, Any]] = []
        for group in groups:
            resp = self.client.get(
                f"/v1/subscriptionGroups/{group['id']}/subscriptions", headers=self._headers
            )
            payload = resp.json() if resp.content else {}
            items = []
            for item in payload.get("data") or []:
                attrs = item.get("attributes") or {}
                items.append(
                    {
                        "id": item.get("id"),
                        "name": attrs.get("name"),
                        "productId": attrs.get("productId"),
                        "subscriptionPeriod": attrs.get("subscriptionPeriod"),
                        "state": attrs.get("state"),
                        "groupLevel": attrs.get("groupLevel"),
                    }
                )
            items.sort(key=lambda x: x.get("groupLevel") or 0)
            result.append({"groupName": group["name"], "groupId": group["id"], "items": items})
        _logger.info(json.dumps(result, indent=4, ensure_ascii=False))
        return result

    def get_in_app_purchase_detail(self, product_id: str) -> Optional[Dict[str, Any]]:
        resp = self.client.get(f"/v2/inAppPurchases/{product_id}", headers=self._headers)
        payload = resp.json() if resp.content else {}
        _logger.info(json.dumps(payload, indent=4, ensure_ascii=False))
        return payload

    def get_subscription_detail(self, product_id: str) -> Optional[Dict[str, Any]]:
        resp = self.client.get(f"/v1/subscriptions/{product_id}", headers=self._headers)
        payload = resp.json() if resp.content else {}
        _logger.info(json.dumps(payload, indent=4, ensure_ascii=False))
        return payload


if __name__ == "__main__":
    c = ConnectApiClient()
    c.get_products_by_group()
