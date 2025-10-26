import datetime

import requests
from django.shortcuts import render

# Create your views here.
def indes(request):
    API_KEY = open("api_key","r").read()
    current_weather_url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}"
    forecast_url = "https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=current,minutely,hourly,alerts&appid={}"

    if request.method == "POSTS":
        city1 = request.POST['City1']
        weather_data1, daily_forecasts1 = fetch_weather_and_forecasts(city1, API_KEY, current_weather_url, forecasts_url)
        

        context ={
            "weather_data1": weather_data1,
            "daily_forecasts1": daily_forecasts1,
            
        }

        return render(request, "weather_app/index.html", context)
    else:
        return render(request, "weather_app/index.html")
    
def fetch_weather_and_forcast(city, api_key, current_weather_url, forecast_url):
    response = requests.get(current_weather_url.format(city,api_key)).json()
    lat, lon = response['coord']['lat'], response['coord']['lon']
    forecast_response = requests.get(forecast_url.format(lat, lon, api_key)).json()

    weather_data ={
        "city": city,
        "temperature": round(response['main']['temp'] - 273.15,2),
        "description": response['weaher'][0]['description'],
        "icon": response['weather'][0]['icon']
    }

    daily_forecasts = []
    for daily_data in forecast_reponse['daiy'][:5]:
        daily_forecasts.append({
            "day": datetime.datetime.fromtimestamp(daily_date['dt']).strftime("%A"),
            "min_temp": round(daily_data['temp']['min'] - 273.15,2),
            "max_temp": round(daily_data['temp']['max'] - 273.15,2),
            "description": daily_data['weather'][0]['description'],
            "icon": daily_date['weather'][0]['icoon']
        })

        return weather_data, daily_forecasts