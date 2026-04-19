"""StoreKit 2 API 客户端（原 `apple/storekit.py`）。"""
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
from .verify import parse_signed_payload

_logger = get_logger(__name__)

PROD_BASE = "https://api.storekit.itunes.apple.com"
SANDBOX_BASE = "https://api.storekit-sandbox.itunes.apple.com"


class StoreKitClient:
    def __init__(self, *, sandbox: bool = True, token: Optional[AppleToken] = None) -> None:
        self.base = SANDBOX_BASE if sandbox else PROD_BASE
        self.token = token or AppleToken()
        self.client = HttpClient(self.base)

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": "Bearer " + self.token.get_storekit_token(),
            "Content-Type": "application/json",
        }

    def get_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """查询单笔订单（`/inApps/v1/transactions/{id}`）。"""
        resp = self.client.get(f"/inApps/v1/transactions/{transaction_id}", headers=self._headers)
        payload = resp.json() if resp.content else {}
        signed = payload.get("signedTransactionInfo")
        if not signed:
            return None
        result = parse_signed_payload(signed)
        _logger.info(json.dumps(result, indent=4, ensure_ascii=False))
        return result

    def get_history(self, transaction_id: str) -> List[Dict[str, Any]]:
        """查询历史订单（按 `purchaseDate` 升序）。"""
        resp = self.client.get(f"/inApps/v2/history/{transaction_id}", headers=self._headers)
        payload = resp.json() if resp.content else {}
        signed_list = payload.get("signedTransactions") or []
        infos = [parse_signed_payload(x) for x in signed_list]
        infos = [i for i in infos if i]
        infos.sort(key=lambda x: x.get("purchaseDate", 0))
        _logger.info(json.dumps(infos, indent=4, ensure_ascii=False))
        return infos

    def get_subscription_status(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """查询订阅状态（`/inApps/v1/subscriptions/{id}`）。"""
        resp = self.client.get(f"/inApps/v1/subscriptions/{transaction_id}", headers=self._headers)
        payload = resp.json() if resp.content else {}
        for data in payload.get("data") or []:
            for transaction in data.get("lastTransactions") or []:
                if transaction.get("signedTransactionInfo"):
                    _logger.info(
                        "用户最新订单：%s",
                        json.dumps(parse_signed_payload(transaction["signedTransactionInfo"]), indent=4, ensure_ascii=False),
                    )
                if transaction.get("signedRenewalInfo"):
                    _logger.info(
                        "用户最新订阅状态：%s",
                        json.dumps(parse_signed_payload(transaction["signedRenewalInfo"]), indent=4, ensure_ascii=False),
                    )
        return payload

    def get_refund_history(self, transaction_id: str) -> List[Dict[str, Any]]:
        resp = self.client.get(f"/inApps/v2/refund/lookup/{transaction_id}", headers=self._headers)
        payload = resp.json() if resp.content else {}
        signed_list = payload.get("signedTransactions") or []
        infos = [parse_signed_payload(x) for x in signed_list if x]
        for info in infos:
            _logger.info(json.dumps(info, indent=4, ensure_ascii=False))
        return infos


if __name__ == "__main__":
    client = StoreKitClient(sandbox=True)
    client.get_transaction("2000001072485485")
    # client.get_history("2000000957610744")
    # client.get_subscription_status("2000001072120255")
    # client.get_refund_history("2000000957610744")
