"""DeepSeek chat 接口 demo（原 `deepseek.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

from openai import OpenAI

from common.logger import get_logger

_logger = get_logger(__name__)


DEEPSEEK_API_KEY = "sk-b382446f26bc4147b2641373ed70b31d"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/"


def chat(system_prompt: str, user_prompt: str, *, model: str = "deepseek-chat") -> str:
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return completion.choices[0].message.content or ""


if __name__ == "__main__":
    answer = chat("你是一位 情感大师", "如何追一个妹子")
    _logger.info("回答：%s", answer)
