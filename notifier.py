import os
import requests

_TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
_TIMEOUT = 8


def _esc(text: str) -> str:
    """Escape <, >, & for Telegram HTML mode."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def send_alert(
    ticker: str,
    classification: str,
    headline: str,
    timestamp: str,
    url: str,
) -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

    if not token or not chat_id:
        print("  [ERROR] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")
        return False

    ts_display = timestamp[:16].replace("T", " ") if timestamp else "—"

    text = (
        f"🔔 <b>[{_esc(ticker)}]</b> {_esc(classification)} Alert\n"
        f"📋 {_esc(classification)}\n"
        f"📰 {_esc(headline)}\n"
        f"🕒 {_esc(ts_display)}\n"
        f"🔗 <a href=\"{url}\">View Filing</a>"
    )

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }

    api_url = _TELEGRAM_API.format(token=token)

    for attempt in range(2):
        try:
            resp = requests.post(api_url, json=payload, timeout=_TIMEOUT)
            resp.raise_for_status()
            return True
        except requests.exceptions.Timeout:
            if attempt == 0:
                continue
            print(f"  [ERROR] Telegram timed out after 2 attempts for {ticker}")
        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Telegram dispatch failed for {ticker}: {e}")
            break

    return False
