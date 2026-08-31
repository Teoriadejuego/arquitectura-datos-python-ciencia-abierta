# Diseño experimental cerrado — La velocidad de las frutas

**Versión:** 1.0 · **Fecha:** 28 de agosto de 2026  
**Uso:** simulación docente; ninguna plataforma queda publicada y ningún resultado valida una señal vial real.

## 1. Pregunta que sí puede responder el experimento

> Cuando una persona adulta con permiso de conducir encuentra por primera vez una señal ficticia sin número, ¿asigna una velocidad media mayor a una naranja que a un plátano?

El experimento mide la **saliencia de dos símbolos dentro de una tarea de coordinación**. No mide si una señal es correcta, segura, legal o universal. Tampoco evalúa la capacidad de conducir.

## 2. Población, marco muestral y elegibilidad

### Población operativa

Personas adultas con permiso de conducir vigente, capaces de leer instrucciones en español y reclutadas como voluntarias en una plataforma en línea. En una ejecución futura, el marco muestral sería Prolific; en el seminario se utilizarán exclusivamente 500 registros sintéticos.

El estimando se refiere a quienes satisfacen estos criterios y completan la tarea bajo el incentivo descrito. No se extrapola a todos los conductores, países, idiomas o entornos viales.

### Inclusión, comprobada antes de aleatorizar

1. Edad declarada de 18 años o más.
2. Permiso de conducir vigente, declarado mediante una opción sí/no. No se solicita número, fotografía, país de expedición ni categoría del permiso.
3. Capacidad declarada para comprender el texto en español.
4. Consentimiento informado.
5. Confirmación de que la persona no está conduciendo ni operando maquinaria mientras responde.
6. No haber participado antes en el mismo estudio, según el identificador pseudonimizado de la plataforma.
7. Navegador capaz de ejecutar la aplicación y registrar una respuesta explícita.

Quien no cumpla un criterio no se aleatoriza. La plataforma muestra una salida neutral y conserva únicamente el registro mínimo exigido para impedir una nueva entrada cuando resulte legítimo hacerlo.

## 3. Diseño mixto

Cada participante ve ambos símbolos una vez.

| Dimensión | Implementación |
|---|---|
| Entre sujetos | Orden asignado: `naranja_primero` o `platano_primero`. |
| Dentro del sujeto | Símbolo: naranja y plátano. |
| Asignación | 1:1, bloques permutados de 10 con cinco secuencias de cada tipo. |
| Respuesta de velocidad | Una de `30`, `50`, `70`, `90`, `110` o `130` km/h. |
| Confianza | Entero de `0` a `100`, sin valor preseleccionado. |
| Explicación | Texto abierto opcional al final. |

Los iconos serán SVG negros, centrados, con el mismo marco, fondo, resolución y área aparente. Las seis velocidades aparecen siempre en orden ascendente y ninguna está marcada de antemano. Se permite asignar la misma velocidad a las dos frutas: no existe una respuesta «correcta» ni obligación de diferenciarlas.

## 4. Flujo completo mostrado a la persona

### 4.1 Información, elegibilidad y consentimiento

La página inicial presenta este texto:

> Este estudio analiza cómo interpretamos símbolos nuevos. Verá dos señales ficticias y asignará una velocidad a cada una. La tarea dura aproximadamente cuatro minutos. No responda mientras conduce. Sus decisiones no se usarán para recomendar señales de tráfico reales. Puede abandonar antes del envío final sin penalización. La pregunta abierta es opcional y no debe contener nombres ni información personal.

Después se comprueban edad, permiso, comprensión del español, participación previa y situación de conducción. La casilla de consentimiento no viene marcada.

### 4.2 Instrucción de coordinación

Tras consentir, y antes de ver el primer símbolo:

> Imagine que conduce en un país que nunca ha visitado. En ese país, las señales de velocidad no muestran números: muestran símbolos. Cada símbolo corresponde a una velocidad máxima en kilómetros por hora, pero usted desconoce el código. Dé su mejor estimación. Cuando cierre la muestra, una de sus respuestas podrá compararse con la de otra persona. Si ambas coinciden exactamente para el mismo símbolo, cada una recibirá una bonificación de 0,50 €. El pago base no depende de coincidir.

