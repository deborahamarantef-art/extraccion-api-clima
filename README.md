# Extraccion de datos de clima con API

Pre-entrega de Data Science II.

El script `extract.py` hace una peticion GET a la API de Open-Meteo y trae el clima diario de Montevideo de octubre 2026 (temperatura maxima, minima, lluvia y viento). Despues guarda los datos en `data/data_extracted.csv` y `data/data_extracted.json`.

## Como usarlo

1. Instalar las librerias:

```
pip install -r requirements.txt
```

2. Crear el archivo `.env` copiando `.env.example` (ahi estan la URL, las coordenadas y las fechas). Esta API no pide API key.

3. Ejecutar:

```
python extract.py
```

## Manejo de errores

- Si no hay conexion o la API no responde, el script muestra un mensaje y termina.
- Si la respuesta no es 200 (por ejemplo 404 o 500), muestra el codigo de error.
