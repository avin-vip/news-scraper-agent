import re

# Classification → trigger terms (Thai + English).
# Substring search, so "งบการเงิน" catches "งบการเงินรวม", "งบการเงินเฉพาะ", etc.
_KEYWORD_MAP = {
    "Financial Statement": [
        # Thai — F45 headline variants
        "แจ้งผลการดำเนินงาน",        # most common F45 prefix
        "ชี้แจงผลการดำเนินงาน",      # explanation of operating results
        "สรุปผลการดำเนินงาน",        # summary of operating results
        "ผลการดำเนินงาน",            # operating results (broad)
        "งบการเงิน",                  # financial statements
        # English
        "financial statement",
        "financial result",           # substring also catches "financial results"
        "f45",
        "operating result",
    ],
    "MD&A": [
        # Thai
        "คำอธิบายและวิเคราะห์ของฝ่ายจัดการ",
        "คำอธิบายและวิเคราะห์",       # shortened form sometimes used
        # English
        "md&a",
        "management discussion",
        "management's discussion",
    ],
    "Annual Report": [
        # Thai
        "รายงานประจำปี",
        "56-1",
        # English
        "annual report",
        "one report",
    ],
}

_SET_NEWS_BASE = "https://www.set.or.th/th/market/news-and-alert/news/"


def watchlist_match(symbol: str, watchlist: list) -> bool:
    return symbol.upper() in [s.upper() for s in watchlist]


def keyword_match(headline: str) -> str | None:
    """Returns classification label if headline matches any keyword, else None."""
    text = headline.lower()
    for classification, terms in _KEYWORD_MAP.items():
        for term in terms:
            if re.search(re.escape(term.lower()), text):
                return classification
    return None


def build_url(news_id: str) -> str:
    return f"{_SET_NEWS_BASE}{news_id}"
