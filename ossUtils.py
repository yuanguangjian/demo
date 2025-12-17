# -*- coding: utf-8 -*-
import os
import oss2
import time
from tqdm import tqdm

access_key_id = ''
access_key_secret = ''
endpoint = 'https://oss-cn-shenzhen.aliyuncs.com'
bucket_name = 'ugreen-dpt'
print(time.time())
auth = oss2.Auth(access_key_id, access_key_secret)
bucket = oss2.Bucket(auth, endpoint, bucket_name)

local_file = 'D:\\Downloads\\CursorUserSetup-x64-1.6.27.exe'
object_name = 'ursorUserSetup.exe'

part_size = 10 * 1024 * 1024

total_size = os.path.getsize(local_file)

upload_id = bucket.init_multipart_upload(object_name).upload_id

parts = []
with open(local_file, 'rb') as file:
    part_number = 1
    offset = 0
    with tqdm(total=total_size, unit='B', unit_scale=True, desc='上传进度') as pbar:
        while offset < total_size:
            num_to_read = min(part_size, total_size - offset)
            file.seek(offset)
            data = file.read(num_to_read)
            result = bucket.upload_part(object_name, upload_id, part_number, data)
            parts.append(oss2.models.PartInfo(part_number, result.etag))
            offset += num_to_read
            pbar.update(num_to_read)
            part_number += 1

bucket.complete_multipart_upload(object_name, upload_id, parts)
print("oss __  sucess")
