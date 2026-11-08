"""Extracción de datos climáticos diarios desde la API de Open-Meteo.

Descarga el histórico diario de una ciudad para un rango de fechas,
lo limpia y lo guarda en data/data_extracted.csv y data/data_extracted.json.

Uso:
    python extract.py
"""
import json
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()  # carga las variables definidas en .env

BASE_URL = os.getenv("API_BASE_URL", "https://archive-api.open-meteo.com/v1/archive")
API_KEY = os.getenv("API_KEY")  # Open-Meteo no la exige; se deja preparada por si se cambia de API
CITY = os.getenv("CITY", "Montevideo")
LATITUDE = os.getenv("LATITUDE", "-34.9033")
LONGITUDE = os.getenv("LONGITUDE", "-56.1882")
START_DATE = os.getenv("START_DATE", "2026-10-01")
END_DATE = os.getenv("END_DATE", "2026-10-31")
TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

VARIABLES = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max"]
OUTPUT_DIR = Path(__file__).resolve().parent / "data"


def get_data() -> dict:
    """Hace la petición GET con reintentos y devuelve el JSON de la respuesta."""
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": ",".join(VARIABLES),
        "timezone": "America/Montevideo",
    }
    headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}

    for intento in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(BASE_URL, params=params, headers=headers, timeout=TIMEOUT)

            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 400:
                # Parámetros inválidos (por ejemplo, fechas mal escritas): no tiene sentido reintentar
                motivo = resp.json().get("reason", resp.text)
                raise SystemExit(f"Error 400 - parámetros inválidos: {motivo}")
            if resp.status_code == 404:
                raise SystemExit(f"Error 404 - no se encontró el recurso: {resp.url}")
            if resp.status_code >= 500:
                print(f"Intento {intento}: el servidor respondió {resp.status_code}. Reintentando...")
            else:
                raise SystemExit(f"Error {resp.status_code}: {resp.text[:200]}")

        except requests.exceptions.Timeout:
            print(f"Intento {intento}: la API no respondió en {TIMEOUT} segundos.")
        except requests.exceptions.ConnectionError:
            print(f"Intento {intento}: no se pudo conectar con la API (¿hay conexión a internet?).")
        except ValueError:
            raise SystemExit("La respuesta de la API no es un JSON válido.")

        time.sleep(2 * intento)  # espera creciente entre intentos

    raise SystemExit(f"No se pudieron obtener los datos después de {MAX_RETRIES} intentos.")


def transform(raw: dict) -> pd.DataFrame:
    """Se queda solo con los datos diarios y les pone nombres claros."""
    if "daily" not in raw:
        raise SystemExit("La respuesta no tiene el bloque 'daily' esperado.")

    df = pd.DataFrame(raw["daily"]).rename(columns={
        "time": "fecha",
        "temperature_2m_max": "temp_max_c",
        "temperature_2m_min": "temp_min_c",
        "precipitation_sum": "precipitacion_mm",
        "wind_speed_10m_max": "viento_max_kmh",
    })
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
    df.insert(0, "ciudad", CITY)
    df["temp_media_c"] = ((df["temp_max_c"] + df["temp_min_c"]) / 2).round(1)
    df["llovio"] = df["precipitacion_mm"] > 0
    return df.dropna().reset_index(drop=True)


def save(df: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    df.to_csv(OUTPUT_DIR / "data_extracted.csv", index=False)
    registros = json.loads(df.assign(fecha=df["fecha"].astype(str)).to_json(orient="records"))
    with open(OUTPUT_DIR / "data_extracted.json", "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)


def main() -> None:
    print(f"Consultando clima diario de {CITY} entre {START_DATE} y {END_DATE}...")
    raw = get_data()
    df = transform(raw)
    save(df)
    print(f"Listo: {len(df)} días guardados en data/data_extracted.csv y data/data_extracted.json")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        print(e, file=sys.stderr)
        sys.exit(1)
