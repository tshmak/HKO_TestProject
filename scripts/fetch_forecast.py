from datetime import datetime
from app.fetcher import fetch
from app.store import store_all
from app.db import init_db

def main():
    init_db()
    data = fetch()
    fetch_time = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    fetch_date = datetime.now().strftime("%Y%m%d")
    store_all(data, fetch_date, fetch_time)
    print(f"[{fetch_time}] Stored {len(data['weatherForecast'])} forecast days")

if __name__ == "__main__":
    main()