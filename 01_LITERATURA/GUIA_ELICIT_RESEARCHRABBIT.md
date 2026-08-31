# Guía operativa: Elicit + ResearchRabbit

**Objetivo docente:** pasar de una intuición a un mapa de evidencia auditable en treinta minutos: quince para búsqueda y extracción; quince para red de citas.  
**Fecha de comprobación de interfaz:** 28 de agosto de 2026.

## Qué debe quedar al terminar

```text
consulta exacta
      ↓
tabla de candidatos
      ↓ verificación en el artículo
tabla de evidencia
      ↓
cuatro semillas fiables
      ↓
red de referencias y citas
      ↓
brecha: naranja frente a plátano aún no está probada
```

La herramienta acelera la localización y la extracción. La afirmación científica sigue dependiendo del artículo original.

---

# Parte A · Elicit: construir la tabla

## 1. Consulta exacta

### Consulta principal en español

Pegue sin modificar en **Find Papers**:

```text
¿Qué estudios experimentales han medido (a) si las personas asocian frutas o alimentos con «rápido» o «lento» y (b) si símbolos salientes permiten coordinar respuestas sin comunicación?
```

### Consulta principal en inglés

La terminología de la literatura está indexada principalmente en inglés. Use esta versión para comparar cobertura:

```text
Which experimental studies have measured (a) whether people associate fruits or foods with “fast” versus “slow” and (b) whether salient symbols enable coordination without communication?
```

### Consulta de límite vial en español

```text
¿Cómo varía la comprensión de símbolos de señales de tráfico entre países y poblaciones de conductores?
```

### Consulta de límite vial en inglés

```text
How does comprehension of traffic-sign symbols vary across countries and driver populations?
```

La consulta principal busca dos ramas deliberadas: correspondencias alimento–velocidad y coordinación focal. La consulta vial no busca confirmar la hipótesis; busca impedir una extrapolación regulatoria.

## 2. Acciones en pantalla