La bonificación introduce una meta de coordinación deliberada. Por eso el estudio estima qué opción parece focal bajo ese incentivo; no una asociación puramente privada y espontánea.

### 4.3 Primera pantalla experimental

La asignación persistente decide qué símbolo aparece. Se muestra solo una fruta, centrada, y este texto:

> Ve la siguiente señal de velocidad: **[NARANJA o PLÁTANO]**. ¿Qué velocidad máxima cree que indica?

Opciones sin preselección:

```text
30 km/h · 50 km/h · 70 km/h · 90 km/h · 110 km/h · 130 km/h
```

Después, en la misma pantalla:

> ¿Qué confianza tiene en que otra persona interprete esta señal del mismo modo?

Escala entera: `0 = ninguna confianza`; `100 = confianza completa`. El envío se habilita solo después de elegir velocidad y confianza. `tiempo_primera_s` transcurre desde que el navegador confirma que el estímulo se ha renderizado hasta que el servidor acepta el formulario válido.

### 4.4 Segunda pantalla experimental

Se muestra el símbolo restante bajo esta transición:

> Unos kilómetros después, bajo las mismas condiciones de carretera y tráfico, aparece otra señal.

Se repiten la pregunta, las seis categorías y la confianza de 0 a 100. `tiempo_segunda_s` se mide con la misma regla. La primera elección permanece oculta: la aplicación no permite volver atrás ni editarla.

### 4.5 Explicación opcional

> En una frase, ¿qué le hizo asociar cada símbolo con la velocidad elegida? Esta respuesta es opcional. No incluya nombres ni información personal.

El campo admite una respuesta vacía. No interviene en la inclusión ni en el contraste confirmatorio.

### 4.6 Envío y debriefing

El servidor valida y guarda el registro una sola vez. Solo tras una escritura confirmada aparece el debriefing:

> No existía un código correcto. Estudiamos si dos símbolos arbitrarios generan respuestas focales y cómo la primera decisión condiciona la segunda. Las señales son ficticias y el estudio no evalúa seguridad vial. En el seminario, todos los datos utilizados son sintéticos.

En una ejecución con Prolific, la redirección de finalización ocurriría después de este mensaje.

## 5. Aleatorización 1:1, oculta y persistente

La secuencia contiene 50 bloques de 10 asignaciones. Cada bloque incluye cinco `naranja_primero` y cinco `platano_primero`, permutadas con la semilla docente `20260902`. La lista vive en el servidor; el navegador no conoce la siguiente asignación.

La asignación se escribe antes de renderizar el primer estímulo. Una restricción de unicidad sobre la clave pseudonimizada y `SESSION_ID` impide reasignar al recargar, abrir otra pestaña o repetir la llamada. Un abandono no libera su posición. Si una ejecución real necesitara superar 500 asignaciones por abandonos, se añadirían bloques completos de 10 y se informaría la desviación respecto de los 250 completados previstos por brazo.

### Pseudocódigo

```python
VELOCIDADES = (30, 50, 70, 90, 110, 130)
SEMILLA_ASIGNACION = 20260902
TAMANO_BLOQUE = 10

rng = Random(SEMILLA_ASIGNACION)
secuencia = []
for _ in range(50):
    bloque = ["naranja_primero"] * 5 + ["platano_primero"] * 5
    rng.shuffle(bloque)
    secuencia.extend(bloque)

def obtener_o_crear_asignacion(prolific_pid, session_id):
    clave = HMAC_SHA256(SECRETO_SERVIDOR, prolific_pid or session_id)

    with transaccion_atomica():
        existente = buscar_por_clave_o_sesion(clave, session_id)
        if existente is not None:
            return existente.orden          # nunca volver a sortear

        indice = reservar_siguiente_indice() # no se reutiliza si abandona
        orden = secuencia[indice]
        insertar_asignacion(
            clave_participante=clave,
            session_id=session_id,
            indice=indice,
            orden=orden,
        )
        return orden
```

