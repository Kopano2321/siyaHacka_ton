import datetime
import requests
from django.shortcuts import render

def index(request):
    API_KEY = open("api_key", "r").read().strip()

    current_weather_url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}"
    forecast_url = "https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=current,minutely,hourly,alerts&appid={}"

    if request.method == "POST":
        city1 = request.POST['city1']
        weather_data1, daily_forecasts1 = fetch_weather_and_forecast(city1, API_KEY, current_weather_url, forecast_url)

        context = {
            "weather_data1": weather_data1,
            "daily_forecasts1": daily_forecasts1,
        }
        return render(request, "weather_app/index.html", context)
    else:
        return render(request, "weather_app/index.html")


def fetch_weather_and_forecast(city, api_key, current_weather_url, forecast_url):
    # Get current weather data
    response = requests.get(current_weather_url.format(city, api_key)).json()

    lat, lon = response['coord']['lat'], response['coord']['lon']

    # Use the 5-day / 3-hour forecast endpoint instead
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}"
    forecast_response = requests.get(forecast_url).json()

    weather_data = {
        "city": city,
        "temperature": round(response['main']['temp'] - 273.15, 2),
        "description": response['weather'][0]['description'],
        "icon": response['weather'][0]['icon']
    }

    # Group forecasts by date
    daily_data = {}
    for item in forecast_response['list']:
        date = datetime.datetime.fromtimestamp(item['dt']).strftime("%A")
        temp = item['main']['temp'] - 273.15
        desc = item['weather'][0]['description']
        icon = item['weather'][0]['icon']

        if date not in daily_data:
            daily_data[date] = {
                "temps": [temp],
                "descriptions": [desc],
                "icons": [icon]
            }
        else:
            daily_data[date]["temps"].append(temp)
            daily_data[date]["descriptions"].append(desc)
            daily_data[date]["icons"].append(icon)

    # Simplify to one summary per day
    daily_forecasts = []
    for day, data in list(daily_data.items())[:7]:
        daily_forecasts.append({
            "day": day,
            "min_temp": round(min(data["temps"]), 2),
            "max_temp": round(max(data["temps"]), 2),
            "description": data["descriptions"][0],
            "icon": data["icons"][0]
        })

    return weather_data, daily_forecasts