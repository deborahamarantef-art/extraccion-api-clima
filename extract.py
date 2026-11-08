# Pre-entrega: extraccion de datos de una API
# Uso la API de Open-Meteo para traer el clima diario de Montevideo

import os
import requests
import pandas as pd
from dotenv import load_dotenv

# cargo las variables del archivo .env
load_dotenv()

url = os.getenv("API_URL", "https://archive-api.open-meteo.com/v1/archive")
latitud = os.getenv("LATITUD", "-34.9033")
longitud = os.getenv("LONGITUD", "-56.1882")
fecha_inicio = os.getenv("FECHA_INICIO", "2026-10-01")
fecha_fin = os.getenv("FECHA_FIN", "2026-10-31")

parametros = {
    "latitude": latitud,
    "longitude": longitud,
    "start_date": fecha_inicio,
    "end_date": fecha_fin,
    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
    "timezone": "America/Montevideo",
}

print("Consultando la API...")

try:
    respuesta = requests.get(url, params=parametros, timeout=10)
except requests.exceptions.RequestException as e:
    print("No se pudo conectar con la API:", e)
    exit()

if respuesta.status_code != 200:
    print("Error en la peticion. Codigo:", respuesta.status_code)
    exit()

datos = respuesta.json()

# me quedo solo con la parte "daily", el resto (coordenadas, unidades, etc) no lo necesito
df = pd.DataFrame(datos["daily"])

# renombro las columnas
df = df.rename(columns={
    "time": "fecha",
    "temperature_2m_max": "temp_max",
    "temperature_2m_min": "temp_min",
    "precipitation_sum": "lluvia_mm",
    "wind_speed_10m_max": "viento_max",
})

df["temp_media"] = (df["temp_max"] + df["temp_min"]) / 2

print(df.head())

# guardo los datos
df.to_csv("data/data_extracted.csv", index=False)
df.to_json("data/data_extracted.json", orient="records", indent=2)

print("Datos guardados en la carpeta data")
