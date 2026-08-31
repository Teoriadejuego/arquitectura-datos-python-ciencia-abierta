# Mecanismo de bonificación por coordinación

**Versión:** 1.0.0-demo  
**Semilla docente congelada:** `20260903`  
**Importe:** `0,50 €` por persona cuando existe coincidencia exacta  
**Momento de ejecución:** una sola vez, después de cerrar y congelar la muestra completa

## 1. Qué remunera

La bonificación remunera una coincidencia, no una respuesta correcta. Para cada pareja se selecciona una fruta —naranja o plátano— y se comparan las categorías elegidas por sus dos miembros. Hay coincidencia si ambos asignaron exactamente la misma de estas velocidades al mismo símbolo:

```text
30 | 50 | 70 | 90 | 110 | 130 km/h
```

Si coinciden, cada persona recibe `0,50 €`. Si no coinciden, ninguna recibe bonificación. No se admite proximidad: `70` y `90` no coinciden.

La remuneración base:

- cumple por sí sola la tarifa aplicable;
- se tramita sin consultar la coincidencia;
- no disminuye por exclusión analítica, respuesta lenta, baja confianza o dirección del efecto;
- nunca se recupera ni se compensa con la bonificación.

## 2. Población de bonificación

En la simulación canónica entran los 500 participantes sintéticos que completaron ambas decisiones. Por tanto, se forman 250 parejas sin reemplazo.

En una futura ejecución real, la población se fija al cerrar la muestra y antes de emparejar:

1. una persona única por `participante_hmac`;
2. envío final aceptado por la aplicación;
3. velocidad disponible para naranja y plátano;
4. ninguna retirada válida recibida antes del cierre del mapa.

La pertenencia al conjunto analítico no aparece en esta definición. Un registro excluido porque `tiempo_primera_s < 2.0` o `tiempo_segunda_s < 2.0` continúa en la población de bonificación si completó las dos respuestas. Tampoco intervienen `incluida`, `motivo_exclusion`, el valor `p`, el signo del efecto o la confianza.

Si una incidencia técnica impide recuperar una de las dos velocidades de un envío aceptado, esa persona no puede emparejarse sin inventar una respuesta. Recibe `0,50 €` de forma garantizada y se registra `bono_tecnico_garantizado`; su pago base permanece intacto.

## 3. Entradas congeladas

Antes del cálculo se crean dos snapshots restringidos de solo lectura:

### Respuestas mínimas

```text
participante_hmac
session_hmac
velocidad_naranja_kmh
velocidad_platano_kmh
```

### Enlace de pago

```text
session_hmac
PROLIFIC_PID
estado_envio
```

El primer snapshot no contiene IDs brutos. El segundo no contiene respuestas. Ambos reciben SHA-256 y quedan enumerados en un manifiesto local junto con:

```text
semilla = 20260903
version_protocolo = 1.0.0-demo
commit_codigo
numero_personas_unicas
sha256_respuestas
sha256_enlace_pago
```

El proceso se detiene si las claves no son únicas, faltan columnas, aparecen velocidades fuera de las seis categorías o el enlace no es uno a uno.

## 4. Orden reproducible y selección de fruta

La semilla no se utiliza como contraseña. Sirve para reproducir dos operaciones mediante SHA-256:

1. ordenar participantes por una clave determinista;
2. elegir una fruta por pareja.

La clave de orden de cada persona es:

```text
SHA256("20260903|orden|" + participante_hmac)
```

Se ordena por el digest hexadecimal ascendente y, si hubiera una colisión, por `participante_hmac` ascendente. Se emparejan posiciones contiguas: `0–1`, `2–3`, …, `498–499`. Nadie aparece dos veces.

Para la pareja `k`, con los HMAC ya ordenados `a` y `b`, se calcula:

```text
bit = primer_byte(
    SHA256("20260903|fruta|" + k + "|" + a + "|" + b)
) mod 2
```

`0` selecciona naranja; `1`, plátano. Como 256 es divisible por 2, esta conversión no introduce sesgo modular. La pareja no puede elegir la fruta y el investigador no puede cambiarla después de observar respuestas.

## 5. Pseudocódigo congelado

