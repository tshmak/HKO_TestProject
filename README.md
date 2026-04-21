# HKO Weather Forecast

Fetches and stores 9-day weather forecasts from the Hong Kong Observatory API, with a Streamlit UI for interactive visualization.

This app is available on <https://hkopast.streamlit.app/> via [Streamlit community cloud](https://streamlit.io/cloud). The data should update automatically via Github Actions (see [.github/workflows/scheduler.yml](.github/workflows/scheduler.yml)).

## Installation

```bash
uv sync
```

## Fetching Data

```bash
python scripts/fetch_forecast.py
```

Or install the command-line entry point after `uv sync`:

```bash
fetch-forecast
```

Each run appends one row per forecast day, keyed on both `fetch_date` (when the data was retrieved) and `forecast_date` (the target day). Running it multiple times on the same day overwrites the same `fetch_date` rows; running on different days creates distinct `fetch_date` entries. This allows comparing how forecasts change over time for the same target dates.

## Querying Data

```bash
# List latest forecasts
python scripts/query_forecast.py

# List specific number of rows
python scripts/query_forecast.py -l 20

# Query all forecasts for a specific target date
python scripts/query_forecast.py -d 20260420
```

Output is JSON.

## Streamlit App

```bash
streamlit run scripts/streamlit_app.py
```

The app lets you:
- Toggle Max/Min temperature display (or both together)
- Select a forecast date range
- Show all fetch dates or pick a specific one
- Each `fetch_date` series is rendered in a different color

To run in Docker: 
```
docker build -t hko-forecast . && docker run --env-file .env -p 8501:8501 hko-forecast
```

## FastAPI Server

```bash
uvicorn scripts.api:app --host 127.0.0.1 --port 8000 --reload
```

Common options:
- `--host` - bind address (default: 127.0.0.1)
- `--port` - port number (default: 8000)
- `--reload` - enable auto-reload on code changes
- `--workers N` - number of worker processes

To run in the background: append `&` or use `--background` (uvicorn >= 0.30).

API endpoints:
- `GET /health` - health check
- `GET /forecasts?date=YYYYMMDD` - query by forecast date
- `GET /forecasts?fetch_date=YYYYMMDD` - query by fetch date
- `GET /forecasts/latest` - latest fetch
- `GET /forecasts/today` - today's forecast
