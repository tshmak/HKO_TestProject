from sqlalchemy import text
from app.db import get_db

def store_all(raw_data: dict, fetch_date: str, fetch_time: str):
    with get_db() as conn:
        for day in raw_data.get("weatherForecast", []):
            conn.execute(
                text("""
                    INSERT INTO forecasts (
                        fetch_date, fetch_time, forecast_date, week,
                        maxtemp_value, maxtemp_unit, mintemp_value, mintemp_unit,
                        weather, wind, maxrh_value, minrh_value, icon, psr
                    ) VALUES (:fd, :ft, :forecastDate, :week,
                        :maxtemp_value, 'C', :mintemp_value, 'C',
                        :weather, :wind, :maxrh, :minrh, :icon, :psr
                    ) ON CONFLICT (forecast_date, fetch_date) DO NOTHING
                """),
                {
                    "fd": fetch_date,
                    "ft": fetch_time,
                    "forecastDate": day.get("forecastDate"),
                    "week": day.get("week"),
                    "maxtemp_value": day.get("forecastMaxtemp", {}).get("value"),
                    "mintemp_value": day.get("forecastMintemp", {}).get("value"),
                    "weather": day.get("forecastWeather"),
                    "wind": day.get("forecastWind"),
                    "maxrh": day.get("forecastMaxrh", {}).get("value"),
                    "minrh": day.get("forecastMinrh", {}).get("value"),
                    "icon": day.get("ForecastIcon"),
                    "psr": day.get("PSR"),
                },
            )
        conn.commit()
