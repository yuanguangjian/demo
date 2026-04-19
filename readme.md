# demo

按业务域分层整理的脚本集合。

## 目录结构

```
demo/
├── common/              # 公共基础库（不含业务语义）
│   ├── config.py        # env.json / 环境变量统一读取
│   ├── logger.py        # 日志（替代 print）
│   ├── http_client.py   # requests.Session + 超时 + 401 自动重登
│   ├── signing/         # 业务签名：ECC (x-ugreen-*) / HMAC (x-ca-*) / MD5 (WMS) / ES256 JWT
│   ├── crypto/          # AES (CBC/GCM) / ECC (密钥 + ECDSA + ECDH + HKDF)
│   ├── db/              # MySQL / Redis / Kafka / Elasticsearch / OSS 客户端
│   ├── mqtt/            # MQTT 压测（gmqtt / paho 两 backend）
│   └── utils/           # 本地 JSON 存取等零散工具
├── ugreen_iot/          # 绿联 IoT 业务 SDK
│   ├── device_gateway.py
│   ├── metadata_gateway.py
│   ├── factory.py
│   ├── consumer.py
│   ├── rtcx.py          # 合并 ipc_rtcx + ipc_rtcx_forceUnbind
│   ├── nacos.py
│   ├── wms_sn.py
│   ├── product.py
│   ├── user_auth.py
│   ├── app/             # bind / share / contact / event_record / ota
│   └── demo/            # 联调脚本（保留各自 __main__）
├── apple_iap/           # Apple IAP：token / verify / storekit / connect_api
├── markets/             # 小米 / vivo / OPPO / 华为 评论抓取 + Excel 导出
├── infra_tests/         # WebSocket / MQTT / Kafka / ES / HTTP 压测与 demo
├── integrations/        # DeepSeek / SMTP / OSS 示例
├── scripts/             # 一次性运维 / 调试脚本
└── legacy/              # 优化前的老目录/顶层脚本归档（只供查证历史，别 import）
```

## 环境准备

```powershell
pip install -r requirements.txt
```

## 运行脚本

两种方式均可：

```powershell
# 1) 作为模块运行
python -m ugreen_iot.demo.ipc_app_client

# 2) 直接运行文件
python ugreen_iot/demo/ipc_app_client.py
```

所有脚本顶部都 `import _bootstrap`，会自动把 `demo/` 加到 `sys.path`。

## 环境配置

在 `demo/` 下放 `env.json`、`mysql.json`、`account.json`、`sn.json`、`key.json` 等
本地配置文件（已有历史格式）。也可读取进程环境变量（见 `common/config.py`）。

## 迁移自旧结构

- `utils/` → 拆到 `common/` 与 `ugreen_iot/`
- `ipc项目/` → 拆到 `ugreen_iot/demo/`，重复文件删除
- `apple/` + `pay.py` → 合并到 `apple_iap/`
- `data/` + `绿联APP评论.py` + `修复数据.py` → 合并到 `markets/`
- `kafka/` → `common/db/kafka.py` + `infra_tests/kafka_demo.py`

## TODO：待迁出源码的敏感信息（暂原样保留）

以下值目前仍硬编码在代码内，后续请迁到 `.env` 或密钥管理系统：

- RDS / Redis 账号密码（`common/db/mysql.py`、`common/db/redis_client.py`）
- OSS AK / SK（`common/db/oss.py`）
- SMTP 授权码（`integrations/email_smtp.py`）
- DeepSeek API Key（`integrations/deepseek.py`）
- Apple `.p8` / `key_id` / `issuer_id`（`apple_iap/token.py`）
- RTCX `app_key` / `app_secret`（`common/signing/hmac_rtcx.py`）
- 各 Bearer JWT / `privateKey` / `clientSecret`（脚本 `__main__` 内）
- 应用商店 Cookie（`markets/*.py`）
