from pydantic import BaseModel

class Temp(BaseModel):
    value: int
    unit: str

class ForecastRow(BaseModel):
    fetch_date: str
    fetch_time: str
    forecast_date: str
    week: str
    maxtemp: Temp
    mintemp: Temp
    weather: str | None
    wind: str | None
    maxrh: Temp | None
    minrh: Temp | None
    icon: int | None
    psr: str | None

class ForecastListResponse(BaseModel):
    count: int
    forecasts: list[ForecastRow]