En modo docente sin `PROLIFIC_PID`, el servidor crea un `registro_id` aleatorio y lo asocia a la sesión. La semilla permite reproducir los datos sintéticos; no se expone en el cliente durante una recogida real.

## 6. Resultado primario y estimando confirmatorio

Para cada registro válido:

```text
Y_i = velocidad_primera_kmh
A_i = 1 si simbolo_primero == "naranja"; 0 si == "platano"
```

El estimando es:

```text
Δ_primera = E[Y_i | A_i = 1] − E[Y_i | A_i = 0]
```

Interpretación: diferencia media, en km/h, entre la velocidad asignada a la naranja cuando aparece primero y la velocidad asignada al plátano cuando aparece primero, dentro de la población elegible y del conjunto analítico predefinido.

**Solo la primera decisión entra en este estimando.** La segunda velocidad, su confianza, la diferencia individual y el texto abierto no pueden actuar como resultado, predictor, covariable, estrato, criterio de éxito ni variable de sustitución del análisis primario. La única información de la segunda pantalla que interviene en la inclusión confirmatoria es su completitud y la regla temporal predeclarada.

## 7. Hipótesis y contraste confirmatorio

```text
H0: Δ_primera <= 0
H1: Δ_primera > 0
```

Se ejecutará un Welch T-Test unilateral con `α = 0,05`:

```python
from scipy.stats import ttest_ind

resultado = ttest_ind(
    grupo_naranja_primero,
    grupo_platano_primero,
    equal_var=False,
    alternative="greater",
    nan_policy="raise",
)
```

La decisión confirmatoria es `rechazar H0` si, y solo si, `p < 0,05`. No se sustituirá el test tras inspeccionar histogramas, varianzas o significación. El soporte discreto de seis valores se mostrará completo; con aproximadamente 240 observaciones válidas por brazo, el contraste de medias resulta interpretable y Welch evita imponer igualdad de varianzas.

El informe mostrará `n`, media y desviación estándar por brazo, `Δ_primera`, intervalo bilateral del 95 % de Welch, estadístico `t`, grados de libertad de Welch, valor `p` unilateral y Cohen `d` con desviación estándar combinada como tamaño descriptivo. La inferencia se apoya en `p`; el tamaño y el intervalo describen la magnitud.

## 8. Tamaño muestral y potencia

Se fija `N = 500` antes de generar o observar respuestas: 250 asignaciones previstas por secuencia. La demostración sintética incorporará 20 casos con tiempo inferior a 2,0 segundos, equilibrados por brazo, y dejará 480 registros válidos —240 por grupo—. Esas cifras se rotularán como construcción docente, no como resultado observado.

La literatura verificada no ofrece un tamaño de efecto naranja–plátano. Por eso la planificación no reutiliza el efecto limón–ciruela ni el resultado sintético. Adopta `d = 0,25` como efecto estandarizado mínimo de interés docente: una cuarta parte de una desviación estándar.

Con dos grupos de 240, asignación equilibrada, `α = 0,05` unilateral y `d = 0,25`, la potencia aproximada es `0,862`. Sin las 20 exclusiones, 250 por grupo producirían `0,874`. Con 240 por grupo, el efecto detectable con 80 % de potencia es aproximadamente `d = 0,227`.

La comprobación se reproduce así:

```python
from statsmodels.stats.power import TTestIndPower

potencia = TTestIndPower().power(
    effect_size=0.25,
    nobs1=240,
    alpha=0.05,
    ratio=1.0,
    alternative="larger",
)
```

Es una aproximación de planificación para dos medias y asignación equilibrada; no garantiza potencia bajo cualquier distribución discreta o patrón de exclusión. El tamaño no se ampliará ni se detendrá por el valor `p`. No habrá análisis intermedio.

## 9. Conjunto analítico: reglas mecánicas

Las reglas se aplican sin mirar velocidades, grupos, medias ni valores `p`.

