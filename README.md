# 📅 Indico Event Notifier Bot
[![Docker](https://github.com/Soap2G/mattermost-indico-announcer/actions/workflows/publish-docker.yml/badge.svg)](https://github.com/Soap2G/mattermost-indico-announcer/actions/workflows/publish-docker.yml)

This bot monitors upcoming Indico events in a specified category and sends notifications to a Mattermost channel shortly before they begin.

---

## 🔧 Features

* ✅ Polls CERN Indico for upcoming events in a category
* 🔔 Sends notifications to a configured Mattermost webhook if event keywords match
* ⏰ Triggers alerts a configurable number of minutes before event start
* 🐳 Containerized with Docker

### Work in progress
* 🩺 `/health` and `/config` endpoints for runtime diagnostics
* ☸️ Helm charts

---


## 🚀 Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/Soap2G/mattermost-indico-announcer.git
cd mattermost-indico-announcer
```

### 2. Create a `.env` file

```ini
# .env

MATTERMOST_WEBHOOK=https://your-mattermost-webhook-url
INDICO_CATEGORY_ID=XXXX
KEYWORDS=ml,ai,data
TIME_BEFORE_MINUTES=15
MATTERMOST_CHANNEL=your-channel-name
DEBUG=True
```

### 3. Install dependencies (for local development)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Run the bot locally

```bash
python bot.py
```

---

## 🐳 Docker

### Build and run the container

```bash
docker build -t indico-bot .
docker run --env-file .env -p 8080:8080 indico-bot
```


<!-- 
--- 
## ☸️ Deploying to Kubernetes (with Helm)

### 1. Package and install the chart

```bash
cd helm-charts
helm install indico-bot . --values values.yaml
```

> Make sure secrets like `MATTERMOST_WEBHOOK` are passed securely, e.g., via Kubernetes secrets or CI/CD tooling. 

---

## 🌐 API Endpoints

* `GET /health` – Check service status (`200 OK`)
* `GET /config` – Inspect current config (category, keywords, time threshold)
-->
---

## ⚙️ Configuration

| Variable              | Description                                        | Required | Default                     |
| --------------------- | -------------------------------------------------- | -------- | --------------------------- |
| `MATTERMOST_WEBHOOK`  | Incoming webhook URL for your Mattermost channel   | ✅        | —                           |
| `INDICO_CATEGORY_ID`  | CERN Indico category ID to monitor                 | ✅        | —                           |
| `KEYWORDS`            | Comma-separated keywords to filter event titles    | ❌        | `""` (match all events)     |
| `TIME_BEFORE_MINUTES` | Minutes before event start to send notification    | ❌        | `15`                        |
| `MATTERMOST_CHANNEL`  | Mattermost channel name to post notifications into | ❌        | `"bot-testing-environment"` |
| `DEBUG`               | Flask debug mode                                   | ❌        | `False`                     |

---

## 📌 Notes

* Events are considered only once using an in-memory cache (`seen_events`).
* Timezone-aware conversion ensures correct UTC handling from CERN Indico.
* Make sure your category contains events with structured `startDate`.

---

## 📄 License

MIT — feel free to use and adapt.
