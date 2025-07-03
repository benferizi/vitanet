import requests
import datetime

routes = {
    "VitalsSync": "http://localhost:5000/vitalsync",
    "StaffTime": "http://localhost:5000/stafftime",
    "Spark History": "http://localhost:5000/spark-history"
}

log_file = "route_status.log"
with open(log_file, "w") as log:
    log.write(f"🔎 Route Health Check — {datetime.datetime.now()}\n\n")
    for name, url in routes.items():
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                log.write(f"✅ {name} — {url} — Status {response.status_code}\n")
            else:
                log.write(f"⚠️ {name} — {url} — Unexpected Status: {response.status_code}\n")
        except Exception as e:
            log.write(f"❌ {name} — {url} — Error: {e}\n")