### 9.1 Tiempo

Se excluye el registro completo si:

```text
tiempo_primera_s < 2.0 OR tiempo_segunda_s < 2.0
```

`2,00` segundos exactos permanece. No se redondea antes de comparar. La regla usa el valor numérico almacenado con precisión de milisegundos.

### 9.2 Ausencias e integridad

- Faltan `velocidad_primera_kmh`, cualquiera de las dos velocidades, cualquiera de las dos confianzas o cualquiera de los dos tiempos: registro incompleto; se excluye del conjunto confirmatorio.
- Falta `respuesta_abierta`: registro válido; el campo es opcional.
- Una velocidad no pertenece a `{30, 50, 70, 90, 110, 130}` o una confianza no es un entero de 0 a 100: error de integridad. El pipeline se detiene, se audita la causa y no se corrige manualmente el valor.
- `orden`, `simbolo_primero` y la derivación de `velocidad_primera_kmh` no concuerdan: error de integridad; el pipeline se detiene.
- No se imputan resultados ni tiempos.

La ausencia de la segunda pantalla puede depender de lo ocurrido en la primera. Se publicará el diagrama de flujo y la tasa de incompletitud por brazo. Como sensibilidad no confirmatoria se describirá la primera respuesta de todo registro aleatorizado que la haya enviado, sin reemplazar la regla principal.

### 9.3 Duplicados

La aplicación debe ser idempotente. Si aun así existen varias filas para la misma clave HMAC o `SESSION_ID`, se ordenan por la primera marca temporal del servidor y se conserva el primer intento; los posteriores se marcan `duplicado_posterior`. Si el primero está incompleto, se aplica la regla de ausencia: no se sustituye por un intento posterior más conveniente.

No se emplean IP, huella del dispositivo o geolocalización para buscar duplicados. Participaciones múltiples con identificadores distintos y no observables no se eliminan por conjetura.

### 9.4 Reglas que no existen

No se excluye por elegir extremos, repetir la misma velocidad, baja confianza, explicación breve, explicación inesperada o respuesta contraria a la hipótesis. No hay criterio de acierto.

## 10. Análisis secundarios predefinidos

Todos los análisis siguientes son secundarios o exploratorios. Se informan estimaciones e intervalos; no pueden rescatar ni invalidar el contraste confirmatorio. Los valores `p` de los siete contrastes secundarios señalados se presentarán en bruto y con ajuste Benjamini–Hochberg dentro de una única familia.

### S1. Diferencia dentro del sujeto

```python
df["diferencia_platano_menos_naranja"] = (
    df["velocidad_platano_kmh"] - df["velocidad_naranja_kmh"]
)
```

Se estima la media y el intervalo del 95 %. Se aplica `scipy.stats.ttest_rel(velocidad_platano_kmh, velocidad_naranja_kmh, alternative="two-sided")` —contraste secundario 1—. Una media negativa indica más velocidad para la naranja dentro de la persona, pero mezcla asociación, anclaje y contraste.

### S2. Asignar velocidades distintas

```text
distintas_i = 1[velocidad_naranja_kmh != velocidad_platano_kmh]
```

Se informa la proporción total con intervalo Wilson del 95 % y por orden. La asociación `distintas × orden` se contrasta con una tabla 2 × 2 sin corrección de Yates —contraste secundario 2—; si alguna frecuencia esperada es menor que 5, se usa `fisher_exact` bilateral según la regla fijada antes de mirar los datos.

### S3. Efecto del orden sobre la diferencia

Se ajusta:

```python
ols(
    "diferencia_platano_menos_naranja ~ "
    "C(orden, Treatment(reference='naranja_primero'))",
    data=df,
).fit(cov_type="HC3")
```

El coeficiente de `platano_primero` y su prueba bilateral forman el contraste secundario 3.

### S4. Regresión solicitada

```python
modelo = ols(
    "velocidad_naranja_kmh ~ velocidad_platano_kmh + "
    "C(orden, Treatment(reference='naranja_primero'))",
    data=df,
).fit(cov_type="HC3")
```

