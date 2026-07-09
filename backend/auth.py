"""
Validates Telegram Mini App `initData` so the backend can trust who is
calling the API. Algorithm per Telegram docs:
https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""
import hashlib
import hmac
import json
import os
from urllib.parse import parse_qsl

BOT_TOKEN = os.getenv("BOT_TOKEN", "")


def validate_init_data(init_data: str, bot_token: str = None) -> dict | None:
    """Returns the parsed Telegram user dict if initData is valid, else None."""
    bot_token = bot_token or BOT_TOKEN
    if not init_data or not bot_token:
        return None

    try:
        pairs = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        return None

    received_hash = pairs.pop("hash", None)
    if not received_hash:
        return None

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return None

    user_json = pairs.get("user")
    if not user_json:
        return None
    return json.loads(user_json)


def dev_fallback_user(telegram_id: int = 111000111) -> dict:
    """Used only when running the Mini App outside Telegram (plain browser) for local dev."""
    return {"id": telegram_id, "username": "dev_user", "first_name": "Dev", "last_name": "User"}
