from flask import Flask, request, jsonify
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

try:
    from dotenv import load_dotenv
    load_dotenv()  # Loads from .env file into os.environ
except ImportError:
    print("dotenv not found, usig environment variables directly.")

# Load environment variables
MATTERMOST_WEBHOOK = os.getenv("MATTERMOST_WEBHOOK")
CATEGORY_ID = os.getenv("INDICO_CATEGORY_ID")
KEYWORDS = os.getenv("KEYWORDS", "").split(",")
TIME_BEFORE_MINUTES = int(os.getenv("TIME_BEFORE_MINUTES", "15"))
MATTERMOST_CHANNEL = os.getenv("MATTERMOST_CHANNEL", "bot-testing-environment")
DEBUG = os.getenv("DEBUG", False)

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

    try:
        start_date = event['startDate']['date']
        start_time = event['startDate']['time']
        tz_name = event['startDate'].get('tz', 'UTC')

        # Combine date and time, assign the correct timezone
        start_dt_local = datetime.strptime(f"{start_date}T{start_time}", "%Y-%m-%dT%H:%M:%S")
        start_dt = start_dt_local.replace(tzinfo=ZoneInfo(tz_name))

        # Convert to UTC for comparison
        start_utc = start_dt.astimezone(ZoneInfo("UTC"))

        # Store the formatted version back (optional)
        event["startDate"]["date"] = start_dt.strftime("%d-%m-%Y")
        event["startDate"]["time"] = start_dt.strftime("%H:%M:%S")
    except KeyError as e:
        print(f"Missing key in event data: {e}")
        return False

    if eid in seen_events:
        return False

    now = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
    time_until_start = start_utc - now
    notify_threshold = timedelta(minutes=TIME_BEFORE_MINUTES)

    # Uncomment for debugging
    # print("Current time (UTC):", now)
    # print("Event start time (UTC):", start_utc)
    # print("Time until start:", time_until_start)
    # print("--------------------------------------")

    if notify_threshold - timedelta(minutes=1) <= time_until_start <= notify_threshold:
        print("Event is within the notification window.")
        return True
    return False

def send_notification(event):
    eid = str(event["id"])
    title = event["title"]
    url = f"https://indico.cern.ch/event/{eid}/"
    start = str(event["startDate"]["date"]+", " + event["startDate"]["time"])

    message = f"##### 🔔 *Upcoming Event in {TIME_BEFORE_MINUTES} minutes @all!*\n ##### **{title}**\n :indico: **[Indico Agenda]({url})**"
    requests.post(MATTERMOST_WEBHOOK, json={"text": message, "channel": MATTERMOST_CHANNEL})
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
    app.run(debug=DEBUG, host="0.0.0.0", port=8080)
