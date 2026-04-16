import os
import ssl
import urllib.request
import json
import certifi

HKO_API_URL = os.getenv("HKO_API_URL", "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang=en")

def fetch() -> dict:
    ctx = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(HKO_API_URL, context=ctx) as resp:
        return json.loads(resp.read().decode())