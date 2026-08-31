# Prerregistro OSF — texto listo para copiar y pegar

> **ESTADO DOCENTE.** Este documento simula un prerregistro para el seminario «Arquitectura de Datos en Python y Ciencia Abierta». No es un registro público, no contiene participantes reales y no se ha enviado a OSF. Los 500 registros serán sintéticos. Una futura recogida real exigiría nueva revisión ética, consentimiento, DMP y registro previo.

---

## 1. Título del estudio

**La velocidad de las frutas: coordinación sobre señales ficticias de velocidad**

## 2. Resumen

Estudiaremos cómo personas adultas construyen una convención compartida ante dos señales ficticias sin números. Cada participante asignará una de seis velocidades a una naranja y a un plátano. El orden será aleatorio 1:1. Tras cada respuesta informará su confianza de 0 a 100 y, al final, podrá explicar su criterio en un campo opcional.

El resultado confirmatorio será exclusivamente la velocidad de la primera decisión. Compararemos entre sujetos a quienes ven primero la naranja con quienes ven primero el plátano. La segunda decisión ya puede estar condicionada por anclaje o contraste y se reservará para análisis secundarios. El estudio mide saliencia bajo una instrucción de coordinación; no valida señales de tráfico ni demuestra universalidad o seguridad vial.

## 3. Estado del estudio al congelar

Este es un ejercicio docente con datos sintéticos. En el momento de la congelación simulada:

- la pregunta, el diseño, las reglas de exclusión y el código analítico están especificados;
- no se ha ejecutado el generador de la muestra final;
- no se han calculado medias, gráficos, intervalos o valores `p` del conjunto final;
- Prolific, OSF, GitHub y Zenodo permanecen sin publicación real o en modo de demostración/Sandbox.

## 4. Pregunta de investigación

Cuando una persona adulta con permiso de conducir encuentra por primera vez una señal ficticia sin número, ¿asigna una velocidad media mayor a una naranja que a un plátano?

## 5. Hipótesis confirmatoria

Definimos:

```text
Y_i = velocidad_primera_kmh
A_i = 1 si simbolo_primero == "naranja"; 0 si == "platano"
Δ = E[Y_i | A_i = 1] − E[Y_i | A_i = 0]
```

Hipótesis unilateral:

```text
H0: Δ <= 0
H1: Δ > 0
```

La predicción es que la velocidad media asignada a la naranja cuando aparece primero será mayor que la velocidad media asignada al plátano cuando aparece primero.

## 6. Diseño

Diseño mixto con dos secuencias:

```text
naranja_primero: naranja → plátano
platano_primero: plátano → naranja
```

- **Factor entre sujetos:** símbolo mostrado primero.
- **Factor dentro del sujeto:** cada persona responde sobre naranja y plátano.
- **Asignación:** 1:1 mediante bloques permutados de 10, cinco secuencias de cada tipo, semilla docente `20260902`.
- **Persistencia:** la asignación se guarda antes de mostrar el primer estímulo y no se vuelve a sortear al recargar o reabrir la sesión.
- **Estímulos:** SVG negros de naranja y plátano, mismo marco, fondo, resolución y área aparente.
- **Orden de opciones:** ascendente y constante en ambas pantallas.

La asignación ocurre después del consentimiento. La secuencia vive en el servidor y no se muestra en el cliente.

## 7. Población y elegibilidad

La población operativa está formada por personas voluntarias que cumplen:

1. 18 años o más;
2. permiso de conducir vigente por autodeclaración;
3. comprensión suficiente del español;
4. consentimiento informado;
5. confirmación de que no responden mientras conducen;
6. ninguna participación previa detectable mediante el identificador pseudonimizado de la plataforma.

No se solicita edad exacta, número o fotografía del permiso, matrícula, IP, geolocalización, datos de salud o información sobre infracciones. El curso no reclutará personas reales: reproducirá esta población mediante datos sintéticos.

## 8. Tamaño muestral y regla de parada

Se fija `N = 500` registros recibidos antes de exclusiones, con 250 asignaciones previstas por secuencia. El generador docente producirá una muestra reproducible con semilla `20260902`.

