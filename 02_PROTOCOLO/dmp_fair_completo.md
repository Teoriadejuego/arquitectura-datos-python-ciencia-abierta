# Plan de Gestión de Datos FAIR · Caso completado

## Identificación

| Campo | Valor |
|---|---|
| Proyecto | La velocidad de las frutas |
| Responsable | Antonio Alfonso |
| Custodio de datos | Antonio Alfonso |
| Institución | Seminario «Arquitectura de Datos en Python y Ciencia Abierta» |
| Versión del DMP | 1.0.0-demo |
| Fecha | 28 / 08 / 2026 |
| Próxima revisión | 02 / 09 / 2026, antes del release docente |
| Registro ético / OSF | Simulación local; sin registro externo |

**Origen previsto**  
[ ] Personas reales · [ ] Datos administrativos · [ ] Datos secundarios · [x] Datos sintéticos · [ ] Otro

**Datos personales**  
[x] No se incluyen personas reales en el conjunto docente. La arquitectura restringida se conserva para demostrar cómo proteger una futura captura; no se publican identificadores, HMAC, texto, timestamps o pagos.

---

## 1. Inventario y nombres

| Capa | Activa | Contenido | Ubicación | Responsable |
|---|:---:|---|---|---|
| Original / bruta | [x] | 500 registros sintéticos tal como los emite el generador; parámetros Prolific nulos; texto y timestamps simulados | `04_DATOS/sinteticos_raw/` | Custodio |
| Restringida | [x] | HMAC, timestamps exactos, texto abierto y mapa de pagos exclusivamente simulados | Almacén local cifrado fuera de Git | Custodio |
| Analítica | [x] | Velocidades, confianza, duraciones, categorías Regex, inclusión y motivo | Entorno local; se regenera con `05_ANALISIS/scripts/` | Responsable de análisis |
| Pública | [x] | 500 filas sintéticas de la lista positiva y metadatos | `04_DATOS/publicos/` | Responsable del release |

**Convención:** `AAAA-MM-DD_objeto_capa_vNN.ext`; variables ASCII en `snake_case`; fechas ISO 8601 UTC; unidades incorporadas al nombre (`_kmh`, `_s`, `_eur`).

[x] Originales de solo lectura  
[x] SHA-256 al ingresar  
[x] Ninguna corrección manual  
[x] Cada cambio produce una derivación nueva

**Identificador local:** `curso_velocidad_frutas_2026:dataset:1.0.0-demo`

---

## 2. Almacenamiento y copias

| Objeto | Copia activa | Copia de seguridad | Cifrado | Frecuencia | Restauración |
|---|---|---|:---:|---|---|
| Original sintético | Equipo de trabajo, carpeta de solo lectura | Almacenamiento institucional cifrado | [x] | Tras cada versión congelada | 02 / 09 / 2026 |
| Restringido simulado | Contenedor cifrado fuera del repositorio | Copia institucional cifrada con acceso separado | [x] | Diaria mientras se usa | 02 / 09 / 2026 |
| Analítico | Entorno local reproducible | Código y manifiesto en Git; artefacto cifrado temporal | [x] | Cada ejecución aprobada | 02 / 09 / 2026 |
| Público | GitHub de demostración | Zenodo Sandbox / ZIP con SHA-256 | [x] tránsito | Cada release | 02 / 09 / 2026 |

[x] Dos soportes distintos  
[x] Una copia fuera del equipo principal  
[x] Ningún restringido en correo, USB no cifrado o nube personal  
[x] Git contiene solo código, metadatos y sintéticos autorizados  
[x] Secretos fuera del código y los datos  
[x] Restauración comprobada antes del release

**Incidencias:** aislar el contenedor y contactar con el custodio del proyecto.

---

## 3. Acceso y roles

| Rol | Persona / unidad | Original | Restringido | Analítico | Público | Motivo |
|---|---|:---:|:---:|:---:|:---:|---|
| Responsable / custodio | Antonio Alfonso | [x] | [x] | [x] | [x] | Gobierno, retirada y release |
| Analista | Responsable designado | [ ] | [ ] | [x] | [x] | Pipeline y resultados |
| Pagos | Responsable designado | [ ] | [x] | [ ] | [ ] | Conciliación de bonificaciones |
| Estudiantes | Participantes del seminario | [ ] | [ ] | [ ] | [x] | Reproducción con el kit público |
| Público | Cualquier persona | [ ] | [ ] | [ ] | [x] | Reutilización del release |

