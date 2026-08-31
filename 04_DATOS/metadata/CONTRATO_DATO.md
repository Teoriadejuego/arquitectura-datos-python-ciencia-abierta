# Contrato del dato — La velocidad de las frutas

**Versión:** 1.0.0-demo  
**Fecha:** 28 de agosto de 2026  
**Alcance:** datos sintéticos del seminario y especificación preventiva para una futura captura en Prolific. La ejecución docente no recoge datos personales reales.

## 1. Regla central

Este paquete público contiene exclusivamente observaciones con:

```text
origen_dato = "sintetico_docente"
```

Un registro recibido de una persona real no puede convertirse en público mediante una simple supresión de columnas. Requeriría una evaluación de riesgo, una base jurídica y un proceso de publicación independientes. En este curso, los datos reales quedan fuera del repositorio; solo se publican sintéticos y resultados agregados no identificables.

La licencia CC BY 4.0 se aplica únicamente a archivos sintéticos o metadatos marcados como publicables. No alcanza identificadores de plataforma, claves HMAC, texto abierto, marcas temporales exactas, mapas de bonificación ni cualquier fichero restringido.

## 2. Cuatro capas

```text
CAPTURA
   │
   ▼
BRUTA ── HMAC + validación ──► RESTRINGIDA
                                   │
                                   ├── pagos y retirada: solo custodios
                                   │
                                   └── selección + derivación ──► ANALÍTICA
                                                                      │
                                                                      └── filtro de publicación
                                                                                │
                                                                                ▼
                                                                             PÚBLICA
```

| Capa | Contenido | Ubicación prevista | Acceso | Regla de modificación |
|---|---|---|---|---|
| **Bruta** | Respuesta tal como llega; parámetros Prolific; marcas temporales exactas; texto abierto. | Almacén cifrado fuera de Git. Para la simulación: `04_DATOS/sinteticos_raw/`, rotulado como sintético. | Custodio de datos. | Inmutable. Las correcciones se documentan como nueva derivación. |
| **Restringida** | Claves HMAC; texto y tiempos exactos; tabla de enlace; variables de emparejamiento, bonificación y pago. | Almacén cifrado separado, nunca incluido en GitHub, ZIP o Zenodo. | Custodio y responsable de pagos; mínimo privilegio. | Cambios trazados; tabla de pagos separada de respuestas. |
| **Analítica** | Variables experimentales, duraciones, categorías Regex y reglas de inclusión. Sin IDs Prolific, texto abierto, timestamps exactos ni pagos. | Entorno local de análisis; para sintéticos puede regenerarse desde el script. | Equipo analítico autorizado. | Se reconstruye mediante código; no se edita a mano. |
| **Pública** | Solo observaciones sintéticas, variables analíticas permitidas y metadatos. | `04_DATOS/publicos/` y depósito Sandbox de demostración. | Cualquier persona. | Release versionado; cualquier cambio crea una versión nueva. |

## 3. Identificadores y parámetros Prolific

La aplicación acepta por compatibilidad:

```text
PROLIFIC_PID
STUDY_ID
SESSION_ID
modo=docente
```

Los tres identificadores llegan a la capa bruta y nunca pasan a la analítica o pública. En la capa restringida se sustituyen por HMAC-SHA-256:

```python
participante_hmac = HMAC_SHA256(
    secreto_servidor,
    b"PROLIFIC_PID:" + normalizar(PROLIFIC_PID).encode("utf-8"),
).hexdigest()
```

Se aplica el mismo patrón, con prefijos de dominio distintos, a `STUDY_ID` y `SESSION_ID`. `normalizar` elimina espacios exteriores, conserva mayúsculas/minúsculas y rechaza cadenas vacías. El secreto:

- vive en una variable de entorno o gestor de secretos;
- no se guarda junto a los datos;
- no entra en código, GitHub, ZIP, OSF o Zenodo;
- tiene una versión (`hmac_version`) registrada en la capa restringida para permitir rotación controlada.

Un HMAC sigue siendo un identificador seudónimo y enlazable. Por eso tampoco es público.

## 4. Separación física de los pagos

El archivo de bonificación contiene únicamente lo necesario para pagar:

```text
pareja_id
simbolo_bonificacion
confianza_seleccionada
coincide_pareja
importe_bonificacion_eur
estado_pago
PROLIFIC_PID o clave de enlace autorizada
```

Se guarda en la capa restringida. No se une al CSV analítico salvo dentro de un proceso temporal y autorizado para el análisis secundario de confianza; el resultado que sale de ese proceso es agregado. La inclusión, el contraste Welch y el pago base no dependen de `coincide_pareja` ni de `importe_bonificacion_eur`.

## 5. Texto abierto y tiempo

`respuesta_abierta` puede contener información personal no solicitada. Permanece en la capa restringida. El análisis aplica patrones Regex y produce `categoria_motivo`, una lista multietiqueta entre:

```text
forma | color | fisica | cultura | contraste | azar | sin_clasificar
```

El texto original no acompaña a la categoría hacia la capa analítica. Ningún ejemplo textual se publica sin revisión humana; en el curso solo se muestran frases generadas sintéticamente.