Se informan ambos coeficientes, intervalos del 95 % y `R²`. Las pruebas bilaterales de la pendiente de `velocidad_platano_kmh` y del coeficiente de orden son los contrastes secundarios 4 y 5. El modelo describe covariación; condicionar por otra respuesta postasignación impide interpretar los coeficientes como efectos causales.

### S5. Distribución completa 2 × 6

Se construye la tabla `simbolo_primero × velocidad_primera_kmh` y se ejecuta:

```python
chi2, p, gl, esperadas = scipy.stats.chi2_contingency(tabla, correction=False)
```

Se informa `χ²`, grados de libertad, `p`, residuos estandarizados y `V` de Cramér —contraste secundario 6—. Si alguna frecuencia esperada es menor que 5, el `p` asintótico se sustituye por un `p` de permutación de 100.000 reasignaciones de la etiqueta de primer símbolo, semilla `20260902`; la tabla y `V` se conservan.

### S6. Probabilidad de coordinación

Para cada fruta, con `m_j` elecciones en la categoría `j` y `N_f` respuestas:

```text
C_plugin   = Σ_j (m_j / N_f)²
C_sin_reemplazo = Σ_j m_j(m_j − 1) / [N_f(N_f − 1)]
```

Se informan ambas. La diferencia naranja–plátano recibe un intervalo percentil obtenido con 10.000 remuestreos de participantes, semilla `20260902`. No se prueba contra 1/6: las categorías no tienen probabilidades base conocidas y los puntos medios o extremos pueden ser focales sin fruta.

### S7. Confianza y coordinación efectiva

Una vez formadas las parejas de bonificación, se crea para cada participante el indicador `coincide_pareja` en la fruta seleccionada. Se ajusta una regresión logística:

```text
coincide_pareja ~ confianza_seleccionada/10 + C(simbolo_seleccionado)
```

Los errores estándar se agrupan por `pareja_id`. La prueba bilateral del coeficiente de confianza forma el contraste secundario 7. El mapa identificable de pagos permanece restringido; solo salen coeficientes y agregados.

### S8. Motivo declarado mediante Regex

El texto se pasa a minúsculas, se eliminan tildes para el emparejamiento y se clasifica de forma multietiqueta con patrones congelados:

```text
forma       = r"\b(forma|redond\w*|curv\w*|alarg\w*|punta\w*|geometri\w*|siluet\w*)\b"
color       = r"\b(color|amarill\w*|negro|negra|oscur\w*)\b"
fisica      = r"\b(peso|pesad\w*|liger\w*|rodar|rued\w*|aerodin\w*|fricci\w*)\b"
cultura     = r"\b(cultur\w*|costumbre\w*|trafic\w*|carretera\w*|deporte\w*|marca\w*)\b"
contraste   = r"\b(contraste|compar\w*|diferent\w*|primero|segundo)\b"
azar        = r"\b(azar|aleatori\w*|intuici\w*|ningun\w*|porque si)\b"
```

Una respuesta puede activar varias categorías; `sin_clasificar` identifica texto no vacío sin coincidencias. Solo se presentan frecuencias y ejemplos sintéticos revisados. No se infiere intención ni se publica texto libre sin revisión.

## 11. Riesgos de orden e interpretación

1. **Anclaje:** la primera velocidad crea una referencia numérica para la segunda.
2. **Contraste:** alguien puede elegir deliberadamente una categoría diferente en la segunda pantalla.
3. **Demanda:** ver dos frutas y leer el incentivo revela que se busca una convención.
4. **Memoria:** aunque la primera respuesta no se muestre de nuevo, permanece en la memoria.
5. **Escala fija:** el orden ascendente y seis categorías pueden producir puntos focales propios, como el centro o los extremos.
6. **Confianza intermedia:** declarar confianza tras la primera decisión puede hacer más explícita la meta de coordinación antes de la segunda.

La defensa metodológica es concreta: el análisis confirmatorio descarta por completo la segunda elección y compara solo primeras respuestas aleatorizadas. Los análisis dentro del sujeto cuantifican el proceso posterior, pero no borran esos riesgos.

