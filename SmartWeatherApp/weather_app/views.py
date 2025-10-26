import datetime
import requests
from django.shortcuts import render
from collections import defaultdict

def index(request):
    API_KEY = open("api_key", "r").read().strip()
    current_weather_url = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}"
    forecast_url = "http://api.openweathermap.org/data/2.5/forecast?q={}&appid={}"

    weather_data1 = None
    daily_forecasts1 = None
    error_message = None

    if request.method == "POST":
        city1 = request.POST.get('city1')

        try:
            weather_data1, daily_forecasts1 = fetch_weather_and_forecast(city1, API_KEY, current_weather_url, forecast_url)
        except Exception as e:
            print("Error:", e)
            error_message = str(e)

    context = {
        "weather_data1": weather_data1,
        "daily_forecasts1": daily_forecasts1,
        "error_message": error_message,
    }
    return render(request, "weather_app/index.html", context)


def fetch_weather_and_forecast(city, api_key, current_weather_url, forecast_url):
    # --- Current weather ---
    response = requests.get(current_weather_url.format(city, api_key)).json()
    if 'main' not in response or 'weather' not in response:
        raise ValueError("City not found or invalid API key.")

    weather_data = {
        "city": response['name'],
        "temperature": round(response['main']['temp'] - 273.15, 2),
        "description": response['weather'][0]['description'],
        "icon": response['weather'][0]['icon']
    }

    # --- 5-day / 3-hour forecast ---
    forecast_response = requests.get(forecast_url.format(city, api_key)).json()
    if 'list' not in forecast_response:
        raise ValueError("Forecast data unavailable for this plan.")

    grouped = defaultdict(list)
    for entry in forecast_response['list']:
        date = datetime.datetime.fromtimestamp(entry['dt']).date()
        grouped[date].append(entry)

    daily_forecasts = []
    for day, entries in list(grouped.items())[:5]:  # limit to 5 days
        temps = [e['main']['temp'] for e in entries]
        descriptions = [e['weather'][0]['description'] for e in entries]
        icons = [e['weather'][0]['icon'] for e in entries]

        daily_forecasts.append({
            "day": day.strftime("%A"),
            "min_temp": round(min(temps) - 273.15, 1),
            "max_temp": round(max(temps) - 273.15, 1),
            "description": max(set(descriptions), key=descriptions.count).title(),
            "icon": icons[len(icons)//2]  # middle icon of the day
        })

    return weather_data, daily_forecasts
