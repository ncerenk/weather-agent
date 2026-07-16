import os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import tool

load_dotenv()


class WeatherInput(BaseModel):
    city: str = Field(
        description="Hava durumu sorgulanacak şehir adı. Örnek: Istanbul, Ankara, London."
    )


@tool("get_weather_info", args_schema=WeatherInput)
def get_weather_info(city: str) -> str:
    """Belirtilen şehir için OpenWeather API kullanarak güncel hava durumu bilgisini getirir."""

    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return "OPENWEATHER_API_KEY bulunamadı. .env dosyasını kontrol et."

    # 1. Şehir adından koordinat alma
    geo_resp = requests.get(
        "https://api.openweathermap.org/geo/1.0/direct",
        params={
            "q": city,
            "limit": 1,
            "appid": api_key,
        },
        timeout=10,
    )

    geo_data = geo_resp.json()

    if not geo_data:
        return f"{city} için konum bulunamadı."

    location = geo_data[0]
    lat = location["lat"]
    lon = location["lon"]
    city_name = location.get("name", city)
    country = location.get("country", "")

    # 2. Koordinatla hava durumu alma
    weather_resp = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": "metric",
            "lang": "tr",
        },
        timeout=10,
    )

    weather_data = weather_resp.json()

    if weather_resp.status_code != 200:
        return f"{city_name} için hava durumu alınamadı: {weather_data.get('message', '')}"

    temp = weather_data["main"]["temp"]
    feels_like = weather_data["main"]["feels_like"]
    humidity = weather_data["main"]["humidity"]
    wind_speed = weather_data["wind"]["speed"]
    description = weather_data["weather"][0]["description"]

    return (
        f"{city_name}, {country}\n"
        f"Hava: {description}\n"
        f"Sıcaklık: {temp}°C\n"
        f"Hissedilen: {feels_like}°C\n"
        f"Nem: %{humidity}\n"
        f"Rüzgar: {wind_speed} m/s"
    )