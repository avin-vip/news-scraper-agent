import json
import os
import sys
import time
from datetime import datetime, timezone

import schedule
from dotenv import load_dotenv

import filter as f
import notifier
import poller
import state

load_dotenv()

_CONFIG_FILE = "config.json"


def _load_config() -> dict:
    with open(_CONFIG_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _log(level: str, msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {level:<5} {msg}")


def run_cycle(config: dict) -> None:
    watchlist = config["watchlist"]

    items = poller.fetch_news()
    _log("POLL", f"fetched {len(items)} items")

    for item in items:
        news_id = item["newsId"]
        symbol = item["symbol"]
        headline = item["headline"]
        timestamp = item["datetime"]

        if state.is_seen(news_id):
            _log("SKIP", f"{symbol} — already seen (id: {news_id})")
            continue

        if not f.watchlist_match(symbol, watchlist):
            continue

        classification = f.keyword_match(headline)
        if not classification:
            _log("DROP", f"{symbol} — headline did not match keywords")
            state.mark_seen(news_id)
            continue

        url = f.build_url(news_id)
        ok = notifier.send_alert(symbol, classification, headline, timestamp, url)

        if ok:
            _log("MATCH", f"{symbol} — {classification} → alert sent")
        else:
            _log("FAIL", f"{symbol} — {classification} → alert failed, will retry next cycle")

        state.mark_seen(news_id)


def main() -> None:
    print("=" * 60)
    print("  SET Corporate Disclosure Router  |  starting up")
    print("=" * 60)

    if not os.path.exists(_CONFIG_FILE):
        print(f"[ERROR] {_CONFIG_FILE} not found. Exiting.")
        raise SystemExit(1)

    config = _load_config()
    print(f"  Watchlist : {config['watchlist']}")
    print(f"  Poll interval : 60 seconds")
    print("=" * 60)

    # Run immediately on startup, then every 60 seconds
    run_cycle(config)
    schedule.every(60).seconds.do(run_cycle, config=config)

    while True:
        schedule.run_pending()
        time.sleep(1)


def run_test() -> None:
    print("=" * 60)
    print("  SET Corporate Disclosure Router  |  TEST MODE")
    print("=" * 60)

    config = _load_config()
    ticker = config["watchlist"][0] if config["watchlist"] else "PTT"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"  Sending mock alert for: {ticker}")
    print(f"  Check your Telegram for the message.")
    print("=" * 60)

    ok = notifier.send_alert(
        ticker=ticker,
        classification="Financial Statement",
        headline=f"[TEST] สรุปผลการดำเนินงานของบริษัทจดทะเบียน ไตรมาสที่ 1 ปี 2568 (F45-1)",
        timestamp=ts,
        url="https://www.set.or.th/th/market/news-and-alert/news/00000000",
    )

    if ok:
        print("  [OK]  Telegram alert delivered successfully.")
        print("        Your credentials are working. Run without --test to start live monitoring.")
    else:
        print("  [FAIL] Alert was not delivered.")
        print("         Check TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in your .env file.")
    print("=" * 60)


if __name__ == "__main__":
    if "--test" in sys.argv:
        run_test()
    else:
        main()