1. Abra [Elicit](https://elicit.com/) y elija **Find Papers**.
2. Pegue la consulta en inglés y ejecute la búsqueda.
3. Localice por título o DOI las cuatro fuentes nucleares de esta guía.
4. Pida las columnas desde el chat de **Research Agent**. La interfaz vigente añade columnas mediante conversación; ya no exige un botón separado *Add Column*.
5. Revise primero título, resumen, año y revista. Esto sirve para descartar falsos positivos, no para cerrar la extracción.
6. Abra cada artículo. Compruebe las cifras en **Methods**, **Results**, tablas o figuras.
7. Escriba página, sección, tabla o figura en `ubicacion_verificada`.
8. Exporte la tabla con **Export** en CSV o Excel; exporte las referencias en BIB o RIS si el plan disponible lo permite.

La exportación de tablas de **Find Papers** depende del plan de Elicit. Si no está habilitada, copie las cuatro filas verificadas a la plantilla local; no cambie de plan durante la clase.

## 3. Mensaje exacto para crear columnas

Pegue en el chat de **Research Agent**:

```text
Añade estas columnas a la tabla:
1) Población y N analizada.
2) País, idioma y contexto de reclutamiento.
3) Diseño, tratamiento, comparación y aleatorización.
4) Estímulos, tarea y opciones de respuesta.
5) Resultado primario y forma de medirlo.
6) Resultado cuantitativo exacto, con recuentos o tamaño de efecto.
7) Incertidumbre o prueba estadística.
8) Limitación reconocida por los autores.
9) Disponibilidad y licencia de datos y código.
10) DOI o identificador persistente.
11) Ubicación verificable: página, sección, tabla o figura.
12) Relación con nuestra pregunta: DIRECTA, SÍNTESIS, MECANISMO, LÍMITE o EXCLUIR.

Para N, usa la muestra analizada al final, no la reclutada al inicio. Si el artículo no informa un dato, escribe «NO INFORMADO»; no lo infieras. Separa el resultado observado de la interpretación de los autores. Incluye unidades y denominadores.
```

Elicit puede leer texto y determinadas tablas, pero algunas figuras o tablas complejas no se extraen correctamente. Una respuesta generada sin localización verificable queda como `PENDIENTE`, nunca como dato final.

## 4. Columnas mínimas y criterio de aceptación

| Columna | Qué debe contener | Rechazar si… |
|---|---|---|
| `poblacion_n` | Población, `N` reclutada y `N` analizada | mezcla sujetos con ensayos |
| `pais_idioma` | País, idioma y plataforma | deduce nacionalidad por afiliación del autor |
| `diseno` | Entre/dentro de sujetos, asignación y comparador | dice solo «experimento» |
| `estimulos_tarea` | Objeto mostrado, pregunta y respuestas permitidas | omite que la elección era binaria o abierta |
| `outcome_primario` | Variable y codificación | sustituye variable por interpretación |
| `resultado` | Recuentos, medias o tamaño de efecto con denominador | ofrece únicamente `p<0,05` |
| `incertidumbre` | IC, error estándar o prueba exacta | inventa un IC no publicado |
| `limitacion` | Sesgo de muestra, tarea o generalización | usa una crítica genérica sin relación con el diseño |
| `datos_codigo` | URL, licencia y archivos; o `NO IDENTIFICADO` | confunde artículo abierto con datos abiertos |
| `doi_id` | DOI, PMID, JSTOR u otro identificador | enlaza solo una búsqueda web |
| `ubicacion_verificada` | Página, sección, tabla o figura | la celda no permite volver al pasaje |
| `relacion` | `DIRECTA`, `SÍNTESIS`, `MECANISMO`, `LÍMITE`, `EXCLUIR` | presenta evidencia indirecta como prueba directa |

## 5. Las cuatro filas que deben aparecer

| Semilla | Clasificación | Razón |
|---|---|---|
| Woods et al. (2013), `10.1068/i0586` | `DIRECTA` | prueba limón/ciruela pasa frente a rápido/lento |
| Spence (2023), `10.1163/22134808-bja10096` | `SÍNTESIS` | resume limón rápido y ciruela pasa/plátano lentos; no aporta muestra nueva |
| Mehta, Starmer y Sugden (1994), JSTOR `2118074` | `MECANISMO` | muestra cómo emerge un punto focal bajo incentivos de coordinación |
| Shinar et al. (2003), `10.1080/0014013032000121615` | `LÍMITE` | documenta heterogeneidad intercultural en comprensión de señales |

## 6. Qué hacemos con la tabla

La tabla cumple cinco trabajos:

1. **Separar candidatos de evidencia.** Una fila encontrada por IA no entra en el argumento hasta verificar el original.
2. **Evitar sustituciones silenciosas.** Limón no equivale a naranja; rápido/lento no equivale a 30–130 km/h.
3. **Registrar una decisión.** Cada artículo queda incluido, contextualizado o excluido con una razón.
4. **Crear semillas fiables.** Solo los artículos verificados pasan a ResearchRabbit.
5. **Definir la contribución.** La celda vacía importante es el contraste naranja–plátano: esa ausencia convierte el ejercicio en extensión, no en reproducción de un hallazgo.

## 7. Guion de quince minutos

| Minuto | Acción visible | Frase del ponente | Objeto que queda |
|---:|---|---|---|
| 00–02 | Pegar la consulta inglesa | «No busco una respuesta; busco candidatos a los que pueda pedir cuentas.» | Consulta fechada |
| 02–05 | Localizar Woods y Spence | «Aquí aparece el salto peligroso: el limón sí fue probado; la naranja, no.» | Dos filas candidatas |
| 05–08 | Pedir las doce columnas | «Una revisión útil no es una carpeta de PDF. Es una matriz de decisiones.» | Esquema de extracción |
| 08–12 | Abrir Woods y verificar `54/27` | «La cifra vive en Results, no en el resumen generado.» | Celda con página |
| 12–14 | Añadir Mehta y Shinar | «Una fuente explica coordinación; la otra limita la pretensión vial.» | Cuatro clases de evidencia |
| 14–15 | Exportar | «Congelamos lo que sabemos y, sobre todo, lo que todavía no sabemos.» | CSV y BIB |

**Contingencia de sesenta segundos:** abrir `literatura_verificada.csv` y señalar `relacion_con_hipotesis`. La herramienta puede fallar; la distinción epistemológica permanece.

---

# Parte B · ResearchRabbit: reconstruir la conversación

## 1. Colección y subcolecciones

Cree la colección:

```text
VELOCIDAD_FRUTAS_CORE
```

Organícela en tres subcolecciones:

```text
01_ALIMENTO_VELOCIDAD
02_COORDINACION_FOCAL
03_COMPRENSION_SENALES
```

No use las cuatro fuentes juntas en la primera expansión. Representan conversaciones distintas y una búsqueda mezclada diluye la señal.

## 2. Semillas exactas

### `01_ALIMENTO_VELOCIDAD`

```text
10.1068/i0586
10.1163/22134808-bja10096
```

### `02_COORDINACION_FOCAL`

El artículo no tiene DOI verificado. Busque el título exacto:

```text
The Nature of Salience: An Experimental Investigation of Pure Coordination Games
```

Confirme autores, año, revista, volumen y páginas antes de seleccionarlo:

```text
Mehta; Starmer; Sugden · 1994 · American Economic Review 84(3) · 658–673
```

### `03_COMPRENSION_SENALES`

```text
10.1080/0014013032000121615
```

## 3. Acciones en la interfaz vigente

1. Elija **Start from an article** o pegue un DOI/título en la barra de búsqueda.
2. Marque de una a tres semillas y pulse **Find Related Articles**. En la versión posterior a octubre de 2025, esta acción equivale a buscar *Similar Work*.
3. Para antecedentes, pulse la burbuja de búsqueda superior y cambie **Search across…** a **All References**.
4. Para trabajos posteriores, cambie **Search across…** a **All Citations**.
5. Revise lista y mapa. Los puntos conectados indican relaciones bibliográficas, no replicación ni calidad.
6. Guarde candidatos prometedores en `PENDIENTES_VERIFICAR`.
7. Abra el artículo original y complete la tabla de Elicit antes de moverlo a una subcolección nuclear.
8. Exporte las referencias seleccionadas en BibTeX para compararlas con `REFERENCIAS.bib`.

## 4. Tres recorridos concretos

### Recorrido 1 · De dónde sale «plátano lento»

1. Seleccione `SPENCE2023`.
2. Abra **All References**.
3. Busque los trabajos citados en el párrafo de la p. 321.
4. Marque cuáles prueban plátano directamente y cuáles solo repiten una afirmación previa.
5. No asigne un tamaño de efecto hasta encontrar datos primarios.

### Recorrido 2 · Cómo medimos coordinación

1. Seleccione `MEHTA1994`.
2. Explore **All Citations**.
3. Identifique estudios que reutilizan el índice de coordinación.
4. Compare `Σ p(v)²` con la corrección sin reemplazo del artículo.
5. Registre si cada trabajo paga por coincidencia real o estima coincidencia desde la distribución.

### Recorrido 3 · Por qué una señal no es universal

1. Seleccione `SHINAR2003`.
2. Explore **All Citations**.
3. Busque réplicas, rediseños ergonómicos y nuevos países.
4. Extraiga qué cambia: familiaridad, estandarización, población, contexto o formato de respuesta.
5. Conserve la heterogeneidad; no la resuma con una media mundial sin justificarla.

## 5. Preguntas para leer el mapa

- ¿Qué artículo conecta correspondencias sensoriales y decisiones de diseño?
- ¿La afirmación sobre el plátano remite a datos o se repite entre revisiones?
- ¿Qué trabajos distinguen saliencia primaria de razonamiento estratégico?
- ¿Qué señales funcionan fuera del país donde son familiares?
- ¿Qué nodo recibe muchas citas pero carece de datos abiertos?
- ¿Dónde cambia la tarea: rápido/lento, elección numérica, respuesta abierta o coordinación pagada?

## 6. Regla para incorporar un artículo

Un artículo pasa de `PENDIENTES_VERIFICAR` a una colección nuclear solo si:

- [ ] su identidad coincide por título, autores, año y DOI o identificador;
- [ ] la muestra y la tarea se han leído en el original;
- [ ] el resultado incluye denominador y ubicación;
- [ ] la disponibilidad de datos y código se comprobó por separado;
- [ ] su relación con la hipótesis está clasificada;
- [ ] no convierte una asociación agregada en afirmación de universalidad o seguridad.

## 7. Guion de quince minutos

| Minuto | Acción visible | Pregunta al aula | Objeto que queda |
|---:|---|---|---|
| 00–03 | Crear colección y tres subcolecciones | «¿Por qué no conviene mezclar desde el inicio tres literaturas?» | Arquitectura de colección |
| 03–06 | Introducir cuatro semillas | «¿Qué papel cumple cada una: dato, síntesis, mecanismo o límite?» | Núcleo verificado |
| 06–09 | `SPENCE2023` → **All References** | «¿Quién midió realmente el plátano?» | Cadena hacia atrás |
| 09–12 | `MEHTA1994` → **All Citations** | «¿Cómo ha evolucionado la medición de coordinación?» | Cadena hacia delante |
| 12–14 | `SHINAR2003` → mapa | «¿Qué le hace la cultura a una señal aparentemente simple?» | Clúster vial |
| 14–15 | Guardar un candidato en pendientes | «Una arista es una invitación a leer, no un sello de calidad.» | Próxima lectura trazable |

**Contingencia de sesenta segundos:** proyectar `TABLA_EVIDENCIA_VERIFICADA.md`, dibujar cuatro nodos y unir `WOODS2013 → SPENCE2023`. Añadir `MEHTA1994` como mecanismo y `SHINAR2003` como límite.

---

# Resultado intelectual del bloque

El alumnado debe poder formular esta frase sin añadir nada:

> «Existe evidencia directa de que el limón se asocia con rapidez y la ciruela pasa con lentitud, junto con una síntesis que incluye al plátano entre los alimentos lentos. La literatura de coordinación explica por qué una opción compartida puede concentrar respuestas; la literatura vial demuestra que esa concentración no basta para afirmar universalidad ni seguridad. Naranja frente a plátano sigue siendo nuestra hipótesis.»

## Fuentes operativas de las herramientas

- Elicit, creación de columnas mediante Research Agent: [Create and save columns in Elicit](https://support.elicit.com/en/articles/14758162-create-and-save-columns-in-elicit).
- Elicit, exportación de tablas y referencias: [Export your data from Elicit](https://support.elicit.com/en/articles/14758189-export-your-data-from-elicit).
- Elicit, límites de extracción desde tablas y figuras: [Extracting data from a table or figure](https://support.elicit.com/en/articles/14758168-extracting-data-from-a-table-or-figure-within-a-paper-in-column-answers).
- ResearchRabbit, búsqueda actual: [How to search in ResearchRabbit](https://learn.researchrabbit.ai/en/articles/12454528-how-to-search-in-researchrabbit).
- ResearchRabbit, similares: [Similar Work](https://learn.researchrabbit.ai/en/articles/12454538-how-do-i-search-similar-work-in-the-new-researchrabbit).
- ResearchRabbit, antecedentes: [Earlier Work / All References](https://learn.researchrabbit.ai/en/articles/12454543-how-do-i-search-earlier-work-in-the-new-researchrabbit).
- ResearchRabbit, posteriores: [Later Work / All Citations](https://learn.researchrabbit.ai/en/articles/12454547-how-do-i-search-later-work-in-the-new-researchrabbit).

## Archivos de esta carpeta

- `TABLA_EVIDENCIA_VERIFICADA.md`: síntesis argumental y ubicaciones.
- `literatura_verificada.csv`: tabla reutilizable en Python o una hoja de cálculo.
- `REFERENCIAS.bib`: cuatro referencias nucleares en BibLaTeX/BibTeX.
- `GUIA_ELICIT_RESEARCHRABBIT.md`: recorrido docente.