## 12. Bonificación y separación analítica

Tras cerrar la muestra se formarán parejas y se seleccionará una fruta por pareja. La coincidencia exige elegir exactamente la misma de las seis velocidades para ese símbolo. Si coincide, ambas personas reciben 0,50 €; si no, ninguna recibe bonificación. El pago base cumple por sí solo la tarifa aplicable.

La bonificación:

- se calcula después del cierre;
- no altera inclusión, exclusión, pago base ni análisis confirmatorio;
- no depende de que la respuesta favorezca la hipótesis;
- no reutiliza la significación estadística;
- produce un mapa de pagos restringido, separado del conjunto público.

El algoritmo de emparejamiento y pagos se documentará en su especificación propia; este diseño solo fija su relación con la medición.

## 13. Tabla de decisiones cerradas

| Decisión | Regla congelada | Cambio permitido tras ver datos |
|---|---|---|
| Población | Adultos con permiso vigente y comprensión del español. | Ninguno. |
| Entorno | Tarea web; nunca mientras se conduce. | Ninguno. |
| Muestra | 500 registros recibidos; demostración enteramente sintética. | No ampliar por `p`. |
| Asignación | 1:1, bloques de 10, semilla `20260902`, persistente. | Solo documentar fallos técnicos. |
| Secuencias | `naranja_primero`; `platano_primero`. | Ninguna tercera secuencia. |
| Estímulos | SVG negros equivalentes en marco, fondo y área aparente. | Corrección técnica previa a recoger datos. |
| Categorías | 30, 50, 70, 90, 110, 130 km/h. | No reagrupar para el primario. |
| Confianza | Entero explícito 0–100 después de cada velocidad. | No dicotomizar para confirmar. |
| Texto | Opcional; advertencia contra información personal. | No usar para excluir. |
| Primario | `velocidad_primera_kmh`, solo primera pantalla. | No sustituir ni combinar. |
| Estimando | Media naranja primero menos media plátano primero. | Ninguno. |
| Hipótesis | `H0: Δ <= 0`; `H1: Δ > 0`. | No invertir dirección. |
| Test | Welch unilateral, `equal_var=False`, `alternative="greater"`. | No elegir por diagnóstico. |
| Alfa | 0,05. | Ninguno. |
| Tiempo | Excluir si cualquiera es `< 2.0`; `2.00` permanece. | No redondear ni recalibrar. |
| Ausencias | Requeridos ausentes: incompleto; texto abierto ausente: válido. | No imputar. |
| Duplicados | Conservar primer intento por clave/sesión; excluir posteriores. | No escoger el más completo. |
| Valores permitidos | Solo seis velocidades y confianza entera 0–100. | Error detiene el pipeline. |
| Segunda decisión | Exclusivamente secundaria. | Nunca entra en el resultado primario. |
| Secundarios | S1–S8 tal como se especifican; siete `p` con BH. | Se pueden añadir solo como no prerregistrados. |
| Bonificación | Coincidencia exacta, 0,50 € por persona, posterior al cierre. | No condicionarla a inclusión o hipótesis. |
| Parada | Sin análisis intermedio ni parada por significación. | Ninguna. |
| Desviaciones | Registrar qué cambió, cuándo, por qué y antes/después de acceder a resultados. | Nunca reescribir el protocolo original. |

## 14. Límite de la afirmación final

Un resultado positivo parecería indicar que, en esta muestra y bajo estas instrucciones, la naranja atrae una velocidad media inicial mayor que el plátano. No demostraría que ambos símbolos sean comprendidos en otros idiomas, que produzcan coordinación estable fuera de la tarea, que reduzcan errores de conducción ni que deban sustituir señales numéricas.

Paradójicamente, una coincidencia alta puede revelar un punto focal sin revelar una convención segura. Desde mi perspectiva, esa separación —saliencia no equivale a validez regulatoria— es el aprendizaje metodológico que debe sobrevivir al experimento.
