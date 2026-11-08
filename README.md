# Extracción de datos climáticos vía API

Script en Python que consulta la API pública de [Open-Meteo](https://open-meteo.com/) para obtener el clima diario de Montevideo (temperatura máxima y mínima, precipitación y viento máximo), limpia la respuesta y la guarda en CSV y JSON.

## Archivos

- `extract.py`: script de extracción.
- `.env.example`: plantilla de configuración. Se copia como `.env`.
- `.gitignore`: evita subir el archivo `.env` y archivos temporales.
- `requirements.txt`: dependencias.
- `data/data_extracted.csv` y `data/data_extracted.json`: datos obtenidos (octubre 2026).

## Instalación

Requiere Python 3.9 o superior.

```bash
git clone https://github.com/deborahamarantef-art/extraccion-api-clima.git
cd extraccion-api-clima

python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS / Linux: source .venv/bin/activate

pip install -r requirements.txt
```

## Configuración

Copiar la plantilla y, si se quiere, cambiar ciudad, coordenadas o fechas:

```bash
cp .env.example .env        # en Windows: copy .env.example .env
```

El script lee la configuración con `python-dotenv`. Open-Meteo no pide API key, pero la variable `API_KEY` queda preparada para usar otra API sin escribir credenciales en el código. Si no existe el `.env`, el script usa los valores por defecto (Montevideo, octubre 2026).

## Ejecución

```bash
python extract.py
```

Salida esperada:

```
Consultando clima diario de Montevideo entre 2026-10-01 y 2026-10-31...
Listo: 31 días guardados en data/data_extracted.csv y data/data_extracted.json
```

## Qué hace el script

1. **Extracción:** petición `GET` con `requests` a `archive-api.open-meteo.com/v1/archive`.
2. **Manejo de errores:**
   - 400 (parámetros inválidos) y 404 (recurso inexistente): muestra el motivo y termina sin reintentar.
   - 5xx, timeout o falta de conexión: reintenta hasta `MAX_RETRIES` veces con espera creciente.
   - Si todo falla, muestra un mensaje claro y termina con código 1, sin traceback.
3. **Transformación:** descarta los metadatos de la respuesta (coordenadas, tiempo de generación, unidades), renombra las columnas al español y agrega `temp_media_c` y `llovio`.
4. **Persistencia:** guarda el resultado en `data/data_extracted.csv` y `data/data_extracted.json`.

## Columnas del resultado

| Columna | Descripción |
|---|---|
| ciudad | Ciudad consultada |
| fecha | Día (AAAA-MM-DD) |
| temp_max_c | Temperatura máxima (°C) |
| temp_min_c | Temperatura mínima (°C) |
| precipitacion_mm | Lluvia acumulada del día (mm) |
| viento_max_kmh | Velocidad máxima del viento a 10 m (km/h) |
| temp_media_c | Promedio entre máxima y mínima (°C) |
| llovio | True si la precipitación fue mayor a 0 |
