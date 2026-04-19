# legacy/

本目录是优化前的老代码归档，仅用于**查证历史逻辑**，不再维护、不建议从新代码里 import。

## 里面有什么

| 路径 | 原位置 | 对应的新实现 |
|---|---|---|
| `utils/` | `demo/utils/` | `common/` + `ugreen_iot/` |
| `ipc项目/` | `demo/ipc项目/` | `ugreen_iot/demo/` + `common/mqtt/stress.py` + `common/db/*` |
| `apple/` | `demo/apple/` | `apple_iap/` |
| `data/` | `demo/data/` | `markets/` |
| `kafka/` | `demo/kafka/` | `common/db/kafka.py` + `infra_tests/kafka_demo.py` |
| `websocket.py` / `websocket_demo1.py` | 顶层 | `infra_tests/websocket_stress.py` / `websocket_simple.py` |
| `pay.py` | 顶层 | `apple_iap/token.py` |
| `my_email.py` | 顶层 | `integrations/email_smtp.py` |
| `ossUtils.py` | 顶层 | `integrations/oss_upload.py`（逻辑在 `common/db/oss.py`） |
| `deepseek.py` | 顶层 | `integrations/deepseek.py` |
| `main.py` | 顶层 | 一次性测试脚本，未迁移 |
| `修复数据.py` | 顶层 | 已合进 `markets/xiaomi.py` |
| `用户登录注册相关接口.py` | 顶层 | `ugreen_iot/user_auth.py` |
| `绿联APP评论.py` | 顶层 | `markets/export_excel.py` |

## 注意事项

- 归档后的 `import` 多半是相对老结构写的（如 `import EccUtil`），**直接跑会 ImportError**，只做参考。
- 如果将来确认新实现能完全覆盖，可以整个 `legacy/` 目录一并删除。
