"""阿里云 OSS 多分片上传封装。"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import oss2
from tqdm import tqdm

from ..logger import get_logger

_logger = get_logger(__name__)


class OSSClient:
    def __init__(
        self,
        access_key_id: str,
        access_key_secret: str,
        endpoint: str,
        bucket_name: str,
    ) -> None:
        self.auth = oss2.Auth(access_key_id, access_key_secret)
        self.bucket = oss2.Bucket(self.auth, endpoint, bucket_name)

    def multipart_upload(
        self,
        local_file: str,
        object_name: str,
        *,
        part_size: int = 10 * 1024 * 1024,
        progress: bool = True,
    ) -> str:
        """分片上传本地文件；返回 object_name。"""
        total_size = os.path.getsize(local_file)
        upload_id: str = self.bucket.init_multipart_upload(object_name).upload_id
        parts = []

        bar: Optional[tqdm] = tqdm(total=total_size, unit="B", unit_scale=True, desc="上传进度") if progress else None
        try:
            with Path(local_file).open("rb") as f:
                part_number = 1
                offset = 0
                while offset < total_size:
                    num_to_read = min(part_size, total_size - offset)
                    f.seek(offset)
                    data = f.read(num_to_read)
                    result = self.bucket.upload_part(object_name, upload_id, part_number, data)
                    parts.append(oss2.models.PartInfo(part_number, result.etag))
                    offset += num_to_read
                    part_number += 1
                    if bar is not None:
                        bar.update(num_to_read)
        finally:
            if bar is not None:
                bar.close()

        self.bucket.complete_multipart_upload(object_name, upload_id, parts)
        _logger.info("OSS 上传完成: %s -> %s", local_file, object_name)
        return object_name
