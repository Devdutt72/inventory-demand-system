import streamlit as st
import requests

# 🔒 SECURE: Fetch from secrets
API_KEY = st.secrets["WEATHER_API_KEY"] 
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_live_weather(city):
    url = f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                "city": data['name'],
                "temperature": data['main']['temp'],
                "condition": data['weather'][0]['main'],
                "description": data['weather'][0]['description']
            }
        else:
            return {"error": "City not found."}
    except Exception as e:
        return {"error": str(e)}