Las marcas `inicio_utc`, `primera_render_utc`, `segunda_render_utc` y `fin_utc` son exactas y restringidas. Las duraciones derivadas `tiempo_primera_s` y `tiempo_segunda_s` pueden formar parte de la capa analítica. Solo se publican porque el conjunto es sintético.

## 6. Transformaciones deterministas

| Paso | Entrada | Salida | Regla |
|---:|---|---|---|
| 1 | Parámetros Prolific brutos | HMAC restringidos | HMAC-SHA-256 con prefijo de dominio y secreto externo. |
| 2 | Orden y respuestas por pantalla | Variables por fruta | Mapear según `orden`; nunca inferir desde la magnitud elegida. |
| 3 | Respuestas por fruta | `velocidad_primera_kmh` | Si `naranja_primero`, copiar naranja; si `platano_primero`, copiar plátano. |
| 4 | Dos velocidades | `diferencia_platano_menos_naranja` | Plátano menos naranja, en km/h. |
| 5 | Dos tiempos | `incluida`, `motivo_exclusion` | Excluir si cualquiera es `< 2.0`; `2.000` permanece. |
| 6 | Texto abierto restringido | `categoria_motivo` | Normalización Unicode y patrones Regex congelados; salida multietiqueta. |
| 7 | IDs internos sintéticos | `registro_id` público | Usar `SIM-000001` a `SIM-000500`; no deriva de un ID de plataforma. |
| 8 | Capa analítica sintética | Capa pública | Lista positiva de columnas; `origen_dato` debe ser `sintetico_docente`. |

No se abre ni se guarda el CSV con Excel durante el pipeline. Los tipos, categorías y codificación UTF-8 se validan por código.

## 7. Lista positiva pública

El archivo público puede contener únicamente:

```text
registro_id
orden
simbolo_primero
velocidad_primera_kmh
velocidad_naranja_kmh
velocidad_platano_kmh
confianza_naranja
confianza_platano
tiempo_primera_s
tiempo_segunda_s
diferencia_platano_menos_naranja
categoria_motivo
incluida
motivo_exclusion
origen_dato
version_app
```

`schema_publico.json` usa `additionalProperties: false`; cualquier columna extra hace fallar la exportación.

### Campos prohibidos en público

- `PROLIFIC_PID`, `STUDY_ID`, `SESSION_ID` o variantes de esos nombres;
- cualquier valor o columna cuyo nombre contenga `hmac`, `hash`, `token`, `cookie` o `ip`;
- `respuesta_abierta` o fragmentos del texto;
- timestamps exactos o fechas de participación por fila;
- `pareja_id`, elección de bonificación, coincidencia, importe o estado de pago;
- secretos, rutas locales, registros de servidor o cabeceras del navegador;
- datos con un `origen_dato` diferente de `sintetico_docente`.

## 8. Invariantes de calidad

El pipeline se detiene si falla una sola condición:

1. `registro_id` es único y no nulo.
2. `orden` pertenece a `{naranja_primero, platano_primero}`.
3. Las velocidades pertenecen a `{30, 50, 70, 90, 110, 130}`.
4. Las confianzas son enteros entre 0 y 100.
5. Los tiempos son numéricos, finitos y no negativos.
6. `simbolo_primero` concuerda con `orden`.
7. `velocidad_primera_kmh` coincide con la fruta mostrada primero.
8. `diferencia_platano_menos_naranja = velocidad_platano_kmh - velocidad_naranja_kmh`.
9. `incluida` y `motivo_exclusion` reproducen la frontera estricta `< 2.0`.
10. Exactamente `2.000` segundos no activa exclusión.
11. Toda fila pública declara `origen_dato=sintetico_docente`.
12. El conjunto público coincide exactamente con la lista positiva y no contiene patrones prohibidos.

## 9. Publicabilidad y licencia

| Objeto | ¿Puede publicarse? | Condición |
|---|---|---|
| CSV público sintético | Sí | Supera `schema_publico.json`; todas las filas declaran `sintetico_docente`. |
| Código, esquema y diccionario | Sí | No contienen secretos, valores HMAC ni rutas de almacenes reales. |
| Figuras y agregados sintéticos | Sí | Rótulo visible «simulación docente». |
| Datos analíticos reales por fila | No en este paquete | Requerirían evaluación independiente. |
| Parámetros o HMAC Prolific | No | Restringidos incluso tras retirar los IDs brutos. |
| Texto abierto | No | Solo categorías y agregados revisados. |
| Timestamps exactos | No | Solo duraciones sintéticas autorizadas. |
| Mapa de bonificación y pagos | No | Almacén restringido y propósito contable. |

La atribución de los archivos publicables se expresa con CC BY 4.0. La licencia no convierte datos personales o restringidos en material reutilizable.

## 10. Archivos normativos

- `diccionario_datos.csv`: definición por variable, capa y permiso.
- `schema_raw.json`: contrato técnico para un registro de captura, incluidas ausencias por abandono.
- `schema_publico.json`: contrato técnico cerrado para una fila pública sintética.
- `metadata_dataset.json`: procedencia, licencia, acceso y alcance del conjunto docente.

Si el código y este documento discrepan, el pipeline debe fallar y la discrepancia debe resolverse antes de crear el release. No se modifica un esquema publicado en silencio: se incrementa la versión y se registra la migración.
