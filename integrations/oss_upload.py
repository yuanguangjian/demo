"""阿里云 OSS 上传 demo（原 `ossUtils.py`）。

实际逻辑在 `common.db.oss.OSSClient`，这里只给一个开箱即用的脚本入口。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

from common.db.oss import OSSClient
from common.logger import get_logger

_logger = get_logger(__name__)


OSS_ACCESS_KEY_ID = ""
OSS_ACCESS_KEY_SECRET = ""
OSS_ENDPOINT = "https://oss-cn-shenzhen.aliyuncs.com"
OSS_BUCKET = "ugreen-dpt"


def main() -> None:
    client = OSSClient(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET, OSS_ENDPOINT, OSS_BUCKET)
    local_file = "D:\\Downloads\\CursorUserSetup-x64-1.6.27.exe"
    object_name = "ursorUserSetup.exe"
    client.multipart_upload(local_file, object_name, part_size=10 * 1024 * 1024)


if __name__ == "__main__":
    main()