La planificación toma `d = 0,25` como efecto estandarizado mínimo de interés docente, no como estimación de la literatura. Con 240 observaciones válidas por grupo, `α = 0,05` unilateral y asignación equilibrada, la potencia aproximada es 0,862. Con 250 por grupo sería 0,874.

No habrá análisis intermedio, parada por significación, ampliación por valor `p` ni reemplazo del contraste después de observar distribuciones. En una recogida real, abandonos o retiradas se informarían; no se reclutaría selectivamente para mejorar el resultado.

## 9. Procedimiento y medidas

Cada participante lee un escenario: conduce en un país desconocido cuyas señales de velocidad muestran símbolos en lugar de números. Debe elegir la categoría que cree que otra persona también escogerá.

En cada pantalla elige exactamente una velocidad:

```text
30, 50, 70, 90, 110 o 130 km/h
```

Después elige una confianza entera entre `0` y `100`, donde 0 significa ninguna confianza y 100 confianza completa. No existe valor preseleccionado.

Variables capturadas o derivadas:

```text
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
respuesta_abierta
categoria_motivo
incluida
motivo_exclusion
origen_dato
version_app
```

La pregunta abierta final es opcional: «En una frase, ¿qué le hizo asociar cada símbolo con la velocidad elegida? No incluya nombres ni información personal».

## 10. Resultado primario

El único resultado confirmatorio es:

```text
velocidad_primera_kmh
```

Se deriva sin consultar la magnitud:

```text
si orden == naranja_primero:
    velocidad_primera_kmh = velocidad_naranja_kmh
si orden == platano_primero:
    velocidad_primera_kmh = velocidad_platano_kmh
```

La segunda velocidad no entrará como resultado, predictor, covariable, estrato, imputación o criterio de éxito del contraste principal. Su única intervención en la selección confirmatoria será la completitud del protocolo y la regla temporal especificada antes de generar los datos.

## 11. Exclusiones

Las reglas se aplicarán sin consultar orden, velocidades, medias, gráficos o valores `p`.

### Tiempo de respuesta

Se excluirá el registro completo del análisis confirmatorio si se cumple al menos una condición:

```text
tiempo_primera_s < 2.0
tiempo_segunda_s < 2.0
```

La comparación utiliza el valor almacenado sin redondear. **Exactamente `2,00` segundos permanece incluido.** Si ambos tiempos son inferiores a 2,0, el motivo será `tiempos_ambos_menor_2`.

### Duplicados

La aplicación será idempotente. Si existen varias filas para la misma clave HMAC o `SESSION_ID`, se conservará el primer intento según la primera marca temporal del servidor y los posteriores se marcarán `duplicado_posterior`. Si el primer intento está incompleto, no se sustituirá por uno posterior. No se usarán IP, geolocalización o huella del dispositivo para inferir duplicados.

### Ausencias e integridad

- Falta una velocidad, una confianza o uno de los dos tiempos requeridos: `incompleto`; se excluye del conjunto confirmatorio.
- Falta `respuesta_abierta`: el registro permanece; el campo es opcional.
- Una velocidad fuera de `{30, 50, 70, 90, 110, 130}`, una confianza no entera o fuera de 0–100, o una incoherencia entre `orden`, `simbolo_primero` y `velocidad_primera_kmh`: el pipeline se detiene para auditoría. No se corrige el valor a mano.
- No se imputan resultados ni tiempos.

No se excluye por elegir extremos, repetir la velocidad en ambas frutas, baja confianza, texto breve, ausencia de una explicación opcional o respuesta contraria a la hipótesis. No hay criterio de acierto.

## 12. Análisis confirmatorio

Se crearán dos vectores dentro del conjunto válido:

```python
grupo_naranja = df.loc[
    df["orden"].eq("naranja_primero"),
    "velocidad_primera_kmh",
]

grupo_platano = df.loc[
    df["orden"].eq("platano_primero"),
    "velocidad_primera_kmh",
]
```

Se ejecutará:

```python
from scipy.stats import ttest_ind

resultado = ttest_ind(
    grupo_naranja,
    grupo_platano,
    equal_var=False,
    alternative="greater",
    nan_policy="raise",
)
```

