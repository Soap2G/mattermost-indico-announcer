from flask import Flask, request, jsonify
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import os

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

MATTERMOST_WEBHOOK = os.getenv("MATTERMOST_WEBHOOK")
CATEGORY_ID = os.getenv("INDICO_CATEGORY_ID")
KEYWORDS = os.getenv("KEYWORDS", "").split(",")
TIME_BEFORE_MINUTES = int(os.getenv("TIME_BEFORE_MINUTES", "15"))

seen_events = {}

def fetch_upcoming_events():
    now = datetime.utcnow().strftime("%Y-%m-%d")
    url = f"https://indico.cern.ch/export/categ/{CATEGORY_ID}.json?from={now}&detail=events"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()["results"]

def should_notify(event):
    title = event["title"].lower()
    description = event.get("description", "").lower()

    if KEYWORDS and not any(k.strip().lower() in title or k.strip().lower() in description for k in KEYWORDS):
        return False

    eid = str(event["id"])
    start_time = datetime.strptime(event["startDate"]["date"], "%Y-%m-%dT%H:%M:%S")

    if eid in seen_events:
        return False

    now = datetime.utcnow()
    if now + timedelta(minutes=TIME_BEFORE_MINUTES) >= start_time:
        return True
    return False

def send_notification(event):
    eid = str(event["id"])
    title = event["title"]
    url = f"https://indico.cern.ch/event/{eid}/"
    start = event["startDate"]["date"]

    message = f"🔔 *Upcoming Event in {TIME_BEFORE_MINUTES} minutes!*\n**{title}**\n🕒 {start} UTC\n🔗 [Event Link]({url})"
    requests.post(MATTERMOST_WEBHOOK, json={"text": message})
    seen_events[eid] = True

def poll():
    try:
        events = fetch_upcoming_events()
        for event in events:
            if should_notify(event):
                send_notification(event)
    except Exception as e:
        print("Error polling events:", e)

scheduler.add_job(poll, "interval", minutes=1)

@app.route("/health")
def health():
    return "OK", 200

@app.route("/config")
def config():
    return jsonify({
        "category_id": CATEGORY_ID,
        "keywords": KEYWORDS,
        "minutes_before": TIME_BEFORE_MINUTES,
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
