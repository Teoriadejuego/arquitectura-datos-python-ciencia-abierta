#!/usr/bin/env python3
"""Genera el conjunto bruto sintético y su resumen reproducible (Prompt 12).

Los datos están construidos exclusivamente para docencia. No representan
participantes, respuestas ni tiempos observados.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import random
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import fmean
from typing import Any, Iterable, Sequence


SEMILLA = 20260902
VELOCIDADES = (30, 50, 70, 90, 110, 130)
ORIGEN_DATO = "sintetico_docente"
VERSION_APP = "1.0.0-demo"

ORDEN_NARANJA = "naranja_primero"
ORDEN_PLATANO = "platano_primero"
ORDENES = (ORDEN_NARANJA, ORDEN_PLATANO)

N_TOTAL = 500
N_POR_ORDEN = 250
N_SPEEDERS_POR_ORDEN = 10
N_VALIDOS_POR_ORDEN = 240

RECUENTOS_PRIMERA_ESPERADOS = {
    ORDEN_NARANJA: (0, 6, 52, 131, 47, 4),
    ORDEN_PLATANO: (5, 73, 102, 53, 7, 0),
}

# Filas = velocidad de naranja; columnas = velocidad de plátano.
# Estas tablas conjuntas fijan las marginales y una asociación imperfecta.
TABLA_VALIDA_NARANJA_PRIMERO = (
    (0, 0, 0, 0, 0, 0),
    (0, 6, 0, 0, 0, 0),
    (9, 29, 14, 0, 0, 0),
    (2, 45, 65, 19, 0, 0),
    (0, 2, 22, 22, 0, 1),
    (0, 0, 2, 2, 0, 0),
)

TABLA_VALIDA_PLATANO_PRIMERO = (
    (0, 1, 0, 0, 0, 0),
    (0, 1, 1, 0, 0, 0),
    (4, 18, 8, 2, 0, 0),
    (1, 44, 54, 19, 0, 0),
    (0, 9, 39, 31, 7, 0),
    (0, 0, 0, 1, 0, 0),
)

PARES_SPEEDER = {
    ORDEN_NARANJA: (
        (70, 50),
        (90, 70),
        (110, 90),
        (90, 50),
        (70, 70),
        (110, 70),
        (90, 90),
        (130, 110),
        (50, 30),
        (90, 70),
    ),
    ORDEN_PLATANO: (
        (90, 70),
        (110, 50),
        (70, 70),
        (90, 90),
        (110, 70),
        (70, 50),
        (130, 90),
        (90, 70),
        (50, 30),
        (110, 50),
    ),
}

EXPLICACIONES = (
    "La forma redonda me sugirió una velocidad estable y la silueta alargada una menor.",
    "Me guié por la forma y por el contraste entre ambos símbolos.",
    "La naranja parecía compacta y el plátano más ligero; fue una asociación intuitiva.",
    "Elegí categorías centrales porque imaginé una convención fácil de coordinar.",
    "Pensé en cómo se verían las siluetas desde lejos y comparé sus formas.",
    "La curva de un símbolo y la geometría del otro orientaron mi elección.",
    "Usé una intuición visual y mantuve una diferencia moderada entre las señales.",
    "La silueta redonda me pareció más focal; para la otra escogí una categoría cercana.",
    "Comparé peso aparente y forma, sin asumir que existiera una respuesta correcta.",
    "Fue una elección por contraste visual entre una figura compacta y otra alargada.",
    "Intenté escoger opciones que otra persona pudiera considerar puntos focales.",
    "Me basé en la geometría de las señales y en una asociación espontánea.",
)

COLUMNAS_RAW = (
    "PROLIFIC_PID",
    "STUDY_ID",
    "SESSION_ID",
    "modo",
    "registro_id",
    "indice_asignacion",
    "consentimiento",
    "edad_18_mas",
    "permiso_vigente",
    "comprende_espanol",
    "no_conduce_ahora",
    "orden",
    "simbolo_primero",
    "velocidad_primera_kmh",
    "velocidad_naranja_kmh",
    "velocidad_platano_kmh",
    "confianza_naranja",
    "confianza_platano",
    "tiempo_primera_s",
    "tiempo_segunda_s",
    "respuesta_abierta",
    "inicio_utc",
    "primera_render_utc",
    "segunda_render_utc",
    "fin_utc",
    "origen_dato",
    "version_app",
)


def exigir(condicion: bool, mensaje: str) -> None:
    """Detiene la generación si se viola una invariante."""

    if not condicion:
        raise ValueError(f"QA fallido: {mensaje}")


def expandir_tabla(tabla: Sequence[Sequence[int]]) -> list[tuple[int, int]]:
    """Convierte una tabla conjunta 6 x 6 en pares (naranja, plátano)."""

    exigir(len(tabla) == len(VELOCIDADES), "la tabla conjunta debe tener seis filas")
    pares: list[tuple[int, int]] = []
    for i, fila in enumerate(tabla):
        exigir(len(fila) == len(VELOCIDADES), "la tabla conjunta debe ser 6 x 6")
        for j, recuento in enumerate(fila):
            exigir(isinstance(recuento, int) and recuento >= 0, "recuento conjunto inválido")
            pares.extend([(VELOCIDADES[i], VELOCIDADES[j])] * recuento)
    exigir(len(pares) == N_VALIDOS_POR_ORDEN, "cada tabla debe sumar 240 casos")
    return pares


def secuencia_bloqueada(rng: random.Random) -> list[str]:
    """Construye 50 bloques de diez con asignación 5/5."""

    secuencia: list[str] = []
    for _ in range(N_TOTAL // 10):
        bloque = [ORDEN_NARANJA] * 5 + [ORDEN_PLATANO] * 5
        rng.shuffle(bloque)
        secuencia.extend(bloque)
    return secuencia


def iso_milisegundos(valor: datetime) -> str:
    return valor.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def confianza_sintetica(
    fruta: str,
    velocidad: int,
    rng: random.Random,
) -> int:
    """Genera una confianza entera plausible sin usar información personal."""

    velocidad_focal = 90 if fruta == "naranja" else 70
    distancia = abs(velocidad - velocidad_focal) // 20
    centro = 72 - 3 * distancia
    return max(0, min(100, int(round(rng.gauss(centro, 12)))))


def tiempos_sinteticos(
    rng: random.Random,
    es_speeder: bool,
    indice_speeder: int,
    indice_valido: int,
) -> tuple[float, float]:
    """Crea tiempos en segundos; 2.000 pertenece al conjunto válido."""

    if es_speeder:
        rapido = round(1.050 + 0.073 * indice_speeder, 3)
        normal = max(2.0, round(rng.lognormvariate(math.log(7.0), 0.32), 3))
        return (rapido, normal) if indice_speeder % 2 == 0 else (normal, rapido)

    primera = max(2.0, round(rng.lognormvariate(math.log(7.2), 0.38), 3))
    segunda = max(2.0, round(rng.lognormvariate(math.log(6.8), 0.38), 3))
    if indice_valido == 0:
        primera = 2.000
    elif indice_valido == 1:
        segunda = 2.000
    return primera, segunda


def construir_filas() -> list[dict[str, Any]]:
    rng = random.Random(SEMILLA)
    secuencia = secuencia_bloqueada(rng)

    pares_validos = {
        ORDEN_NARANJA: expandir_tabla(TABLA_VALIDA_NARANJA_PRIMERO),
        ORDEN_PLATANO: expandir_tabla(TABLA_VALIDA_PLATANO_PRIMERO),
    }
    for pares in pares_validos.values():
        rng.shuffle(pares)

    posiciones_speeder = {
        orden: set(rng.sample(range(N_POR_ORDEN), N_SPEEDERS_POR_ORDEN))
        for orden in ORDENES
    }
    contador_orden = Counter()
    contador_validos = Counter()
    contador_speeders = Counter()
    filas: list[dict[str, Any]] = []
    base_temporal = datetime(2026, 9, 2, 8, 0, tzinfo=timezone.utc)

    for indice, orden in enumerate(secuencia):
        posicion_orden = contador_orden[orden]
        contador_orden[orden] += 1
        es_speeder = posicion_orden in posiciones_speeder[orden]

        if es_speeder:
            indice_speeder = contador_speeders[orden]
            naranja, platano = PARES_SPEEDER[orden][indice_speeder]
            contador_speeders[orden] += 1
            indice_valido = -1
        else:
            indice_valido = contador_validos[orden]
            naranja, platano = pares_validos[orden][indice_valido]
            contador_validos[orden] += 1
            indice_speeder = -1

        tiempo_primera, tiempo_segunda = tiempos_sinteticos(
            rng,
            es_speeder,
            indice_speeder,
            indice_valido,
        )
        simbolo_primero = "naranja" if orden == ORDEN_NARANJA else "platano"
        velocidad_primera = naranja if simbolo_primero == "naranja" else platano

        inicio = base_temporal + timedelta(minutes=7 * indice)
        primera_render = inicio + timedelta(seconds=12)
        segunda_render = primera_render + timedelta(seconds=tiempo_primera + 1.25)
        fin = segunda_render + timedelta(seconds=tiempo_segunda + 6.5)

        fila: dict[str, Any] = {
            "PROLIFIC_PID": None,
            "STUDY_ID": None,
            "SESSION_ID": None,
            "modo": "docente",
            "registro_id": f"SIM-{indice + 1:06d}",
            "indice_asignacion": indice,
            "consentimiento": True,
            "edad_18_mas": True,
            "permiso_vigente": True,
            "comprende_espanol": True,
            "no_conduce_ahora": True,
            "orden": orden,
            "simbolo_primero": simbolo_primero,
            "velocidad_primera_kmh": velocidad_primera,
            "velocidad_naranja_kmh": naranja,
            "velocidad_platano_kmh": platano,
            "confianza_naranja": confianza_sintetica("naranja", naranja, rng),
            "confianza_platano": confianza_sintetica("platano", platano, rng),
            "tiempo_primera_s": tiempo_primera,
            "tiempo_segunda_s": tiempo_segunda,
            "respuesta_abierta": rng.choice(EXPLICACIONES),
            "inicio_utc": iso_milisegundos(inicio),
            "primera_render_utc": iso_milisegundos(primera_render),
            "segunda_render_utc": iso_milisegundos(segunda_render),
            "fin_utc": iso_milisegundos(fin),
            "origen_dato": ORIGEN_DATO,
            "version_app": VERSION_APP,
        }
        filas.append(fila)

    exigir(contador_validos == Counter({orden: 240 for orden in ORDENES}), "consumo de pares válidos")
    exigir(contador_speeders == Counter({orden: 10 for orden in ORDENES}), "consumo de speeders")
    return filas


def varianza_muestral(valores: Sequence[float]) -> float:
    exigir(len(valores) > 1, "se requieren al menos dos valores")
    media = fmean(valores)
    return sum((x - media) ** 2 for x in valores) / (len(valores) - 1)


def beta_continua(a: float, b: float, x: float) -> float:
    """Fracción continua de Lentz para la beta incompleta regularizada."""

    max_iter = 10_000
    epsilon = 3e-14
    minimo = 1e-300
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    d = minimo if abs(d) < minimo else d
    d = 1.0 / d
    h = d

    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = minimo if abs(d) < minimo else d
        c = 1.0 + aa / c
        c = minimo if abs(c) < minimo else c
        d = 1.0 / d
        h *= d * c

        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = minimo if abs(d) < minimo else d
        c = 1.0 + aa / c
        c = minimo if abs(c) < minimo else c
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < epsilon:
            return h
    raise ArithmeticError("la beta incompleta no convergió")


def beta_regularizada(a: float, b: float, x: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    factor = math.exp(
        math.lgamma(a + b)
        - math.lgamma(a)
        - math.lgamma(b)
        + a * math.log(x)
        + b * math.log1p(-x)
    )
    if x < (a + 1.0) / (a + b + 2.0):
        return factor * beta_continua(a, b, x) / a
    return 1.0 - factor * beta_continua(b, a, 1.0 - x) / b


def supervivencia_t_positiva(t: float, grados_libertad: float) -> float:
    exigir(t >= 0.0 and grados_libertad > 0.0, "parámetros inválidos para Student t")
    x = grados_libertad / (grados_libertad + t * t)
    return 0.5 * beta_regularizada(grados_libertad / 2.0, 0.5, x)


def recuentos(valores: Iterable[int]) -> dict[str, int]:
    contador = Counter(valores)
    return {str(v): contador[v] for v in VELOCIDADES}


def pearson(x: Sequence[float], y: Sequence[float]) -> float:
    exigir(len(x) == len(y) and len(x) > 1, "vectores incompatibles para correlación")
    media_x = fmean(x)
    media_y = fmean(y)
    sxx = sum((valor - media_x) ** 2 for valor in x)
    syy = sum((valor - media_y) ** 2 for valor in y)
    sxy = sum((a - media_x) * (b - media_y) for a, b in zip(x, y))
    return sxy / math.sqrt(sxx * syy)


def ols_naranja_sobre_platano_y_orden(filas: Sequence[dict[str, Any]]) -> dict[str, float]:
    por_grupo = {
        orden: [fila for fila in filas if fila["orden"] == orden]
        for orden in ORDENES
    }
    medias = {}
    for orden, grupo in por_grupo.items():
        medias[orden] = {
            "naranja": fmean(fila["velocidad_naranja_kmh"] for fila in grupo),
            "platano": fmean(fila["velocidad_platano_kmh"] for fila in grupo),
        }

    numerador = 0.0
    denominador = 0.0
    for orden, grupo in por_grupo.items():
        media_n = medias[orden]["naranja"]
        media_p = medias[orden]["platano"]
        for fila in grupo:
            p_centrada = fila["velocidad_platano_kmh"] - media_p
            numerador += p_centrada * (fila["velocidad_naranja_kmh"] - media_n)
            denominador += p_centrada * p_centrada

    pendiente = numerador / denominador
    efecto_orden = (
        medias[ORDEN_PLATANO]["naranja"]
        - medias[ORDEN_NARANJA]["naranja"]
        - pendiente
        * (
            medias[ORDEN_PLATANO]["platano"]
            - medias[ORDEN_NARANJA]["platano"]
        )
    )
    intercepto = (
        medias[ORDEN_NARANJA]["naranja"]
        - pendiente * medias[ORDEN_NARANJA]["platano"]
    )

    observados = [fila["velocidad_naranja_kmh"] for fila in filas]
    media_observada = fmean(observados)
    sst = sum((valor - media_observada) ** 2 for valor in observados)
    sse = 0.0
    for fila in filas:
        orden_binario = int(fila["orden"] == ORDEN_PLATANO)
        prediccion = (
            intercepto
            + pendiente * fila["velocidad_platano_kmh"]
            + efecto_orden * orden_binario
        )
        sse += (fila["velocidad_naranja_kmh"] - prediccion) ** 2

    return {
        "intercepto": intercepto,
        "pendiente_platano": pendiente,
        "coeficiente_orden_platano_primero": efecto_orden,
        "r_cuadrado": 1.0 - sse / sst,
    }


def coordinacion_plugin(valores: Sequence[int]) -> float:
    contador = Counter(valores)
    n = len(valores)
    return sum((contador[v] / n) ** 2 for v in VELOCIDADES)


def coordinacion_sin_reemplazo(valores: Sequence[int]) -> float:
    contador = Counter(valores)
    n = len(valores)
    return sum(contador[v] * (contador[v] - 1) for v in VELOCIDADES) / (n * (n - 1))


def calcular_metricas(filas_validas: Sequence[dict[str, Any]]) -> dict[str, Any]:
    primera_naranja = [
        fila["velocidad_primera_kmh"]
        for fila in filas_validas
        if fila["orden"] == ORDEN_NARANJA
    ]
    primera_platano = [
        fila["velocidad_primera_kmh"]
        for fila in filas_validas
        if fila["orden"] == ORDEN_PLATANO
    ]
    naranja = [fila["velocidad_naranja_kmh"] for fila in filas_validas]
    platano = [fila["velocidad_platano_kmh"] for fila in filas_validas]

    n1 = len(primera_naranja)
    n2 = len(primera_platano)
    media1 = fmean(primera_naranja)
    media2 = fmean(primera_platano)
    var1 = varianza_muestral(primera_naranja)
    var2 = varianza_muestral(primera_platano)
    error2 = var1 / n1 + var2 / n2
    t_welch = (media1 - media2) / math.sqrt(error2)
    gl_welch = error2**2 / (
        (var1 / n1) ** 2 / (n1 - 1) + (var2 / n2) ** 2 / (n2 - 1)
    )
    p_unilateral = supervivencia_t_positiva(t_welch, gl_welch)
    desviacion_agrupada = math.sqrt(
        ((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)
    )
    d_cohen = (media1 - media2) / desviacion_agrupada
    correccion_hedges = 1.0 - 3.0 / (4.0 * (n1 + n2) - 9.0)

    tabla_primera = [
        [Counter(primera_naranja)[v] for v in VELOCIDADES],
        [Counter(primera_platano)[v] for v in VELOCIDADES],
    ]
    chi2 = 0.0
    for columna in range(len(VELOCIDADES)):
        total_columna = tabla_primera[0][columna] + tabla_primera[1][columna]
        esperado = total_columna / 2.0
        exigir(esperado > 0.0, "frecuencia esperada nula en chi-cuadrado")
        chi2 += sum(
            (tabla_primera[fila][columna] - esperado) ** 2 / esperado
            for fila in (0, 1)
        )

    media_naranja = fmean(naranja)
    media_platano = fmean(platano)
    solapamiento_primera = sum(
        min(tabla_primera[0][i], tabla_primera[1][i])
        for i in range(len(VELOCIDADES))
    ) / n1

    return {
        "primario": {
            "n_naranja_primero": n1,
            "n_platano_primero": n2,
            "media_naranja_primero": media1,
            "media_platano_primero": media2,
            "delta_naranja_menos_platano": media1 - media2,
            "sd_naranja_primero": math.sqrt(var1),
            "sd_platano_primero": math.sqrt(var2),
            "welch_t": t_welch,
            "welch_gl": gl_welch,
            "welch_p_unilateral": p_unilateral,
            "cohen_d": d_cohen,
            "hedges_g": d_cohen * correccion_hedges,
        },
        "secundario": {
            "media_global_naranja": media_naranja,
            "media_global_platano": media_platano,
            "media_delta_platano_menos_naranja": media_platano - media_naranja,
            "correlacion_pearson_naranja_platano": pearson(naranja, platano),
            "ols": ols_naranja_sobre_platano_y_orden(filas_validas),
            "chi2_primera_2x6": chi2,
            "chi2_gl": 5,
            "coordinacion": {
                "naranja_plugin": coordinacion_plugin(naranja),
                "naranja_sin_reemplazo": coordinacion_sin_reemplazo(naranja),
                "platano_plugin": coordinacion_plugin(platano),
                "platano_sin_reemplazo": coordinacion_sin_reemplazo(platano),
            },
            "coeficiente_solapamiento_primera": solapamiento_primera,
        },
        "distribuciones": {
            "primera_naranja_primero": recuentos(primera_naranja),
            "primera_platano_primero": recuentos(primera_platano),
            "global_naranja": recuentos(naranja),
            "global_platano": recuentos(platano),
        },
    }


def validar_y_resumir(filas: Sequence[dict[str, Any]]) -> dict[str, Any]:
    exigir(len(filas) == N_TOTAL, "deben existir exactamente 500 filas")
    exigir(all(tuple(fila) == COLUMNAS_RAW for fila in filas), "columnas raw no canónicas")
    exigir(len({fila["registro_id"] for fila in filas}) == N_TOTAL, "registro_id duplicado")
    exigir(
        Counter(fila["orden"] for fila in filas)
        == Counter({orden: N_POR_ORDEN for orden in ORDENES}),
        "la asignación debe ser 250/250",
    )

    for inicio in range(0, N_TOTAL, 10):
        bloque = Counter(fila["orden"] for fila in filas[inicio : inicio + 10])
        exigir(bloque == Counter({orden: 5 for orden in ORDENES}), "bloque no equilibrado 5/5")

    patrones_pii = (
        re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
        re.compile(r"https?://|www\.", re.IGNORECASE),
        re.compile(r"(?<!\d)(?:\+?\d[\s().-]?){7,}\d(?!\d)"),
    )
    for fila in filas:
        exigir(fila["origen_dato"] == ORIGEN_DATO, "origen de dato incorrecto")
        exigir(fila["modo"] == "docente", "modo distinto de docente")
        exigir(all(fila[campo] is None for campo in ("PROLIFIC_PID", "STUDY_ID", "SESSION_ID")), "ID de plataforma presente")
        exigir(fila["orden"] in ORDENES, "orden inválido")
        exigir(fila["simbolo_primero"] in ("naranja", "platano"), "símbolo inválido")
        velocidades_fila = (
            fila["velocidad_primera_kmh"],
            fila["velocidad_naranja_kmh"],
            fila["velocidad_platano_kmh"],
        )
        exigir(all(v in VELOCIDADES for v in velocidades_fila), "velocidad fuera del soporte")
        primera_esperada = (
            fila["velocidad_naranja_kmh"]
            if fila["orden"] == ORDEN_NARANJA
            else fila["velocidad_platano_kmh"]
        )
        exigir(fila["velocidad_primera_kmh"] == primera_esperada, "primera respuesta incoherente")
        for campo in ("confianza_naranja", "confianza_platano"):
            valor = fila[campo]
            exigir(isinstance(valor, int) and 0 <= valor <= 100, "confianza fuera de 0-100")
        for campo in ("tiempo_primera_s", "tiempo_segunda_s"):
            valor = fila[campo]
            exigir(isinstance(valor, float) and math.isfinite(valor) and valor >= 0.0, "tiempo inválido")
        texto = fila["respuesta_abierta"]
        exigir(isinstance(texto, str) and texto.strip(), "explicación sintética vacía")
        exigir(not any(patron.search(texto) for patron in patrones_pii), "posible PII en explicación")

    es_speeder = lambda fila: (
        fila["tiempo_primera_s"] < 2.0 or fila["tiempo_segunda_s"] < 2.0
    )
    speeders = [fila for fila in filas if es_speeder(fila)]
    validas = [fila for fila in filas if not es_speeder(fila)]
    exigir(len(speeders) == 20, "deben existir exactamente veinte speeders")
    exigir(len(validas) == 480, "deben quedar exactamente 480 casos válidos")
    exigir(
        Counter(fila["orden"] for fila in speeders)
        == Counter({orden: 10 for orden in ORDENES}),
        "los speeders deben quedar equilibrados 10/10",
    )
    exigir(
        Counter(fila["orden"] for fila in validas)
        == Counter({orden: 240 for orden in ORDENES}),
        "los casos válidos deben quedar equilibrados 240/240",
    )
    exigir(any(fila["tiempo_primera_s"] == 2.0 for fila in validas), "falta caso frontera 2.000")
    exigir(any(fila["tiempo_segunda_s"] == 2.0 for fila in validas), "falta caso frontera 2.000")

    metricas = calcular_metricas(validas)
    distribuciones = metricas["distribuciones"]
    for orden, esperados in RECUENTOS_PRIMERA_ESPERADOS.items():
        clave = f"primera_{orden}"
        observados = tuple(distribuciones[clave][str(v)] for v in VELOCIDADES)
        exigir(observados == esperados, f"recuentos de primera respuesta en {orden}")

    primario = metricas["primario"]
    secundario = metricas["secundario"]
    ols = secundario["ols"]
    coordinacion = secundario["coordinacion"]
    exigir(abs(primario["media_naranja_primero"] - 89.25) < 1e-12, "media naranja primero")
    exigir(abs(primario["media_platano_primero"] - 68.6666666667) < 1e-9, "media plátano primero")
    exigir(abs(primario["welch_t"] - 13.9635) < 1e-4, "Welch t de referencia")
    exigir(abs(primario["welch_p_unilateral"] / 1.216e-37 - 1.0) < 0.001, "p de Welch")
    exigir(abs(primario["cohen_d"] - 1.2747) < 1e-4, "d de Cohen")
    exigir(abs(secundario["media_global_naranja"] - 91.6666666667) < 1e-9, "media global naranja")
    exigir(abs(secundario["media_global_platano"] - 66.9166666667) < 1e-9, "media global plátano")
    exigir(abs(secundario["media_delta_platano_menos_naranja"] + 24.75) < 1e-12, "delta global")
    exigir(abs(secundario["correlacion_pearson_naranja_platano"] - 0.5202) < 5e-4, "correlación")
    exigir(abs(ols["pendiente_platano"] - 0.4576) < 5e-4, "pendiente OLS")
    exigir(abs(ols["coeficiente_orden_platano_primero"] - 3.2317) < 0.002, "efecto de orden OLS")
    exigir(abs(ols["r_cuadrado"] - 0.2819) < 5e-4, "R cuadrado OLS")
    exigir(abs(secundario["chi2_primera_2x6"] - 144.75) < 0.01, "chi-cuadrado")
    exigir(abs(coordinacion["naranja_plugin"] - 0.377) < 5e-4, "coordinación naranja")
    exigir(abs(coordinacion["platano_plugin"] - 0.328) < 5e-4, "coordinación plátano")
    exigir(secundario["coeficiente_solapamiento_primera"] > 0.45, "falta solapamiento")

    return {
        "estado": "OK",
        "semilla": SEMILLA,
        "filas_totales": len(filas),
        "orden": dict(sorted(Counter(fila["orden"] for fila in filas).items())),
        "speeders": {
            "total": len(speeders),
            "por_orden": dict(sorted(Counter(fila["orden"] for fila in speeders).items())),
            "regla": "tiempo_primera_s < 2.0 o tiempo_segunda_s < 2.0",
        },
        "validos": {
            "total": len(validas),
            "por_orden": dict(sorted(Counter(fila["orden"] for fila in validas).items())),
        },
        "soporte_velocidades_kmh": list(VELOCIDADES),
        "confianza_rango": [0, 100],
        "explicaciones": {
            "tipo": "frases sintéticas predefinidas; no observadas",
            "sin_pii_detectada": True,
            "textos_unicos_utilizados": len({fila["respuesta_abierta"] for fila in filas}),
        },
        "metricas": metricas,
    }


def serializar_csv(filas: Sequence[dict[str, Any]]) -> bytes:
    buffer = io.StringIO(newline="")
    escritor = csv.DictWriter(
        buffer,
        fieldnames=COLUMNAS_RAW,
        extrasaction="raise",
        lineterminator="\n",
    )
    escritor.writeheader()
    escritor.writerows(filas)
    return buffer.getvalue().encode("utf-8")


def main() -> None:
    raiz = Path(__file__).resolve().parents[2]
    directorio_salida = raiz / "04_DATOS" / "sinteticos_raw"
    ruta_csv = directorio_salida / "respuestas_sinteticas_500.csv"
    ruta_json = directorio_salida / "resumen_generacion.json"

    filas = construir_filas()
    resumen_qa = validar_y_resumir(filas)
    contenido_csv = serializar_csv(filas)
    hash_csv = hashlib.sha256(contenido_csv).hexdigest()

    resumen = {
        "tipo": "resumen_generacion_datos_sinteticos",
        "advertencia": (
            "Simulación docente generada por código; no contiene participantes "
            "ni respuestas observadas y no valida señales viales reales."
        ),
        "origen_dato": ORIGEN_DATO,
        "version_app": VERSION_APP,
        "archivo_csv": ruta_csv.relative_to(raiz).as_posix(),
        "sha256_csv": hash_csv,
        "qa": resumen_qa,
    }

    directorio_salida.mkdir(parents=True, exist_ok=True)
    ruta_csv.write_bytes(contenido_csv)
    ruta_json.write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    metricas = resumen_qa["metricas"]
    print(f"CSV: {ruta_csv}")
    print(f"Resumen: {ruta_json}")
    print(f"SHA-256 CSV: {hash_csv}")
    print(
        "QA: OK | "
        f"n={resumen_qa['filas_totales']} | "
        f"válidos={resumen_qa['validos']['total']} | "
        f"speeders={resumen_qa['speeders']['total']} | "
        f"Welch t={metricas['primario']['welch_t']:.7f} | "
        f"p={metricas['primario']['welch_p_unilateral']:.4e}"
    )


if __name__ == "__main__":
    main()