[x] Mínimo privilegio  
[x] MFA en cuentas institucionales, GitHub y depósitos  
[x] Sin cuentas compartidas  
[x] Revisión de permisos al inicio y al cierre del seminario  
[x] Revocación al abandonar el proyecto  
[x] Registro de accesos al contenedor restringido

**Base:** ejecución enteramente sintética. Una futura captura real requerirá autorización ética y base jurídica independientes.

---

## 4. Formatos y diccionario

| Objeto | Trabajo | Conservación | Estándar |
|---|---|---|---|
| Datos tabulares | CSV y Parquet | CSV UTF-8 y Parquet | RFC 4180; tipos fijados por esquema |
| Metadatos | JSON y CSV | JSON / JSON Schema Draft 2020-12 / CSV | UTF-8; nombres ASCII |
| Código | `.py` y `.ipynb` | `.py`, `.ipynb`, HTML ejecutado | Python y entorno versionado |
| Protocolo | Markdown | Markdown y PDF | UTF-8; versión Git |
| Figuras | SVG y PNG | SVG y PNG | SVG 1.1; PNG sin metadatos personales |

[x] Diccionario por variable  
[x] Tipo, rango, categorías y unidad  
[x] Procedencia, transformación y uso  
[x] Acceso y publicabilidad  
[x] JSON Schema para bruto y público  
[x] UTF-8  
[x] Entorno de software congelado

**Diccionario:** `04_DATOS/metadata/diccionario_datos.csv`  
**Esquemas:** `04_DATOS/metadata/schema_raw.json`; `schema_publico.json`

---

## 5. Flujo de transformación y procedencia

```text
GENERADOR, semilla 20260902
   ↓  CSV bruto + SHA-256
ORIGINAL SINTÉTICO, 500 filas, solo lectura
   ↓  validación de categorías y esquema
RESTRINGIDO SIMULADO
   ├── texto → normalización + Regex → categoria_motivo
   ├── timestamps → diferencias → tiempo_primera_s / tiempo_segunda_s
   └── mapa de pagos, semilla 20260903 → solo agregado
   ↓  reglas cerradas y derivaciones
ANALÍTICO
   ├── velocidad_primera según orden
   ├── diferencia = plátano − naranja
   └── incluida = ambos tiempos >= 2.0
   ↓  lista positiva + schema_publico.json
PÚBLICO, origen_dato = sintetico_docente
```

[x] Salidas generadas por código  
[x] Semillas `20260902` y `20260903` registradas  
[x] SHA-256 de entradas y salidas  
[x] `version_app` y commit registrados  
[x] Exclusiones con motivo  
[x] Sin edición manual  
[x] Desviaciones en registro aparte  
[x] Prueba desde carpeta limpia antes del release

**Pipeline previsto:** `05_ANALISIS/scripts/pipeline.py`  
**Manifiesto previsto:** `08_PUBLICACION/MANIFEST_SHA256.txt`

---

## 6. Publicación y licencia

| Objeto | Publicar | Destino | Licencia | Condición |
|---|:---:|---|---|---|
| Original sintético | [ ] | No se deposita como capa bruta | Sin licencia pública | Conserva estructura de captura y texto sintético |
| Restringido simulado | [ ] | Fuera de GitHub, ZIP y Zenodo | Sin licencia pública | Contiene enlaces, tiempos, texto o pagos simulados |
| CSV público sintético | [x] | GitHub y Zenodo Sandbox durante la demostración | CC BY 4.0 | Todas las filas: `sintetico_docente`; esquema aprobado |
| Código | [x] | GitHub y release | MIT | Sin secretos ni rutas restringidas |
| Protocolo y metadatos | [x] | GitHub y release | CC BY 4.0 | Sin valores identificables |
| Figuras y agregados | [x] | Presentación y release | CC BY 4.0 | Rótulo «simulación docente» |

[x] Versión y cita  
[x] `CITATION.cff` previsto  
[x] README reproducible  
[x] Revisión de privacidad  
[x] Lista positiva de 16 columnas  
[x] DOI solo cuando se cree un release deliberado; durante el curso, Sandbox

