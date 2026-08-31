# Arquitectura de Datos en Python y Ciencia Abierta
## Antonio Alfonso.

Material público del seminario impartido por Antonio Alfonso el 2 de septiembre de 2026.

El repositorio sigue un experimento docente: dos personas deben asignar límites de velocidad a una naranja y a un plátano sin conocer un código previo. El caso permite recorrer el ciclo completo de una investigación: pregunta, literatura, protocolo, dato, análisis, control de versiones y depósito citable.

> **SIMULACIÓN DOCENTE.** Los 500 registros son sintéticos. No proceden de participantes reales, no validan señales de tráfico y no demuestran una asociación universal.

## Mapa del repositorio

| Carpeta                | Contenido                                                               |
| ---------------------- | ----------------------------------------------------------------------- |
| `00_PRESENTACION`      | Diapositivas visibles del seminario, sin notas privadas del ponente     |
| `00_CUADERNO_Y_MANUAL` | Cuaderno editable, versión imprimible, manual y plantilla de proyecto   |
| `01_LITERATURA`        | Tabla de evidencia, referencias y guía de Elicit/ResearchRabbit         |
| `02_PROTOCOLO`         | Diseño, prerregistro, DMP, ética, consentimiento y borrador de Prolific |
| `03_MINIWEB`           | Aplicación Streamlit del experimento                                    |
| `04_DATOS`             | Datos sintéticos, archivo público, diccionario y esquemas               |
| `05_ANALISIS`          | Cuaderno Jupyter, HTML autocontenido, scripts, figuras y resultados     |
| `08_PUBLICACION`       | Licencias, cita, metadatos y notas del release de demostración          |

## Resultado confirmatorio

La primera respuesta es el único resultado confirmatorio:

```text
H0: E[velocidad_primera | naranja_primero]
    ≤ E[velocidad_primera | platano_primero]

H1: E[velocidad_primera | naranja_primero]
    > E[velocidad_primera | platano_primero]
```

La simulación contiene 500 registros, 20 exclusiones temporales y 480 observaciones analíticas. La regla es estricta: un tiempo inferior a 2,0 segundos se excluye; exactamente 2,0 segundos permanece.

## Leer o ejecutar el análisis

La opción más sencilla es abrir:

```text
05_ANALISIS/laboratorio_velocidad_frutas.html
```

Para ejecutarlo en Jupyter:

```powershell
cd 05_ANALISIS
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-analisis.txt
jupyter notebook laboratorio_velocidad_frutas.ipynb
```

## Ejecutar la miniweb

```powershell
cd 03_MINIWEB
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

El modo docente se abre en:

```text
http://localhost:8501/?modo=docente
```

El panel exige un hash de contraseña en un archivo local `.streamlit/secrets.toml`. El repositorio contiene únicamente el ejemplo; nunca debe versionarse el secreto real.

## Qué no contiene este repositorio

- Identificadores reales de Prolific.
- Secretos HMAC o contraseñas.
- Bases SQLite recibidas.
- Mapa restringido de bonificaciones.
- Notas del ponente o cuaderno resuelto.
- Datos de participantes reales.

## De Git a un DOI

Git conserva la historia local. GitHub permite inspeccionarla. Un release identifica una versión. Tras habilitar este repositorio en la integración GitHub–Zenodo, Zenodo archiva cada nuevo release y genera su DOI.

La versión prevista para la demostración es `v1.0.0-demo`. Crear un tag o un depósito Sandbox no convierte el caso sintético en evidencia empírica.

## Licencias y cita

- Código: MIT, según `LICENSE`.
- Datos y materiales docentes: CC BY 4.0, según `08_PUBLICACION/LICENSE_DATOS.txt`.
- Cita recomendada: `CITATION.cff`.

Los hashes de los archivos versionados se recogen en `MANIFIESTO_SHA256.txt`.
