import requests

_SET_API_URL = (
    "https://www.set.or.th/api/set/news/search"
    "?lang=th&newsType=company&page=1&limit=50"
)

_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "th-TH,th;q=0.9,en-US;q=0.8",
    "Referer": "https://www.set.or.th/th/market/news-and-alert/news",
    "User-Agent": (
        "Mozilla/5.0 (compatible; SET-Router/1.0)"
    ),
}

_TIMEOUT = 10


def fetch_news() -> list[dict]:
    """
    Fetches the latest SET company news items.
    Returns a list of dicts with keys: newsId, symbol, headline, datetime.
    Returns empty list on any error so the caller never crashes.
    """
    try:
        resp = requests.get(_SET_API_URL, headers=_HEADERS, timeout=_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.Timeout:
        print("  [WARN] SET API request timed out")
        return []
    except requests.exceptions.ConnectionError as e:
        print(f"  [WARN] SET API connection error: {e}")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"  [WARN] SET API HTTP error: {e}")
        return []
    except ValueError:
        print("  [WARN] SET API returned non-JSON response")
        return []

    return _normalize(data)


def _normalize(data) -> list[dict]:
    """
    Handles multiple possible response shapes from the SET API.
    Tries common envelope keys; falls back to raw list.
    """
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        for key in ("newsItems", "data", "items", "news", "results"):
            if key in data and isinstance(data[key], list):
                items = data[key]
                break
        else:
            print(f"  [WARN] Unexpected SET API shape — top-level keys: {list(data.keys())}")
            return []
    else:
        return []

    normalized = []
    for item in items:
        if not isinstance(item, dict):
            continue
        news_id = (
            item.get("newsId")
            or item.get("id")
            or item.get("news_id")
        )
        symbol = (
            item.get("symbol")
            or item.get("securitySymbol")
            or item.get("ticker")
            or ""
        )
        headline = (
            item.get("headline")
            or item.get("subject")
            or item.get("title")
            or ""
        )
        timestamp = (
            item.get("datetime")
            or item.get("publishedDate")
            or item.get("date")
            or ""
        )

        if not news_id or not symbol or not headline:
            continue

        normalized.append({
            "newsId": str(news_id),
            "symbol": str(symbol).upper().strip(),
            "headline": str(headline).strip(),
            "datetime": str(timestamp),
        })

    return normalized