**Nunca públicos:** IDs Prolific, HMAC, secretos, timestamps exactos, `respuesta_abierta`, `pair_id`, fruta sorteada, coincidencia individual, importe y estado de pago.

---

## 7. Retención y borrado

| Objeto | Inicio | Conservación | Acción final | Responsable | Evidencia |
|---|---|---|---|---|---|
| IDs / tabla de enlace simulada | Cierre de QA | 90 días | Borrado seguro de activa y copia | Custodio | Acta sin valores |
| Texto abierto sintético restringido | Release v1.0.0-demo | 12 meses | Borrar capa restringida; conservar categorías | Custodio | Manifiesto actualizado |
| Timestamps exactos sintéticos | Release v1.0.0-demo | 12 meses | Borrar exactos; conservar duraciones públicas | Custodio | Acta de borrado |
| Mapa de pagos simulado | Cierre del seminario | 90 días | Borrado seguro; conservar agregado 83/250 | Custodio | Acta de conciliación simulada |
| Original sintético | Release v1.0.0-demo | 5 años | Revisar valor; borrar si el release reproduce todo | Responsable | Revisión 2031 |
| Analítico reproducible | Release v1.0.0-demo | 5 años | Regenerar o migrar formato antes de borrar | Responsable | Prueba de reproducción |
| Release público | Publicación deliberada | Al menos 10 años; preferencia por conservación indefinida | Migrar si el formato queda obsoleto | Responsable del depósito | DOI, versión y checksum |
| Código y metadatos | Release v1.0.0-demo | Al menos 10 años | Mantener release inmutable | Responsable del depósito | Git tag y DOI |

[x] Borrado de original y copias restringidas  
[x] Destrucción de secretos y temporales  
[x] Acta sin identificadores  
[x] Excepciones legales documentadas antes de ampliar un plazo  
[x] Revisión programada

Una futura recogida real fijará plazos propios antes de reclutar. Los plazos anteriores gobiernan esta simulación y no justifican conservar datos personales reales.

---

## 8. Riesgos

| Riesgo | Prob. | Impacto | Control | Responsable | Estado |
|---|---:|---:|---|---|---|
| Confundir sintéticos con respuestas observadas | M | A | `origen_dato=sintetico_docente` en cada fila y rótulo en figuras | Responsable | Cerrado |
| Filtrar IDs, HMAC, timestamps, texto o pagos | B | A | Lista positiva, `additionalProperties=false`, escaneo y revisión dual | Custodio | Cerrado para release |
| Sobrescribir el original | B | A | Solo lectura, SHA-256 y derivaciones nuevas | Custodio | Cerrado |
| Perder datos o claves de reproducción | B | M | Dos soportes, manifiesto y restauración | Responsable | Cerrado |
| Divergencia entre diccionario, esquema y código | M | M | Validación automática que detiene el pipeline | Analista | Abierto hasta QA final |
| Publicar el mapa de pagos por error | B | A | Carpeta externa, `.gitignore`, escaneo del ZIP y depósito | Custodio | Abierto hasta QA final |
| Presentar saliencia como seguridad universal | M | A | Límite explícito en metadatos, manual y diapositivas | Responsable | Abierto hasta revisión final |

**Incidencia:** aislar → preservar evidencia → avisar al custodio → evaluar alcance → corregir → registrar → notificar si procediera.

---

## 9. Comprobación FAIR

| Principio | Evidencia | Estado |
|---|---|:---:|
| **F · Encontrable** | Nombre estable, metadatos JSON, versión, `CITATION.cff` y DOI previsto. | [x] |
| **A · Accesible** | Público por HTTPS; condiciones y responsables definidos para capas no abiertas. | [x] |
| **I · Interoperable** | CSV UTF-8, Parquet, JSON Schema, tipos, categorías y unidades. | [x] |
| **R · Reutilizable** | CC BY 4.0 para datos sintéticos/documentos; MIT para código; procedencia y límites. | [x] |

## Aprobación

| Función | Nombre | Firma | Fecha |
|---|---|---|---|
| Responsable del proyecto | Antonio Alfonso | Pendiente | 02 / 09 / 2026 |
| Custodio de datos | Antonio Alfonso | Pendiente | 02 / 09 / 2026 |
| Revisión ética / protección de datos | Simulación docente; no aplica aprobación real | — | 02 / 09 / 2026 |