- Test: Welch entre grupos independientes.
- Dirección: unilateral, naranja mayor que plátano.
- Alfa: `0,05`.
- Decisión: rechazar `H0` si, y solo si, `p < 0,05`.

Se informarán `n`, media y desviación estándar de cada grupo; diferencia media `naranja − plátano`; estadístico `t`; grados de libertad de Welch; valor `p` unilateral; intervalo bilateral del 95 % de la diferencia mediante error estándar y grados de libertad de Welch; y Cohen `d`.

El intervalo se calculará como:

```text
SE = sqrt(s_naranja²/n_naranja + s_platano²/n_platano)
IC95% = diferencia ± t_(0,975; gl_Welch) × SE
```

Cohen `d` se calculará de forma descriptiva con desviación estándar combinada:

```text
s_pooled = sqrt(
  [(n_naranja−1)s_naranja² + (n_platano−1)s_platano²]
  / (n_naranja+n_platano−2)
)

d = (media_naranja − media_platano) / s_pooled
```

Welch sigue siendo el contraste inferencial; `d` no impone igualdad de varianzas al test. Si `s_pooled = 0`, `d` se informará como no definido.

## 13. Análisis secundarios

Todos los análisis de esta sección son secundarios o exploratorios. No pueden reemplazar el resultado primario. Se mostrarán estimaciones e intervalos. Los siete valores `p` señalados se informarán en bruto y con ajuste Benjamini–Hochberg como una sola familia.

### 13.1 Diferencia dentro del sujeto

```text
delta_i = diferencia_platano_menos_naranja
        = velocidad_platano_kmh − velocidad_naranja_kmh
```

Se informará media, desviación, IC del 95 % y `ttest_rel` bilateral entre ambas velocidades. Este será el contraste secundario 1. Un valor negativo significa que la naranja recibió más velocidad dentro de la persona, pero puede incorporar anclaje y contraste.

### 13.2 Velocidades distintas

Se calculará la proporción:

```text
I(velocidad_naranja_kmh != velocidad_platano_kmh)
```

Se informará intervalo Wilson del 95 %, total y por orden. La asociación entre `distintas` y `orden` se evaluará en una tabla 2 × 2 con chi-cuadrado sin corrección de Yates; si alguna frecuencia esperada es menor que 5, se usará Fisher bilateral. Contraste secundario 2.

### 13.3 Efecto de orden

Se estimará con OLS y errores HC3:

```text
diferencia_platano_menos_naranja
    ~ C(orden, referencia="naranja_primero")
```

La prueba bilateral del coeficiente `platano_primero` será el contraste secundario 3.

### 13.4 Regresión de velocidades

Se ajustará:

```text
velocidad_naranja_kmh
    ~ velocidad_platano_kmh
    + C(orden, referencia="naranja_primero")
```

Estimación OLS con errores estándar HC3. Se informarán coeficientes, IC del 95 % y `R²`. Las pruebas bilaterales de la pendiente del plátano y del coeficiente de orden serán los contrastes secundarios 4 y 5. El modelo describe covariación; no produce un efecto causal de una respuesta sobre otra.

### 13.5 Distribución completa 2 × 6

Se construirá `simbolo_primero × velocidad_primera_kmh` y se aplicará:

```python
scipy.stats.chi2_contingency(tabla, correction=False)
```

Se informarán `χ²`, grados de libertad, `p`, residuos estandarizados y `V` de Cramér. Contraste secundario 6. Si alguna frecuencia esperada es menor que 5, el valor `p` se obtendrá con 100.000 permutaciones de la etiqueta entre sujetos, semilla `20260902`.

### 13.6 Coordinación

Para cada fruta y cada categoría `j`:

```text
C_plugin = Σ_j (m_j / N)²
C_sin_reemplazo = Σ_j m_j(m_j−1) / [N(N−1)]
```

Se informarán ambos índices y la diferencia naranja–plátano. Su IC percentil del 95 % se obtendrá mediante 10.000 remuestreos de participantes, semilla `20260902`. No se contrastará contra 1/6 porque no se supone equiprobabilidad de las seis opciones.

### 13.7 Confianza y coincidencia efectiva

