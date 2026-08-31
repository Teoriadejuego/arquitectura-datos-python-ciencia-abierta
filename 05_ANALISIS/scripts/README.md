# Generación de datos sintéticos

`generar_datos_sinteticos.py` ejecuta únicamente el Prompt 12. Con la semilla
congelada `20260902` crea 500 respuestas docentes sintéticas, incluidos veinte
speeders equilibrados, y valida recuentos, soporte, privacidad y métricas de
referencia antes de escribir:

- `04_DATOS/sinteticos_raw/respuestas_sinteticas_500.csv`
- `04_DATOS/sinteticos_raw/resumen_generacion.json`

Ejecución portátil desde la raíz del proyecto, con el entorno de análisis activado:

```powershell
.\.venv_analisis\Scripts\Activate.ps1
python .\05_ANALISIS\scripts\generar_datos_sinteticos.py
```

El CSV es una simulación reproducible: no contiene personas, identificadores ni
respuestas observadas, y todas las filas declaran `origen_dato=sintetico_docente`.

## Cuaderno autoguiado de 30 minutos

`construir_cuaderno_autoguiado.py` reconstruye el cuaderno limpio destinado al
alumnado. El recorrido enseña a leer código y a realizar cambios controlados:
cargar el CSV, inspeccionar la tabla, aplicar la exclusión prerregistrada,
calcular medias por grupo, cambiar colores, leer el Welch y reconocer una
regresión con su tabla.

```powershell
python .\05_ANALISIS\scripts\construir_cuaderno_autoguiado.py
python -m jupyter lab .\05_ANALISIS\laboratorio_velocidad_frutas.ipynb
```

El análisis extenso no se ha eliminado. Permanece en `analizar_datos.py` para
reproducibilidad y auditoría, separado de la introducción presencial.
