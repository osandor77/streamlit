import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- Konfiguráció ---
st.set_page_config(page_title="Robot Dreams Weather App", layout="centered")

# --- API Kulcs Betöltése ---
API_KEY = st.secrets["openweathermap"]["api_key"]

#---Base URL ---
base_url = "https://api.openweathermap.org/data/2.5/"

# --- Függvények ---
def get_current_weather(city,api_key):
    """
    Lekéri a jelenlegi időjárási adatokat a megadott városhoz.
    """
    url = f"{base_url}weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        # HTTP státusz ellenőrzése
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

def get_forecast_data(city, api_key):
    """
    Lekéri az 5 napos előrejelzést a grafikonhoz.
    """
    url = f"{base_url}forecast?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

# --- UI Felépítése ---
st.title("Robot Dreams Python - Weather Map & Data Visualization App")
st.write("Enter city name")
city_input = st.text_input("", placeholder="London")

if city_input:
    if API_KEY:
        # Adatok lekérése a TOML-ból
        current_weather = get_current_weather(city_input, API_KEY)

        if current_weather:
            # --- 1. Szekció: Jelenlegi időjárás (KPI-ok) ---
            st.header(f"Current Weather in {city_input}")
            
            col1, col2, col3 = st.columns(3)
            
            temp = current_weather['main']['temp']
            humidity = current_weather['main']['humidity']
            wind_speed = current_weather['wind']['speed']
            
            col1.metric("Temperature (°C)", f"{temp}°C")
            col2.metric("Humidity (%)", f"{humidity}%")
            col3.metric("Wind Speed (m/s)", f"{wind_speed} m/s")

            # --- 2. Szekció: Térkép ---
            st.subheader("Weather Map")
            # Koordináták kinyerése
            lat = current_weather['coord']['lat']
            lon = current_weather['coord']['lon']
            
            # DataFrame készítése a térképhez
            map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
            
            # Térkép megjelenítése
            st.map(map_data, zoom=10)
            
            # --- 3. Szekció: Grafikon ---
            forecast_data = get_forecast_data(city_input, API_KEY)
            
            if forecast_data:
                st.subheader("Temperature Trends (Next 5 Days)")
                
                # Adatfeldolgozás a grafikonhoz
                temps = []
                dates = []
                
                for item in forecast_data['list']:
                    temps.append(item['main']['temp'])
        
                    # Dátum/idő formázása
                    dt_object = datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
                    formatted_date = dt_object.strftime('%m.%d %H:%M')
                    dates.append(formatted_date) # A formázott dátum hozzáadása
                            
                chart_data = pd.DataFrame({
                    'Temperature': temps,
                    'Date': dates
                })
                
                # Index beállítása a dátumra
                chart_data = chart_data.set_index('Date')
                
                # Vonaldiagram kirajzolása
                st.line_chart(chart_data)
                
        else:
            st.warning(f"Could not retrieve data for city: {city_input}. Please check the name or the configured API key!")