```python
from decimal import Decimal
from hashlib import sha256

SEMILLA = "20260903"
BONO = Decimal("0.50")
VELOCIDADES = {30, 50, 70, 90, 110, 130}

def digest(texto: str) -> str:
    return sha256(texto.encode("utf-8")).hexdigest()

def clave_orden(participante_hmac: str) -> tuple[str, str]:
    return (
        digest(f"{SEMILLA}|orden|{participante_hmac}"),
        participante_hmac,
    )

def fruta_pareja(indice: int, hmac_a: str, hmac_b: str) -> str:
    material = f"{SEMILLA}|fruta|{indice}|{hmac_a}|{hmac_b}"
    primer_byte = bytes.fromhex(digest(material))[0]
    return "naranja" if primer_byte % 2 == 0 else "platano"

def construir_mapa(respuestas):
    # respuestas ya contiene una fila por persona unica y dos velocidades validas
    personas = sorted(respuestas, key=lambda r: clave_orden(r.participante_hmac))
    mapa = []

    # Contingencia: una persona impar nunca se reutiliza ni queda perjudicada.
    if len(personas) % 2 == 1:
        impar = personas.pop()
        mapa.append(fila_garantizada(impar, BONO, "n_impar_garantizado"))

    for posicion in range(0, len(personas), 2):
        a, b = personas[posicion], personas[posicion + 1]
        indice_pareja = posicion // 2 + 1
        fruta = fruta_pareja(
            indice_pareja,
            a.participante_hmac,
            b.participante_hmac,
        )
        va = getattr(a, f"velocidad_{fruta}_kmh")
        vb = getattr(b, f"velocidad_{fruta}_kmh")
        assert va in VELOCIDADES and vb in VELOCIDADES
        coincide = va == vb
        importe = BONO if coincide else Decimal("0.00")

        mapa.extend([
            fila_pago(indice_pareja, a, fruta, va, vb, coincide, importe),
            fila_pago(indice_pareja, b, fruta, vb, va, coincide, importe),
        ])

    return ordenar_salida(mapa)
```

`fila_garantizada`, `fila_pago` y `ordenar_salida` solo construyen columnas del esquema restringido siguiente; no consultan variables analíticas.

## 6. Esquema restringido del mapa de pagos

El mapa tiene una fila por persona. Vive fuera del repositorio y del kit docente.

| Variable | Tipo / valores | Función | Publicación |
|---|---|---|---|
| `run_id` | string derivado de semilla y hash de entrada | Hace idempotente la ejecución. | No. |
| `pair_id` | `PAIR-001`…`PAIR-250`; nulo en garantía individual | Identifica pareja sin identificar personas. | No. |
| `participant_hmac` | 64 caracteres hexadecimales | Une respuesta con sesión restringida. | No. |
| `session_hmac` | 64 caracteres hexadecimales | Enlace local con exportación Prolific. | No. |
| `simbolo_bonificacion` | `naranja`; `platano`; nulo si garantía | Fruta sorteada para la pareja. | No. |
| `velocidad_propia_kmh` | seis categorías; nulo si incidencia técnica | Respuesta evaluada. | No. |
| `velocidad_pareja_kmh` | seis categorías; nulo si garantía | Comparación exacta. | No. |
| `confianza_seleccionada` | entero entre 0 y 100 | Confianza declarada para la fruta sorteada; se usa solo en el análisis secundario restringido. | No. |
| `coincide_pareja` | boolean; nulo si garantía | Resultado lógico. | No. |
| `importe_bonificacion_eur` | `0.00` o `0.50` | Cantidad que se tramita. | No. |
| `motivo_pago` | `coincidencia`; `sin_coincidencia`; `n_impar_garantizado`; `bono_tecnico_garantizado`; `retirada_garantizada` | Explica la regla aplicada. | No. |
| `estado_pago` | `pendiente`; `enviado`; `error`; `no_corresponde` | Conciliación contable. | No. |

El archivo de carga a la plataforma se genera después mediante un enlace local y contiene solo `PROLIFIC_PID` e importe. No incluye respuestas, pareja, fruta, velocidades, HMAC o variables analíticas.

## 7. Enlace local con la exportación de Prolific

El enlace ocurre en un equipo autorizado, sin subir archivos a servicios intermedios:

1. Cerrar la recogida y exportar las submissions de Prolific a una carpeta restringida.
2. Verificar que la exportación corresponde al `STUDY_ID` previsto y congelar su SHA-256.
3. Leer el identificador de envío de la exportación y el `SESSION_ID` capturado por la aplicación.
4. Normalizar ambos sin alterar mayúsculas/minúsculas y generar `session_hmac` con el mismo secreto, prefijo de dominio y versión.
5. Ejecutar una unión uno a uno con validación equivalente a `merge(..., validate="one_to_one")`.
6. Detenerse ante duplicados o filas no enlazadas. Las únicas ausencias permitidas son retiradas o incidencias documentadas en el manifiesto.
7. Unir temporalmente el importe con `PROLIFIC_PID` dentro del entorno restringido.
8. Exportar el fichero mínimo de pago; revisar suma, número de personas y valores permitidos.
9. Tramitar los importes y actualizar `estado_pago` en el mapa restringido.
10. Destruir la copia de trabajo que combina identidad y respuesta cuando termina la conciliación; conservar solo lo exigido por el DMP y las obligaciones contables.

`PROLIFIC_PID` nunca entra en Python analítico, Git, GitHub, OSF, el ZIP del alumno o Zenodo.

## 8. Contingencias cerradas

### Retirada

- **Antes del emparejamiento:** la respuesta se elimina de la población. Para que retirar datos no reduzca la compensación prometida, se asigna `0,50 €` con `retirada_garantizada`, si todavía existe el identificador mínimo necesario para pagar.
- **Después del emparejamiento y antes del pago:** se retiran sus datos de investigación; se conserva solo el mínimo contable. Su importe se respeta y el de la pareja no se revoca.
- **Después del pago:** no se recupera dinero. Se atiende la retirada de los datos conservados conforme al DMP.

