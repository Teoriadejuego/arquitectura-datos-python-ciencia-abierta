# Miniweb · La velocidad de las frutas

Aplicación Streamlit independiente para una demostración docente del experimento.
El modo predeterminado es `demo`; no despliega nada, no activa pagos y guarda sus
respuestas en una SQLite **recibida** separada de los 500 registros sintéticos.

## Contenido

- `app.py`: flujo participante y panel docente protegido.
- `storage.py`: secuencia 1:1, HMAC y transacciones SQLite idempotentes.
- `analysis.py`: agregados y gráficos separados por fuente.
- `assets/`: copias controladas de los dos SVG y su documentación geométrica.
- `data/velocidad_frutas_publico.csv`: copia exacta del CSV público sintético.
- `.streamlit/secrets.toml.example`: configuración sin secretos reales.

La SQLite recibida, sus archivos WAL/SHM, el entorno virtual y `secrets.toml`
quedan excluidos por `.gitignore`.

## Ejecución local

Desde esta carpeta, en PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abra la URL local impresa por Streamlit. Sin parámetros se genera un token opaco
de demostración en la URL para que una recarga recupere la misma asignación. Ese
token no es un identificador de Prolific y solo se almacena como HMAC en SQLite.

## Modos

### Demo local, predeterminado

```text
http://localhost:8501/
```

Presenta todo el flujo y guarda en `data/respuestas_recibidas.sqlite3`. La
secuencia tiene 50 bloques de 10 asignaciones, cinco por orden en cada bloque,
con semilla congelada `20260902`. Una asignación no se libera al abandonar.

### Panel docente

```text
http://localhost:8501/?modo=docente
```

El parámetro solo abre el formulario de acceso: nunca autoriza el panel. Debe
existir `DOCENTE_PASSWORD_HASH` en un secreto externo. Para generar una entrada
PBKDF2 en un terminal seguro:

```powershell
.\.venv\Scripts\python.exe -c "import hashlib,secrets,getpass; p=getpass.getpass().encode(); s=secrets.token_bytes(16); d=hashlib.pbkdf2_hmac('sha256',p,s,600000); print('pbkdf2_sha256$600000$'+s.hex()+'$'+d.hex())"
```

El panel mantiene pestañas independientes:

- **SINTÉTICA · SIMULACIÓN DOCENTE**: copia pública congelada, gráficos y descarga
  del CSV de lista positiva.
- **RECIBIDA · RESTRINGIDA**: únicamente recuentos y agregados; no muestra ni
  descarga HMAC, texto abierto o timestamps exactos, y nunca se concatena con la
  muestra sintética.

### Live, bloqueado por defecto

Además de `?modo=live`, el servidor debe configurar `LIVE_ENABLED=true`, un
`HMAC_SECRET` de al menos 32 bytes, `HMAC_VERSION`, correo de soporte, URL de
finalización válida y una `DATABASE_PATH` absoluta fuera del código. Los tres
parámetros son obligatorios y se validan antes de reservar una asignación:

```text
?modo=live&PROLIFIC_PID=...&STUDY_ID=...&SESSION_ID=...
```

Los valores brutos solo transitan por la URL y memoria inmediata. La aplicación
guarda HMAC-SHA-256 con dominios separados y no registra ni exporta IDs brutos.
Revise también que el proxy y el alojamiento no conserven query strings en sus
logs. Rotar el secreto o su versión durante un estudio rompe la deduplicación.

El botón de retorno a Prolific aparece únicamente después de que SQLite confirme
`estado=completo`. Un error de almacenamiento conserva la misma etapa, muestra
el canal de ayuda y no ofrece redirección.

## Límites y paso a producción

SQLite local y el sistema de archivos de Streamlit Community Cloud **no ofrecen
persistencia de producción**: pueden reiniciarse, no coordinan varias réplicas y
no sustituyen copias de seguridad, cifrado, control de acceso ni retención. Antes
de recoger respuestas reales hacen falta aprobación institucional, contrato de
datos real versionado, almacenamiento duradero externo, revisión de logs,
contactos sin marcadores y prueba integral de recuperación.

Streamlit puro registra como inicio temporal la primera ejecución de servidor
que muestra cada estímulo. No afirma confirmar el instante exacto de pintado en
el navegador; esa precisión necesitaría un componente cliente validado.

Los resultados y señales son docentes: no demuestran seguridad vial,
universalidad cultural ni una velocidad correcta.

## Pruebas locales

El Prompt 16 incorpora pytest y Streamlit AppTest como dependencias de
desarrollo, sin añadirlas al entorno de ejecución de producción:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest
```

También puede ejecutar el flujo local reproducible:

```powershell
.\scripts\qa_local.ps1
```

La suite usa únicamente SQLite temporales y no escribe respuestas ni secretos
en `data/`.

## Procedencia de copias controladas

- `assets/senal_naranja.svg`: copia de `09_ASSETS/estimulos/senal_naranja.svg`.
- `assets/senal_platano.svg`: copia de `09_ASSETS/estimulos/senal_platano.svg`.
- `assets/control_geometrico.json` y `assets/texto_alternativo.csv`: controles de
  procedencia y accesibilidad de esos estímulos.
- `data/velocidad_frutas_publico.csv`: copia de
  `04_DATOS/publicos/velocidad_frutas_publico.csv`.

No se modifica ni reutiliza la miniweb anterior.
