"""EMQX Dashboard HTTP API demo（原 `ipc项目/emxxx.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

from common.logger import get_logger
from common.mqtt.stress import list_clients

_logger = get_logger(__name__)


if __name__ == "__main__":
    result = list_clients(
        dashboard_host="http://192.168.75.132:18083",
        app_id="ee26b0dd4af7e749",
        app_secret="e2BZ3nGh9C9CkAWzO9C9AtSuJKNdrGQyn9BJ5p7YUURXr2nC",
    )
    _logger.info(result)
