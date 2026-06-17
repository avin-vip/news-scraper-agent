# SET Corporate Disclosure Router

Polls the Stock Exchange of Thailand (SET) every 60 seconds for corporate filings. When a stock on your watchlist publishes a financial report, MD&A, or annual report — you get a Telegram alert with a direct link to the document. No AI, no summarization, no cost.

## How it works

1. Fetches the SET company news feed every 60 seconds
2. Drops anything not on your watchlist
3. Checks the headline for financial report keywords (Thai + English)
4. Sends a Telegram message with ticker, classification, and direct link

## Setup

**1. Clone and install**
```bash
pip install -r requirements.txt
```

**2. Create your `.env` file**
```bash
cp .env.example .env
```
Fill in your Telegram credentials:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```
> To get these: create a bot via [@BotFather](https://t.me/BotFather) on Telegram, then get your chat ID from [@userinfobot](https://t.me/userinfobot).

**3. Edit your watchlist**

Open `config.json` and update the `watchlist` array with the SET tickers you want to track:
```json
{
  "watchlist": ["PTT", "ADVANC", "CPALL", "SCC", "BDMS"],
  ...
}
```

**4. Run**
```bash
python main.py
```

## Docker

```bash
docker build -t set-router .
docker run --env-file .env -v $(pwd)/state.json:/app/state.json set-router
```

## What you'll see in the terminal

```
[2026-06-17 09:44:01] POLL  fetched 47 items
[2026-06-17 09:44:01] MATCH PTT — Financial Statement → alert sent
[2026-06-17 09:44:01] DROP  KBANK — headline did not match keywords
[2026-06-17 09:44:01] SKIP  CPALL — already seen (id: 12345678)
```

## Telegram alert format

```
🔔 [PTT] Financial Statement Alert
📋 Financial Statement
📰 สรุปผลการดำเนินงานของบริษัทจดทะเบียน ประจำปี 2568
🕒 2026-06-17 09:43
🔗 https://www.set.or.th/th/market/news-and-alert/news/12345678
```

## Files

| File | What it does |
|---|---|
| `config.json` | Edit your watchlist and keywords here |
| `state.json` | Auto-created — tracks seen news IDs to prevent duplicate alerts |
| `.env` | Your Telegram secrets (never commit this) |

## Keywords tracked

| Category | Examples |
|---|---|
| Financial Statement | งบการเงิน, สรุปผลการดำเนินงาน, F45 |
| MD&A | คำอธิบายและวิเคราะห์ของฝ่ายจัดการ, MD&A |
| Annual Report | รายงานประจำปี, 56-1 One Report |