Después del emparejamiento de bonificaciones se ajustará, dentro del entorno restringido:

```text
coincide_pareja
    ~ confianza_seleccionada/10
    + C(simbolo_bonificacion)
```

Regresión logística con errores agrupados por `pair_id`. La prueba bilateral de confianza será el contraste secundario 7. Solo se publicarán coeficientes y agregados; nunca el mapa de parejas o pagos.

### 13.8 Clasificación Regex del texto

El texto opcional se pasará a minúsculas, se normalizará Unicode y se eliminarán tildes para emparejar patrones congelados. La clasificación será multietiqueta:

```text
forma      r"\b(forma|redond\w*|curv\w*|alarg\w*|punta\w*|geometri\w*|siluet\w*)\b"
color      r"\b(color|amarill\w*|negro|negra|oscur\w*)\b"
fisica     r"\b(peso|pesad\w*|liger\w*|rodar|rued\w*|aerodin\w*|fricci\w*)\b"
cultura    r"\b(cultur\w*|costumbre\w*|trafic\w*|carretera\w*|deporte\w*|marca\w*)\b"
contraste  r"\b(contraste|compar\w*|diferent\w*|primero|segundo)\b"
azar       r"\b(azar|aleatori\w*|intuici\w*|ningun\w*|porque si)\b"
```

Una respuesta puede activar varias categorías. Texto no vacío sin coincidencia se marcará `sin_clasificar`; respuesta vacía producirá una lista vacía. Se informarán frecuencias. El texto original permanecerá restringido.

## 14. Bonificación por coordinación

La bonificación se calcula después de cerrar la muestra, con semilla docente `20260903`. Los 500 participantes completos se ordenan de manera reproducible, se emparejan sin reemplazo y se selecciona una fruta por pareja. Si ambas velocidades para esa fruta coinciden exactamente, cada miembro recibe `0,50 €`.

El proceso de bonificación es independiente de:

- la inclusión o exclusión analítica;
- los tiempos de respuesta;
- el contraste Welch y su valor `p`;
- la dirección de la respuesta;
- el pago base.

Identificadores, HMAC, parejas, respuestas comparadas, importes y estados de pago permanecen en un mapa restringido. Solo los agregados pueden salir de ese entorno. Retiradas, duplicados, fallos técnicos y un número impar se resolverán mediante las reglas congeladas en `mecanismo_bonificacion.md`; ninguna incidencia autoriza a volver a sortear después de ver coincidencias.

## 15. Datos, código y acceso

El conjunto docente tendrá 500 filas y declarará en todas:

```text
origen_dato = "sintetico_docente"
```

Los archivos públicos no contendrán `PROLIFIC_PID`, `STUDY_ID`, `SESSION_ID`, HMAC, texto abierto, timestamps exactos, parejas o pagos. La licencia CC BY 4.0 se aplicará a datos sintéticos, esquemas, metadatos y resultados publicables. El código se distribuirá por separado bajo la licencia MIT.

El generador, la limpieza y el análisis se ejecutarán por código. La semilla, versiones, hashes y entorno se conservarán. Los datos sintéticos no se presentarán como observaciones y no se utilizarán para recomendar señales reales.

## 16. Desviaciones del protocolo

El texto congelado no se sobrescribirá. Cualquier desviación se añadirá a un registro separado con:

```text
fecha y hora
persona responsable
regla original
cambio aplicado
motivo
si ocurrió antes o después de acceder a resultados
archivos y análisis afectados
```

Cuando resulte técnicamente posible, se presentará primero el análisis prerregistrado y después el análisis desviado, rotulado como no prerregistrado. Un error técnico puede detener el pipeline; no autoriza a elegir una regla que favorezca la hipótesis.

## 17. Fecha de congelación simulada

```text
Fecha: 2 de septiembre de 2026
Momento docente: T+90 minutos del seminario
Zona horaria: Europe/Madrid (CEST)
Estado: congelación simulada antes de generar la muestra sintética final
```

Esta marca temporal es parte del ejercicio. No afirma que exista una registration de OSF ni un sello externo. Durante la clase se conservará una copia local inmutable y una etiqueta Git `prereg-v1`; no se publicará ningún registro real.