Tras una retirada previa, el emparejamiento se recalcula desde el snapshot definitivo. No se parchea una pareja a mano.

### Duplicado

- Dos filas con el mismo `SESSION_ID` representan la misma submission: se colapsan de forma idempotente.
- Varias sesiones con el mismo `participante_hmac`: se conserva el primer intento aceptado según la marca del servidor. La persona obtiene una sola oportunidad de bonificación.
- Un duplicado técnico no reduce el pago base. Si el registro canónico carece de una respuesta por fallo de la aplicación, se aplica `bono_tecnico_garantizado`.
- No se buscan duplicados mediante IP, geolocalización o huella de dispositivo.

### Número impar

Si, después de retiradas e incidencias, quedan `N` personas impares, la última de la ordenación reproducible no se empareja ni se reutiliza. Recibe `0,50 €` con `n_impar_garantizado`. Las otras `N−1` personas forman parejas sin reemplazo.

### Error de pago

Un error de plataforma cambia `estado_pago` a `error`, no el importe calculado. Se reintenta la misma orden; nunca se vuelve a sortear pareja o fruta.

## 9. Seguridad HMAC

`participante_hmac` y `session_hmac` son seudónimos, no anonimización. Se aplican estas reglas:

- HMAC-SHA-256 con secreto aleatorio externo al repositorio;
- prefijos distintos para participante y sesión, evitando enlaces entre dominios;
- secreto y tabla de enlace almacenados por separado;
- cifrado en tránsito y reposo;
- acceso nominal y registro de aperturas;
- ninguna salida de consola muestra IDs o HMAC completos;
- rotación documentada mediante `hmac_version`;
- comparación y unión solo dentro del entorno restringido.

La semilla `20260903` puede ser pública. Sin los HMAC restringidos no permite reconstruir parejas.

## 10. Auditoría antes de pagar

El proceso debe superar estos controles:

1. El snapshot de entrada está cerrado y su SHA-256 coincide con el manifiesto.
2. Cada `participante_hmac` y `session_hmac` aparece una sola vez.
3. Ninguna pareja contiene dos veces a la misma persona.
4. En `N=500`, hay exactamente 250 `pair_id` y dos filas por pareja.
5. Cada pareja comparte una sola fruta y un solo resultado de coincidencia.
6. Las dos velocidades comparadas pertenecen al conjunto permitido.
7. `coincide_pareja` equivale exactamente a igualdad de enteros.
8. El importe es `0.50` si coincide y `0.00` si no; las garantías están justificadas por su motivo.
9. Ninguna columna analítica —incluida `incluida`, `motivo_exclusion` o `p`— entra en el cálculo.
10. La suma del mapa coincide con la suma del archivo de carga.
11. Ejecutar dos veces con idénticas entradas produce el mismo `run_id`, parejas, frutas e importes.
12. El mapa y el archivo de carga no aparecen en Git, ZIP público o Zenodo.

Después se genera un acta sin identificadores con: versión de código, hashes, semilla, número de parejas, coincidencias, personas bonificadas, importe total, garantías y errores de pago.

## 11. Resultado sintético de referencia

Para los 500 registros sintéticos congelados del curso, el resultado esperado es:

```text
participantes simulados       500
parejas simuladas             250
parejas que coinciden          83
personas con bonificación     166
importe por persona          0,50 €
importe total simulado       83,00 €
```

Comprobación aritmética:

```text
83 parejas × 2 personas = 166 bonificaciones
166 × 0,50 € = 83,00 €
```

Estas cifras son una **simulación docente programada**. No describen pagos reales, comportamiento observado ni una tasa de coordinación universal.

## 12. Comunicación al participante

### Antes de responder

> Su pago base no depende de sus elecciones. Cuando cierre la muestra, una de las dos frutas se seleccionará para su pareja. Si usted y otra persona eligieron exactamente la misma velocidad para esa fruta, cada uno recibirá 0,50 € adicionales. La exclusión de un análisis estadístico no elimina esta oportunidad.

### Si hay coincidencia

> La fruta seleccionada para su pareja fue **[fruta]**. Ambas personas eligieron **[velocidad] km/h**. Se ha tramitado una bonificación de **0,50 €**.

### Si no hay coincidencia

> La fruta seleccionada para su pareja fue **[fruta]**. Las categorías no coincidieron exactamente, por lo que no corresponde bonificación. Su pago base no cambia.

### Si se aplica una garantía

> Una incidencia técnica o de emparejamiento impidió aplicar la comparación prevista. Para que no resulte perjudicado, se ha tramitado la bonificación completa de **0,50 €**. Su respuesta no se modificó.

Nunca se comunica la identidad de la pareja. Tampoco se comparte su respuesta cuando no existe coincidencia.
