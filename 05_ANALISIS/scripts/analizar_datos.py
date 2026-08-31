#!/usr/bin/env python
"""Pipeline reproducible del estudio docente «La velocidad de las frutas».

Este programa trabaja exclusivamente con la simulación docente. Valida primero el
contrato del CSV bruto y solo después escribe productos públicos, analíticos y
restringidos. No interpreta los resultados como evidencia de seguridad vial ni
como preferencias universales.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import re
import sys
import unicodedata
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import seaborn as sns
    import statsmodels.formula.api as smf
    from scipy import stats
except ImportError as exc:  # pragma: no cover - depende del entorno de ejecución
    print(
        "ERROR DE DEPENDENCIAS: falta un paquete de análisis. "
        "Instale 05_ANALISIS/requirements-analisis.txt en el entorno del proyecto. "
        f"Detalle: {exc}",
        file=sys.stderr,
    )
    raise SystemExit(3) from exc


ETIQUETA = "SIMULACIÓN DOCENTE"
AVISO = (
    "Datos totalmente sintéticos para docencia; no son observaciones reales y "
    "no demuestran seguridad vial ni preferencias universales."
)
SEMILLA_ANALISIS = 20260902
SEMILLA_BONOS = "20260903"
NUMERO_PERMUTACIONES = 100_000
NUMERO_BOOTSTRAP = 10_000
VELOCIDADES = [30, 50, 70, 90, 110, 130]
ORDENES = ["naranja_primero", "platano_primero"]

COLUMNAS_PUBLICAS = [
    "registro_id",
    "orden",
    "simbolo_primero",
    "velocidad_primera_kmh",
    "velocidad_naranja_kmh",
    "velocidad_platano_kmh",
    "confianza_naranja",
    "confianza_platano",
    "tiempo_primera_s",
    "tiempo_segunda_s",
    "diferencia_platano_menos_naranja",
    "categoria_motivo",
    "incluida",
    "motivo_exclusion",
    "origen_dato",
    "version_app",
]

CATEGORIAS = [
    "forma",
    "color",
    "fisica",
    "cultura",
    "contraste",
    "azar",
    "sin_clasificar",
]

# Orden fijo: una misma explicación puede activar varias categorías.
PATRONES_MOTIVO = {
    "forma": re.compile(
        r"\b(forma|redond\w*|curv\w*|alarg\w*|punta\w*|geometri\w*|siluet\w*)\b"
    ),
    "color": re.compile(r"\b(color|amarill\w*|negro|negra|oscur\w*)\b"),
    "fisica": re.compile(
        r"\b(peso|pesad\w*|liger\w*|rodar|rued\w*|aerodin\w*|fricci\w*)\b"
    ),
    "cultura": re.compile(
        r"\b(cultur\w*|costumbre\w*|trafic\w*|carretera\w*|deporte\w*|marca\w*)\b"
    ),
    "contraste": re.compile(r"\b(contraste|compar\w*|diferent\w*|primero|segundo)\b"),
    "azar": re.compile(r"\b(azar|aleatori\w*|intuici\w*|ningun\w*|porque si)\b"),
}


class ErrorContrato(ValueError):
    """Incumplimiento legible del contrato de datos."""


def sha256_bytes(contenido: bytes) -> str:
    return hashlib.sha256(contenido).hexdigest()


def sha256_texto(texto: str) -> str:
    return sha256_bytes(texto.encode("utf-8"))


def escribir_bytes(ruta: Path, contenido: bytes) -> None:
    """Escribe de forma atómica en el mismo volumen."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_name(ruta.name + ".tmp")
    temporal.write_bytes(contenido)
    os.replace(temporal, ruta)


def csv_bytes(tabla: pd.DataFrame, *, float_format: str | None = None) -> bytes:
    texto = tabla.to_csv(index=False, lineterminator="\n", float_format=float_format)
    return texto.encode("utf-8")


def exigir(condicion: bool, mensaje: str) -> None:
    if not condicion:
        raise ErrorContrato(mensaje)


def comprobar_numerica(
    tabla: pd.DataFrame,
    columna: str,
    *,
    minimo: float | None = None,
    maximo: float | None = None,
    enteros: bool = False,
    permitidos: Iterable[int] | None = None,
) -> pd.Series:
    original = tabla[columna]
    valores = pd.to_numeric(original, errors="coerce")
    exigir(
        bool(valores.notna().all()),
        f"la columna '{columna}' contiene valores ausentes o no numéricos",
    )
    exigir(
        bool(np.isfinite(valores.to_numpy(dtype=float)).all()),
        f"la columna '{columna}' contiene valores no finitos",
    )
    if minimo is not None:
        exigir(bool((valores >= minimo).all()), f"'{columna}' contiene valores menores que {minimo}")
    if maximo is not None:
        exigir(bool((valores <= maximo).all()), f"'{columna}' contiene valores mayores que {maximo}")
    if enteros:
        exigir(
            bool(np.equal(valores, np.floor(valores)).all()),
            f"'{columna}' debe contener enteros",
        )
        valores = valores.astype(int)
    if permitidos is not None:
        conjunto = set(int(x) for x in permitidos)
        observados = set(int(x) for x in valores.unique())
        exigir(
            observados == conjunto,
            f"'{columna}' debe usar exactamente {sorted(conjunto)}; se observó {sorted(observados)}",
        )
    tabla[columna] = valores
    return valores


def validar_bruto(tabla: pd.DataFrame, columnas_esperadas: list[str]) -> None:
    exigir(not tabla.columns.duplicated().any(), "el CSV contiene nombres de columna duplicados")
    actuales = list(tabla.columns)
    faltan = [c for c in columnas_esperadas if c not in actuales]
    sobran = [c for c in actuales if c not in columnas_esperadas]
    exigir(
        actuales == columnas_esperadas,
        "columnas brutas inválidas (también se exige el orden contractual). "
        f"Faltan: {faltan or 'ninguna'}; sobran: {sobran or 'ninguna'}",
    )
    exigir(len(tabla) == 500, f"se esperaban 500 filas y se encontraron {len(tabla)}")

    ids = tabla["registro_id"].astype("string")
    exigir(bool(ids.notna().all()), "'registro_id' contiene valores ausentes")
    exigir(bool(ids.str.fullmatch(r"SIM-[0-9]{6}").all()), "'registro_id' no cumple SIM-000000")
    exigir(bool(ids.is_unique), "'registro_id' debe ser único")
    tabla["registro_id"] = ids.astype(str)

    comprobar_numerica(tabla, "indice_asignacion", minimo=0, enteros=True)
    exigir(tabla["indice_asignacion"].is_unique, "'indice_asignacion' debe ser único")

    for columna in [
        "velocidad_primera_kmh",
        "velocidad_naranja_kmh",
        "velocidad_platano_kmh",
    ]:
        comprobar_numerica(tabla, columna, enteros=True, permitidos=VELOCIDADES)
    for columna in ["confianza_naranja", "confianza_platano"]:
        comprobar_numerica(tabla, columna, minimo=0, maximo=100, enteros=True)
    for columna in ["tiempo_primera_s", "tiempo_segunda_s"]:
        comprobar_numerica(tabla, columna, minimo=0)

    exigir(set(tabla["orden"].dropna()) == set(ORDENES), "'orden' solo admite los dos órdenes previstos")
    recuentos_orden = tabla["orden"].value_counts().to_dict()
    exigir(
        recuentos_orden == {"naranja_primero": 250, "platano_primero": 250},
        f"el orden debe estar equilibrado 250/250; se observó {recuentos_orden}",
    )
    exigir(
        set(tabla["simbolo_primero"].dropna()) == {"naranja", "platano"},
        "'simbolo_primero' solo admite naranja o platano",
    )
    esperado_simbolo = tabla["orden"].map(
        {"naranja_primero": "naranja", "platano_primero": "platano"}
    )
    exigir(
        bool(tabla["simbolo_primero"].eq(esperado_simbolo).all()),
        "incoherencia entre 'orden' y 'simbolo_primero'",
    )
    esperado_velocidad = np.where(
        tabla["simbolo_primero"].eq("naranja"),
        tabla["velocidad_naranja_kmh"],
        tabla["velocidad_platano_kmh"],
    )
    exigir(
        bool(np.equal(tabla["velocidad_primera_kmh"], esperado_velocidad).all()),
        "incoherencia entre 'simbolo_primero' y 'velocidad_primera_kmh'",
    )

    for columna in [
        "consentimiento",
        "edad_18_mas",
        "permiso_vigente",
        "comprende_espanol",
        "no_conduce_ahora",
    ]:
        normalizada = tabla[columna].astype("string").str.lower()
        exigir(bool(normalizada.eq("true").all()), f"'{columna}' debe ser verdadero en esta simulación")
        tabla[columna] = True

    exigir(bool(tabla["modo"].eq("docente").all()), "'modo' debe ser 'docente'")
    exigir(
        bool(tabla["origen_dato"].eq("sintetico_docente").all()),
        "'origen_dato' debe ser 'sintetico_docente'; no se aceptan datos reales",
    )
    exigir(
        bool(tabla["version_app"].astype(str).str.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?").all()),
        "'version_app' no cumple el patrón semántico esperado",
    )
    for columna in ["PROLIFIC_PID", "STUDY_ID", "SESSION_ID"]:
        exigir(
            bool(tabla[columna].isna().all() | tabla[columna].astype("string").str.strip().eq("").all()),
            f"'{columna}' debe estar vacío en la simulación docente",
        )
    respuestas = tabla["respuesta_abierta"].fillna("").astype(str)
    exigir(bool(respuestas.str.len().le(1000).all()), "'respuesta_abierta' supera 1000 caracteres")
    for columna in ["inicio_utc", "primera_render_utc", "segunda_render_utc", "fin_utc"]:
        convertida = pd.to_datetime(tabla[columna], utc=True, errors="coerce")
        exigir(bool(convertida.notna().all()), f"'{columna}' contiene timestamps ausentes o inválidos")


def normalizar_texto(valor: Any) -> str:
    texto = unicodedata.normalize("NFKD", "" if pd.isna(valor) else str(valor))
    return "".join(c for c in texto if not unicodedata.combining(c)).lower()


def categorizar_motivo(valor: Any) -> list[str]:
    texto = normalizar_texto(valor)
    halladas = [categoria for categoria, patron in PATRONES_MOTIVO.items() if patron.search(texto)]
    if not halladas and texto.strip():
        return ["sin_clasificar"]
    return halladas


def derivar_variables(tabla: pd.DataFrame) -> pd.DataFrame:
    salida = tabla.copy()
    primera_rapida = salida["tiempo_primera_s"].lt(2.0)
    segunda_rapida = salida["tiempo_segunda_s"].lt(2.0)
    salida["incluida"] = ~(primera_rapida | segunda_rapida)
    salida["motivo_exclusion"] = pd.Series(pd.NA, index=salida.index, dtype="string")
    salida.loc[primera_rapida & ~segunda_rapida, "motivo_exclusion"] = "tiempo_primera_menor_2"
    salida.loc[~primera_rapida & segunda_rapida, "motivo_exclusion"] = "tiempo_segunda_menor_2"
    salida.loc[primera_rapida & segunda_rapida, "motivo_exclusion"] = "tiempos_ambos_menor_2"
    salida["diferencia_platano_menos_naranja"] = (
        salida["velocidad_platano_kmh"] - salida["velocidad_naranja_kmh"]
    ).astype(int)
    salida["categoria_motivo"] = salida["respuesta_abierta"].map(categorizar_motivo)
    return salida


def validar_derivadas(tabla: pd.DataFrame) -> None:
    exigir(int(tabla["incluida"].sum()) == 480, "la exclusión mecánica debía conservar 480 filas")
    recuentos = tabla.groupby("orden", observed=True)["incluida"].sum().astype(int).to_dict()
    exigir(
        recuentos == {"naranja_primero": 240, "platano_primero": 240},
        f"la muestra válida debía quedar equilibrada 240/240; se observó {recuentos}",
    )
    en_umbral = tabla["tiempo_primera_s"].eq(2.0) | tabla["tiempo_segunda_s"].eq(2.0)
    exigir(
        bool(tabla.loc[en_umbral, "incluida"].all()),
        "la regla es estrictamente <2.0; los tiempos exactamente 2.00 deben conservarse",
    )
    exigir(
        bool(tabla.loc[tabla["incluida"], "motivo_exclusion"].isna().all()),
        "las filas incluidas no pueden tener motivo de exclusión",
    )
    exigir(
        bool(tabla.loc[~tabla["incluida"], "motivo_exclusion"].notna().all()),
        "las filas excluidas deben tener motivo de exclusión",
    )
    exigir(
        bool(tabla["categoria_motivo"].map(lambda xs: len(xs) == len(set(xs))).all()),
        "la categorización Regex produjo categorías repetidas",
    )
    exigir(
        bool(tabla["categoria_motivo"].map(lambda xs: set(xs).issubset(CATEGORIAS)).all()),
        "la categorización Regex produjo una categoría no pública",
    )


def construir_publico(tabla: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    objetos = tabla[COLUMNAS_PUBLICAS].copy()
    exigir(list(objetos.columns) == COLUMNAS_PUBLICAS, "falló la lista positiva del esquema público")
    exigir(objetos["registro_id"].is_unique, "el CSV público tendría IDs duplicados")
    exigir(
        not any(c in objetos.columns for c in ["respuesta_abierta", "PROLIFIC_PID", "SESSION_ID", "fin_utc"]),
        "el esquema público intentó incluir una columna restringida",
    )
    serializada = objetos.copy()
    serializada["categoria_motivo"] = serializada["categoria_motivo"].map(
        lambda xs: json.dumps(xs, ensure_ascii=False, separators=(",", ":"))
    )
    serializada["incluida"] = serializada["incluida"].map({True: "true", False: "false"})
    serializada["motivo_exclusion"] = serializada["motivo_exclusion"].fillna("")
    return objetos, serializada


def coordinacion(serie: pd.Series) -> dict[str, float | int]:
    n = int(len(serie))
    proporciones = serie.value_counts(normalize=True).reindex(VELOCIDADES, fill_value=0.0)
    plugin = float(np.square(proporciones.to_numpy(dtype=float)).sum())
    corregida = float((n * plugin - 1.0) / (n - 1.0)) if n > 1 else float("nan")
    return {"n": n, "suma_p2": plugin, "correccion_finita": corregida}


def intervalo_wilson(exitos: int, n: int, confianza: float = 0.95) -> list[float]:
    """Intervalo de Wilson para una proporción binaria."""
    exigir(n > 0, "el intervalo de Wilson requiere n positivo")
    z = float(stats.norm.ppf(0.5 + confianza / 2.0))
    proporcion = exitos / n
    z2 = z**2
    denominador = 1.0 + z2 / n
    centro = (proporcion + z2 / (2.0 * n)) / denominador
    semiancho = z * math.sqrt(
        proporcion * (1.0 - proporcion) / n + z2 / (4.0 * n**2)
    ) / denominador
    return [float(centro - semiancho), float(centro + semiancho)]


def ajuste_benjamini_hochberg(valores_p: list[float]) -> list[float]:
    """Ajuste BH monotónico, devuelto en el orden original."""
    p = np.asarray(valores_p, dtype=float)
    exigir(bool(np.isfinite(p).all()), "la familia BH contiene valores p no finitos")
    exigir(bool(((p >= 0.0) & (p <= 1.0)).all()), "la familia BH contiene valores p fuera de [0, 1]")
    orden = np.argsort(p)
    ordenados = p[orden]
    m = len(ordenados)
    ajustados_ordenados = ordenados * m / np.arange(1, m + 1)
    ajustados_ordenados = np.minimum.accumulate(ajustados_ordenados[::-1])[::-1]
    ajustados_ordenados = np.minimum(ajustados_ordenados, 1.0)
    ajustados = np.empty(m, dtype=float)
    ajustados[orden] = ajustados_ordenados
    return [float(x) for x in ajustados]


def permutacion_chi_cuadrado(
    tabla: pd.DataFrame,
    chi2_observado: float,
) -> float:
    """Permuta la etiqueta de fila manteniendo fijos los márgenes 2 x k."""
    exigir(tabla.shape[0] == 2, "la permutación implementada requiere exactamente dos filas")
    totales_columnas = tabla.sum(axis=0).to_numpy(dtype=int)
    n_fila_1 = int(tabla.iloc[0].sum())
    n_total = int(totales_columnas.sum())
    n_fila_2 = n_total - n_fila_1
    generador = np.random.default_rng(SEMILLA_ANALISIS)
    muestras_fila_1 = generador.multivariate_hypergeometric(
        totales_columnas,
        nsample=n_fila_1,
        size=NUMERO_PERMUTACIONES,
    )
    esperada_1 = n_fila_1 * totales_columnas / n_total
    esperada_2 = n_fila_2 * totales_columnas / n_total
    muestras_fila_2 = totales_columnas - muestras_fila_1
    chi2_permutado = (
        ((muestras_fila_1 - esperada_1) ** 2 / esperada_1)
        + ((muestras_fila_2 - esperada_2) ** 2 / esperada_2)
    ).sum(axis=1)
    return float(
        (np.count_nonzero(chi2_permutado >= chi2_observado - 1e-12) + 1)
        / (NUMERO_PERMUTACIONES + 1)
    )


def bootstrap_diferencia_coordinacion(validos: pd.DataFrame) -> dict[str, Any]:
    """IC percentil de la diferencia naranja - plátano, remuestreando personas."""
    naranja = validos["velocidad_naranja_kmh"].to_numpy(dtype=int)
    platano = validos["velocidad_platano_kmh"].to_numpy(dtype=int)
    n = len(validos)
    generador = np.random.default_rng(SEMILLA_ANALISIS)
    diferencias = np.empty(NUMERO_BOOTSTRAP, dtype=float)
    for replica in range(NUMERO_BOOTSTRAP):
        indices = generador.integers(0, n, size=n)
        p_naranja = np.array(
            [np.mean(naranja[indices] == velocidad) for velocidad in VELOCIDADES]
        )
        p_platano = np.array(
            [np.mean(platano[indices] == velocidad) for velocidad in VELOCIDADES]
        )
        diferencias[replica] = float(np.square(p_naranja).sum() - np.square(p_platano).sum())
    estimacion = coordinacion(validos["velocidad_naranja_kmh"])["suma_p2"] - coordinacion(
        validos["velocidad_platano_kmh"]
    )["suma_p2"]
    return {
        "estimacion_naranja_menos_platano": float(estimacion),
        "ic95_percentil": [float(x) for x in np.quantile(diferencias, [0.025, 0.975])],
        "remuestreos": NUMERO_BOOTSTRAP,
        "semilla": SEMILLA_ANALISIS,
    }


def analizar_logit_bonificaciones(mapa: pd.DataFrame) -> dict[str, Any]:
    """Modelo secundario restringido; solo devuelve coeficientes agregados."""
    datos = mapa.copy()
    datos["coincide_binaria"] = datos["coincide_pareja"].eq("true").astype(int)
    datos["confianza_decena"] = pd.to_numeric(
        datos["confianza_seleccionada"], errors="raise"
    ) / 10.0
    formula = (
        "coincide_binaria ~ confianza_decena + "
        "C(simbolo_bonificacion, Treatment(reference='naranja'))"
    )
    modelo = smf.logit(formula, data=datos).fit(
        disp=False,
        cov_type="cluster",
        cov_kwds={"groups": datos["pair_id"]},
    )
    nombre_simbolo = (
        "C(simbolo_bonificacion, Treatment(reference='naranja'))[T.platano]"
    )
    intervalos = modelo.conf_int(alpha=0.05)
    return {
        "formula": "coincide_pareja ~ confianza_seleccionada/10 + C(simbolo_bonificacion)",
        "n_personas": int(modelo.nobs),
        "n_parejas": int(datos["pair_id"].nunique()),
        "errores_agrupados_por": "pair_id",
        "coeficientes_log_odds": {
            "intercepto": float(modelo.params["Intercept"]),
            "confianza_por_10_puntos": float(modelo.params["confianza_decena"]),
            "simbolo_platano": float(modelo.params[nombre_simbolo]),
        },
        "errores_estandar_cluster": {
            "intercepto": float(modelo.bse["Intercept"]),
            "confianza_por_10_puntos": float(modelo.bse["confianza_decena"]),
            "simbolo_platano": float(modelo.bse[nombre_simbolo]),
        },
        "ic95_coeficientes": {
            "intercepto": [float(x) for x in intervalos.loc["Intercept"]],
            "confianza_por_10_puntos": [float(x) for x in intervalos.loc["confianza_decena"]],
            "simbolo_platano": [float(x) for x in intervalos.loc[nombre_simbolo]],
        },
        "p_valores": {
            "intercepto": float(modelo.pvalues["Intercept"]),
            "confianza_por_10_puntos": float(modelo.pvalues["confianza_decena"]),
            "simbolo_platano": float(modelo.pvalues[nombre_simbolo]),
        },
        "odds_ratio_confianza_por_10_puntos": float(
            math.exp(modelo.params["confianza_decena"])
        ),
    }


def analizar(
    tabla: pd.DataFrame,
    mapa_bonos: pd.DataFrame,
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame, Any]:
    validos = tabla.loc[tabla["incluida"]].copy()
    grupo_naranja = validos.loc[validos["orden"].eq("naranja_primero"), "velocidad_primera_kmh"].to_numpy(float)
    grupo_platano = validos.loc[validos["orden"].eq("platano_primero"), "velocidad_primera_kmh"].to_numpy(float)

    prueba = stats.ttest_ind(grupo_naranja, grupo_platano, equal_var=False, alternative="greater")
    var_n = float(np.var(grupo_naranja, ddof=1))
    var_p = float(np.var(grupo_platano, ddof=1))
    n_n, n_p = len(grupo_naranja), len(grupo_platano)
    diferencia = float(np.mean(grupo_naranja) - np.mean(grupo_platano))
    se = math.sqrt(var_n / n_n + var_p / n_p)
    gl = (var_n / n_n + var_p / n_p) ** 2 / (
        (var_n / n_n) ** 2 / (n_n - 1) + (var_p / n_p) ** 2 / (n_p - 1)
    )
    critico = float(stats.t.ppf(0.975, gl))
    ic = [diferencia - critico * se, diferencia + critico * se]
    sd_agrupada = math.sqrt(((n_n - 1) * var_n + (n_p - 1) * var_p) / (n_n + n_p - 2))
    d_cohen = diferencia / sd_agrupada

    delta = validos["diferencia_platano_menos_naranja"].to_numpy(dtype=float)
    prueba_pareada = stats.ttest_rel(
        validos["velocidad_platano_kmh"],
        validos["velocidad_naranja_kmh"],
        alternative="two-sided",
    )
    media_delta = float(np.mean(delta))
    desviacion_delta = float(np.std(delta, ddof=1))
    se_delta = desviacion_delta / math.sqrt(len(delta))
    critico_delta = float(stats.t.ppf(0.975, len(delta) - 1))
    ic_delta = [
        media_delta - critico_delta * se_delta,
        media_delta + critico_delta * se_delta,
    ]

    velocidad_distinta = validos["velocidad_naranja_kmh"].ne(
        validos["velocidad_platano_kmh"]
    )
    tabla_distintas = pd.crosstab(validos["orden"], velocidad_distinta).reindex(
        index=ORDENES,
        columns=[False, True],
        fill_value=0,
    )
    chi2_distintas, p_distintas_chi, gl_distintas, esperadas_distintas = (
        stats.chi2_contingency(tabla_distintas.to_numpy(), correction=False)
    )
    if float(np.min(esperadas_distintas)) < 5.0:
        _, p_distintas = stats.fisher_exact(tabla_distintas.to_numpy(), alternative="two-sided")
        prueba_distintas = "Fisher bilateral"
    else:
        p_distintas = p_distintas_chi
        prueba_distintas = "chi-cuadrado 2x2 sin corrección de Yates"

    formula_delta = (
        "diferencia_platano_menos_naranja ~ "
        "C(orden, Treatment(reference='naranja_primero'))"
    )
    modelo_delta = smf.ols(formula_delta, data=validos).fit(cov_type="HC3")
    nombre_orden_delta = (
        "C(orden, Treatment(reference='naranja_primero'))[T.platano_primero]"
    )
    intervalo_delta_orden = modelo_delta.conf_int(alpha=0.05).loc[nombre_orden_delta]

    correlacion = stats.pearsonr(
        validos["velocidad_naranja_kmh"], validos["velocidad_platano_kmh"]
    )
    formula = "velocidad_naranja_kmh ~ velocidad_platano_kmh + C(orden, Treatment(reference='naranja_primero'))"
    modelo = smf.ols(formula, data=validos).fit(cov_type="HC3")
    nombre_orden = "C(orden, Treatment(reference='naranja_primero'))[T.platano_primero]"
    intervalos_modelo = modelo.conf_int(alpha=0.05)

    tabla_chi = pd.crosstab(validos["orden"], validos["velocidad_primera_kmh"]).reindex(
        index=ORDENES, columns=VELOCIDADES, fill_value=0
    )
    chi2, p_chi_asintotico, gl_chi, esperadas = stats.chi2_contingency(
        tabla_chi.to_numpy(),
        correction=False,
    )
    p_chi_permutacion = permutacion_chi_cuadrado(tabla_chi, float(chi2))
    usa_permutacion = bool(float(np.min(esperadas)) < 5.0)
    p_chi_inferencial = p_chi_permutacion if usa_permutacion else float(p_chi_asintotico)
    v_cramer = math.sqrt(
        float(chi2)
        / (
            float(tabla_chi.to_numpy().sum())
            * min(tabla_chi.shape[0] - 1, tabla_chi.shape[1] - 1)
        )
    )
    residuos_chi = (tabla_chi.to_numpy(dtype=float) - esperadas) / np.sqrt(esperadas)

    bootstrap_coordinacion = bootstrap_diferencia_coordinacion(validos)
    logit_bonificaciones = analizar_logit_bonificaciones(mapa_bonos)

    familia_ids = [
        "S1_diferencia_pareada",
        "S2_velocidades_distintas_por_orden",
        "S3_efecto_orden_sobre_delta",
        "S4_ols_pendiente_platano",
        "S5_ols_efecto_orden",
        "S6_distribucion_2x6",
        "S7_confianza_y_coincidencia",
    ]
    familia_nombres = [
        "t pareada bilateral de plátano menos naranja",
        "asociación bilateral entre velocidades distintas y orden",
        "coeficiente bilateral de orden en delta",
        "pendiente bilateral de velocidad del plátano en OLS",
        "coeficiente bilateral de orden en OLS de velocidad de naranja",
        "distribución completa 2x6; permutación si esperada < 5",
        "coeficiente bilateral de confianza en logit agrupado por pareja",
    ]
    familia_p = [
        float(prueba_pareada.pvalue),
        float(p_distintas),
        float(modelo_delta.pvalues[nombre_orden_delta]),
        float(modelo.pvalues["velocidad_platano_kmh"]),
        float(modelo.pvalues[nombre_orden]),
        float(p_chi_inferencial),
        float(logit_bonificaciones["p_valores"]["confianza_por_10_puntos"]),
    ]
    familia_p_bh = ajuste_benjamini_hochberg(familia_p)
    bh_por_id = dict(zip(familia_ids, familia_p_bh, strict=True))

    resultados: dict[str, Any] = {
        "rotulo": ETIQUETA,
        "aviso_interpretacion": AVISO,
        "contrato_muestra": {
            "filas_brutas": int(len(tabla)),
            "filas_incluidas": int(validos.shape[0]),
            "filas_excluidas_tiempo_menor_2": int((~tabla["incluida"]).sum()),
            "regla_exclusion": "se excluye si cualquiera de los dos tiempos es < 2.0 s; 2.00 s se conserva",
            "incluidas_por_orden": {
                clave: int(valor)
                for clave, valor in validos["orden"].value_counts().reindex(ORDENES).items()
            },
        },
        "analisis_primario_primera_respuesta": {
            "definicion": "Welch unilateral: velocidad primera, naranja primero > plátano primero",
            "usa_solo_primera_respuesta": True,
            "n_naranja_primero": int(n_n),
            "n_platano_primero": int(n_p),
            "media_naranja_primero": float(np.mean(grupo_naranja)),
            "media_platano_primero": float(np.mean(grupo_platano)),
            "diferencia_medias_naranja_menos_platano": diferencia,
            "t_welch": float(prueba.statistic),
            "gl_welch": float(gl),
            "p_unilateral": float(prueba.pvalue),
            "ic95_diferencia_bilateral": [float(x) for x in ic],
            "cohen_d": float(d_cohen),
        },
        "analisis_secundarios": {
            "media_global_naranja": float(validos["velocidad_naranja_kmh"].mean()),
            "media_global_platano": float(validos["velocidad_platano_kmh"].mean()),
            "media_delta_platano_menos_naranja": media_delta,
            "proporcion_velocidades_distintas": float(velocidad_distinta.mean()),
            "diferencia_dentro_del_sujeto": {
                "definicion": "velocidad_platano_kmh - velocidad_naranja_kmh",
                "n": int(len(delta)),
                "media": media_delta,
                "desviacion_estandar": desviacion_delta,
                "ic95_media": [float(x) for x in ic_delta],
                "t_pareada": float(prueba_pareada.statistic),
                "gl": int(len(delta) - 1),
                "p_bilateral": float(prueba_pareada.pvalue),
                "p_bh": bh_por_id["S1_diferencia_pareada"],
            },
            "velocidades_distintas": {
                "n_distintas": int(velocidad_distinta.sum()),
                "n_total": int(len(velocidad_distinta)),
                "proporcion_total": float(velocidad_distinta.mean()),
                "ic95_wilson_total": intervalo_wilson(
                    int(velocidad_distinta.sum()), int(len(velocidad_distinta))
                ),
                "por_orden": {
                    orden: {
                        "n_distintas": int(
                            velocidad_distinta.loc[validos["orden"].eq(orden)].sum()
                        ),
                        "n": int(validos["orden"].eq(orden).sum()),
                        "proporcion": float(
                            velocidad_distinta.loc[validos["orden"].eq(orden)].mean()
                        ),
                        "ic95_wilson": intervalo_wilson(
                            int(velocidad_distinta.loc[validos["orden"].eq(orden)].sum()),
                            int(validos["orden"].eq(orden).sum()),
                        ),
                    }
                    for orden in ORDENES
                },
                "tabla_2x2": {
                    orden: {
                        "iguales": int(tabla_distintas.loc[orden, False]),
                        "distintas": int(tabla_distintas.loc[orden, True]),
                    }
                    for orden in ORDENES
                },
                "prueba": prueba_distintas,
                "estadistico_chi2": float(chi2_distintas),
                "gl_chi2": int(gl_distintas),
                "frecuencia_esperada_minima": float(np.min(esperadas_distintas)),
                "p_bilateral": float(p_distintas),
                "p_bh": bh_por_id["S2_velocidades_distintas_por_orden"],
            },
            "efecto_orden_sobre_diferencia_ols_hc3": {
                "formula": "diferencia_platano_menos_naranja ~ orden",
                "referencia_orden": "naranja_primero",
                "n": int(modelo_delta.nobs),
                "r_cuadrado": float(modelo_delta.rsquared),
                "coeficiente_orden_platano_primero": float(
                    modelo_delta.params[nombre_orden_delta]
                ),
                "error_estandar_hc3": float(modelo_delta.bse[nombre_orden_delta]),
                "ic95": [float(x) for x in intervalo_delta_orden],
                "p_bilateral": float(modelo_delta.pvalues[nombre_orden_delta]),
                "p_bh": bh_por_id["S3_efecto_orden_sobre_delta"],
            },
            "correlacion_pearson": {
                "clasificacion": "exploratoria; fuera de la familia BH prerregistrada",
                "r": float(correlacion.statistic),
                "p_bilateral": float(correlacion.pvalue),
            },
            "confianza": {
                "media_naranja": float(validos["confianza_naranja"].mean()),
                "media_platano": float(validos["confianza_platano"].mean()),
                "media_primera": float(
                    np.where(
                        validos["simbolo_primero"].eq("naranja"),
                        validos["confianza_naranja"],
                        validos["confianza_platano"],
                    ).mean()
                ),
                "media_segunda": float(
                    np.where(
                        validos["simbolo_primero"].eq("naranja"),
                        validos["confianza_platano"],
                        validos["confianza_naranja"],
                    ).mean()
                ),
            },
            "coordinacion": {
                "naranja": coordinacion(validos["velocidad_naranja_kmh"]),
                "platano": coordinacion(validos["velocidad_platano_kmh"]),
                "diferencia_plugin_bootstrap": bootstrap_coordinacion,
            },
            "ols_hc3": {
                "formula": "velocidad_naranja_kmh ~ velocidad_platano_kmh + orden",
                "referencia_orden": "naranja_primero",
                "n": int(modelo.nobs),
                "r_cuadrado": float(modelo.rsquared),
                "coeficientes": {
                    "intercepto": float(modelo.params["Intercept"]),
                    "velocidad_platano_kmh": float(modelo.params["velocidad_platano_kmh"]),
                    "orden_platano_primero": float(modelo.params[nombre_orden]),
                },
                "errores_estandar_hc3": {
                    "intercepto": float(modelo.bse["Intercept"]),
                    "velocidad_platano_kmh": float(modelo.bse["velocidad_platano_kmh"]),
                    "orden_platano_primero": float(modelo.bse[nombre_orden]),
                },
                "p_valores_hc3": {
                    "intercepto": float(modelo.pvalues["Intercept"]),
                    "velocidad_platano_kmh": float(modelo.pvalues["velocidad_platano_kmh"]),
                    "orden_platano_primero": float(modelo.pvalues[nombre_orden]),
                },
                "ic95_coeficientes": {
                    "intercepto": [float(x) for x in intervalos_modelo.loc["Intercept"]],
                    "velocidad_platano_kmh": [
                        float(x) for x in intervalos_modelo.loc["velocidad_platano_kmh"]
                    ],
                    "orden_platano_primero": [
                        float(x) for x in intervalos_modelo.loc[nombre_orden]
                    ],
                },
                "p_bh": {
                    "velocidad_platano_kmh": bh_por_id["S4_ols_pendiente_platano"],
                    "orden_platano_primero": bh_por_id["S5_ols_efecto_orden"],
                },
            },
            "chi_cuadrado_orden_por_primera_velocidad": {
                "tabla_2x6": {
                    orden: {str(v): int(tabla_chi.loc[orden, v]) for v in VELOCIDADES}
                    for orden in ORDENES
                },
                "chi2": float(chi2),
                "gl": int(gl_chi),
                "p": float(p_chi_inferencial),
                "p_inferencial": float(p_chi_inferencial),
                "p_asintotico": float(p_chi_asintotico),
                "p_permutacion": float(p_chi_permutacion),
                "numero_permutaciones": NUMERO_PERMUTACIONES,
                "semilla_permutacion": SEMILLA_ANALISIS,
                "usa_permutacion_por_frecuencia_esperada_menor_5": usa_permutacion,
                "p_bh": bh_por_id["S6_distribucion_2x6"],
                "frecuencia_esperada_minima": float(np.min(esperadas)),
                "v_cramer": float(v_cramer),
                "residuos_estandarizados": {
                    orden: {
                        str(velocidad): float(residuos_chi[fila, columna])
                        for columna, velocidad in enumerate(VELOCIDADES)
                    }
                    for fila, orden in enumerate(ORDENES)
                },
            },
            "confianza_y_coincidencia_logit": {
                **logit_bonificaciones,
                "p_bh_confianza": bh_por_id["S7_confianza_y_coincidencia"],
                "poblacion": "500 filas del mapa restringido; la bonificación no usa exclusiones analíticas",
            },
            "familia_benjamini_hochberg": [
                {
                    "id": identificador,
                    "prueba": nombre,
                    "p_bruto": p_bruto,
                    "p_bh": p_bh,
                    "rechaza_bh_0_05": bool(p_bh < 0.05),
                }
                for identificador, nombre, p_bruto, p_bh in zip(
                    familia_ids,
                    familia_nombres,
                    familia_p,
                    familia_p_bh,
                    strict=True,
                )
            ],
        },
        "regex_exploratoria": {
            "nota": (
                "Categorías no mutuamente excluyentes mediante los patrones congelados "
                "en el prerregistro; el texto sintético abierto no se publica."
            ),
            "recuentos_incluidos": {
                categoria: int(validos["categoria_motivo"].map(lambda xs, c=categoria: c in xs).sum())
                for categoria in CATEGORIAS
            },
        },
    }

    filas_descriptivas: list[dict[str, Any]] = []
    series = [
        ("primario", "velocidad_primera_kmh", "naranja_primero", pd.Series(grupo_naranja)),
        ("primario", "velocidad_primera_kmh", "platano_primero", pd.Series(grupo_platano)),
        ("secundario", "velocidad_naranja_kmh", "muestra_valida", validos["velocidad_naranja_kmh"]),
        ("secundario", "velocidad_platano_kmh", "muestra_valida", validos["velocidad_platano_kmh"]),
        ("secundario", "confianza_naranja", "muestra_valida", validos["confianza_naranja"]),
        ("secundario", "confianza_platano", "muestra_valida", validos["confianza_platano"]),
        (
            "secundario",
            "diferencia_platano_menos_naranja",
            "muestra_valida",
            validos["diferencia_platano_menos_naranja"],
        ),
    ]
    for ambito, variable, grupo, serie in series:
        filas_descriptivas.append(
            {
                "rotulo": ETIQUETA,
                "ambito": ambito,
                "variable": variable,
                "grupo": grupo,
                "n": int(serie.count()),
                "media": float(serie.mean()),
                "desviacion_estandar": float(serie.std(ddof=1)),
                "mediana": float(serie.median()),
                "minimo": float(serie.min()),
                "maximo": float(serie.max()),
            }
        )
    descriptiva = pd.DataFrame(filas_descriptivas)

    largo = validos.melt(
        id_vars=["registro_id", "orden"],
        value_vars=["velocidad_naranja_kmh", "velocidad_platano_kmh"],
        var_name="simbolo_variable",
        value_name="velocidad_kmh",
    )
    largo["simbolo"] = largo["simbolo_variable"].map(
        {"velocidad_naranja_kmh": "naranja", "velocidad_platano_kmh": "platano"}
    )
    return resultados, descriptiva, largo, modelo


def construir_mapa_bonos(tabla: pd.DataFrame, hash_bruto: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    personas: list[dict[str, Any]] = []
    for fila in tabla.to_dict(orient="records"):
        registro_id = str(fila["registro_id"])
        participante = sha256_texto(f"{SEMILLA_BONOS}|participante_sintetico|{registro_id}")
        sesion = sha256_texto(f"{SEMILLA_BONOS}|sesion_sintetica|{registro_id}")
        personas.append(
            {
                "participant_hmac": participante,
                "session_hmac": sesion,
                "clave_orden": sha256_texto(f"{SEMILLA_BONOS}|orden|{participante}"),
                "velocidad_naranja_kmh": int(fila["velocidad_naranja_kmh"]),
                "velocidad_platano_kmh": int(fila["velocidad_platano_kmh"]),
                "confianza_naranja": int(fila["confianza_naranja"]),
                "confianza_platano": int(fila["confianza_platano"]),
            }
        )
    personas.sort(key=lambda x: (x["clave_orden"], x["participant_hmac"]))
    run_id = "SIMBONO-" + sha256_texto(f"{SEMILLA_BONOS}|run|{hash_bruto}")[:16].upper()
    filas: list[dict[str, Any]] = []
    resumen_fruta = {"naranja": {"parejas": 0, "coincidentes": 0}, "platano": {"parejas": 0, "coincidentes": 0}}
    for posicion in range(0, len(personas), 2):
        numero = posicion // 2 + 1
        a, b = personas[posicion], personas[posicion + 1]
        primer_byte = hashlib.sha256(
            f"{SEMILLA_BONOS}|fruta|{numero}|{a['participant_hmac']}|{b['participant_hmac']}".encode("utf-8")
        ).digest()[0]
        fruta = "naranja" if primer_byte % 2 == 0 else "platano"
        columna = f"velocidad_{fruta}_kmh"
        coincide = a[columna] == b[columna]
        resumen_fruta[fruta]["parejas"] += 1
        resumen_fruta[fruta]["coincidentes"] += int(coincide)
        pair_id = f"{run_id}-P{numero:03d}"
        for propia, pareja in [(a, b), (b, a)]:
            filas.append(
                {
                    "clasificacion": "RESTRINGIDO - SIMULACIÓN DOCENTE",
                    "origen_dato": "sintetico_docente",
                    "run_id": run_id,
                    "pair_id": pair_id,
                    "participant_hmac": propia["participant_hmac"],
                    "session_hmac": propia["session_hmac"],
                    "simbolo_bonificacion": fruta,
                    "velocidad_propia_kmh": propia[columna],
                    "velocidad_pareja_kmh": pareja[columna],
                    "confianza_seleccionada": propia[f"confianza_{fruta}"],
                    "coincide_pareja": "true" if coincide else "false",
                    "importe_bonificacion_eur": "0.50" if coincide else "0.00",
                    "motivo_pago": "coincidencia" if coincide else "sin_coincidencia",
                    "estado_pago": "pendiente" if coincide else "no_corresponde",
                    "nota_identificador": "SHA-256 sintético docente; no es HMAC real",
                }
            )
    mapa = pd.DataFrame(filas)
    validar_mapa_bonos(mapa)
    parejas_coincidentes = int(
        mapa.loc[mapa["coincide_pareja"].eq("true"), "pair_id"].nunique()
    )
    filas_bonificadas = int(mapa["importe_bonificacion_eur"].eq("0.50").sum())
    importe = sum(Decimal(x) for x in mapa["importe_bonificacion_eur"])
    resumen = {
        "clasificacion": "RESTRINGIDO",
        "rotulo": ETIQUETA,
        "semilla": int(SEMILLA_BONOS),
        "poblacion": "las 500 filas, sin aplicar la exclusión analítica",
        "algoritmo_identificador": "SHA-256 sintético docente sin clave; el nombre de columna protocolario participant_hmac no implica HMAC real",
        "run_id": run_id,
        "parejas_totales": int(mapa["pair_id"].nunique()),
        "parejas_coincidentes": parejas_coincidentes,
        "personas_bonificadas": filas_bonificadas,
        "importe_total_eur": f"{importe:.2f}",
        "por_simbolo": resumen_fruta,
    }
    return mapa, resumen


def validar_mapa_bonos(mapa: pd.DataFrame) -> None:
    exigir(len(mapa) == 500, "el mapa restringido debe contener 500 personas")
    exigir(mapa["participant_hmac"].is_unique, "cada seudónimo debe aparecer una sola vez en el mapa")
    exigir(mapa["session_hmac"].is_unique, "cada sesión sintética debe aparecer una sola vez")
    confianza = pd.to_numeric(mapa["confianza_seleccionada"], errors="coerce")
    exigir(
        bool(confianza.notna().all() and confianza.between(0, 100, inclusive="both").all()),
        "la confianza seleccionada debe estar entre 0 y 100",
    )
    tamanos = mapa.groupby("pair_id").size()
    exigir(len(tamanos) == 250 and bool(tamanos.eq(2).all()), "el mapa debe tener 250 parejas de dos personas")
    for _, pareja in mapa.groupby("pair_id", sort=False):
        a, b = pareja.iloc[0], pareja.iloc[1]
        exigir(a["simbolo_bonificacion"] == b["simbolo_bonificacion"], "una pareja tiene símbolos distintos")
        exigir(a["coincide_pareja"] == b["coincide_pareja"], "una pareja tiene indicadores distintos")
        exigir(
            int(a["velocidad_propia_kmh"]) == int(b["velocidad_pareja_kmh"])
            and int(b["velocidad_propia_kmh"]) == int(a["velocidad_pareja_kmh"]),
            "las velocidades propia/pareja no son recíprocas",
        )
        coincide_real = int(a["velocidad_propia_kmh"]) == int(a["velocidad_pareja_kmh"])
        exigir((a["coincide_pareja"] == "true") == coincide_real, "el indicador de coincidencia es incorrecto")
    parejas = mapa.loc[mapa["coincide_pareja"].eq("true"), "pair_id"].nunique()
    bonificados = mapa["importe_bonificacion_eur"].eq("0.50").sum()
    importe = sum(Decimal(x) for x in mapa["importe_bonificacion_eur"])
    exigir(int(parejas) == 83, f"se esperaban 83 parejas coincidentes y se obtuvieron {parejas}")
    exigir(int(bonificados) == 166, f"se esperaban 166 bonos y se obtuvieron {bonificados}")
    exigir(importe == Decimal("83.00"), f"se esperaban 83.00 EUR y se obtuvieron {importe}")


def guardar_figura(figura: Any, ruta: Path) -> None:
    memoria = io.BytesIO()
    figura.savefig(
        memoria,
        format="png",
        dpi=160,
        bbox_inches="tight",
        metadata={"Title": ETIQUETA, "Description": AVISO, "Author": "curso_velocidad_frutas_2026"},
    )
    plt.close(figura)
    escribir_bytes(ruta, memoria.getvalue())


def generar_figuras(tabla: pd.DataFrame, resultados: dict[str, Any], modelo: Any, directorio: Path) -> list[Path]:
    sns.set_theme(style="whitegrid", context="notebook")
    colores = {"naranja": "#E07A1F", "platano": "#D4B000"}
    validos = tabla.loc[tabla["incluida"]].copy()
    rutas: list[Path] = []

    # 1. Distribuciones globales, solapadas y discretas.
    fig, ax = plt.subplots(figsize=(8.6, 5.2))
    x = np.arange(len(VELOCIDADES))
    conteo_n = validos["velocidad_naranja_kmh"].value_counts().reindex(VELOCIDADES, fill_value=0)
    conteo_p = validos["velocidad_platano_kmh"].value_counts().reindex(VELOCIDADES, fill_value=0)
    ancho = 0.38
    ax.bar(x - ancho / 2, conteo_n, ancho, label="Naranja", color=colores["naranja"], alpha=0.82)
    ax.bar(x + ancho / 2, conteo_p, ancho, label="Plátano", color=colores["platano"], alpha=0.82)
    ax.set(xticks=x, xticklabels=VELOCIDADES, xlabel="Velocidad elegida (km/h)", ylabel="Frecuencia")
    ax.set_title(f"{ETIQUETA} — Distribuciones en la muestra válida")
    ax.legend()
    fig.subplots_adjust(bottom=0.22)
    fig.text(0.5, 0.01, "n=480; datos sintéticos, no implican seguridad vial", ha="center", fontsize=9)
    ruta = directorio / "01_distribucion_velocidades.png"
    guardar_figura(fig, ruta)
    rutas.append(ruta)

    # 2. Comparación primaria: únicamente la primera decisión.
    fig, ax = plt.subplots(figsize=(8.6, 5.2))
    tabla_primaria = pd.crosstab(validos["orden"], validos["velocidad_primera_kmh"]).reindex(
        index=ORDENES, columns=VELOCIDADES, fill_value=0
    )
    ax.plot(VELOCIDADES, tabla_primaria.loc["naranja_primero"], marker="o", linewidth=2.2, color=colores["naranja"], label="Naranja primero")
    ax.plot(VELOCIDADES, tabla_primaria.loc["platano_primero"], marker="o", linewidth=2.2, color=colores["platano"], label="Plátano primero")
    ax.set(xlabel="Primera velocidad (km/h)", ylabel="Frecuencia")
    ax.set_xticks(VELOCIDADES)
    ax.set_title(f"{ETIQUETA} — Comparación primaria (solo primera respuesta)")
    primario = resultados["analisis_primario_primera_respuesta"]
    ax.text(
        0.02,
        0.96,
        f"Medias: {primario['media_naranja_primero']:.2f} vs {primario['media_platano_primero']:.2f} km/h\nWelch unilateral: t={primario['t_welch']:.3f}",
        transform=ax.transAxes,
        va="top",
        bbox={"facecolor": "white", "alpha": 0.86, "edgecolor": "#888888"},
    )
    ax.legend()
    ruta = directorio / "02_comparacion_primaria.png"
    guardar_figura(fig, ruta)
    rutas.append(ruta)

    # 3. Índice de coordinación Σp² y corrección de muestra finita.
    fig, ax = plt.subplots(figsize=(7.8, 5.0))
    coord = resultados["analisis_secundarios"]["coordinacion"]
    nombres = ["Naranja", "Plátano"]
    plugin = [coord["naranja"]["suma_p2"], coord["platano"]["suma_p2"]]
    finita = [coord["naranja"]["correccion_finita"], coord["platano"]["correccion_finita"]]
    posiciones = np.arange(2)
    ax.bar(posiciones - 0.18, plugin, 0.36, label="Σp²", color="#4361A6")
    ax.bar(posiciones + 0.18, finita, 0.36, label="Corrección finita", color="#87A8D0")
    ax.set(xticks=posiciones, xticklabels=nombres, ylabel="Probabilidad estimada de coincidencia", ylim=(0, 0.45))
    ax.set_title(f"{ETIQUETA} — Coordinación por símbolo")
    ax.legend()
    ruta = directorio / "03_coordinacion.png"
    guardar_figura(fig, ruta)
    rutas.append(ruta)

    # 4. Regresión: puntos agregados para evitar jitter aleatorio.
    fig, ax = plt.subplots(figsize=(8.2, 5.4))
    marcadores = {"naranja_primero": "o", "platano_primero": "s"}
    etiquetas = {"naranja_primero": "Naranja primero", "platano_primero": "Plátano primero"}
    for orden in ORDENES:
        sub = validos.loc[validos["orden"].eq(orden)]
        agregada = sub.groupby(["velocidad_platano_kmh", "velocidad_naranja_kmh"]).size().reset_index(name="n")
        color = "#E07A1F" if orden == "naranja_primero" else "#7867A8"
        ax.scatter(
            agregada["velocidad_platano_kmh"],
            agregada["velocidad_naranja_kmh"],
            s=14 + agregada["n"] * 5,
            alpha=0.58,
            marker=marcadores[orden],
            color=color,
            edgecolor="white",
            linewidth=0.5,
            label=etiquetas[orden],
        )
        rejilla = pd.DataFrame({"velocidad_platano_kmh": np.linspace(30, 130, 101), "orden": orden})
        ax.plot(rejilla["velocidad_platano_kmh"], modelo.predict(rejilla), color=color, linewidth=2.2)
    ax.set(xlabel="Velocidad del plátano (km/h)", ylabel="Velocidad de la naranja (km/h)")
    ax.set_title(f"{ETIQUETA} — OLS con líneas por orden (EE HC3)")
    ax.legend(title="Orden")
    ax.text(0.02, 0.97, f"R² = {modelo.rsquared:.3f}", transform=ax.transAxes, va="top")
    ruta = directorio / "04_regresion_ols.png"
    guardar_figura(fig, ruta)
    rutas.append(ruta)
    return rutas


def hash_archivo(ruta: Path) -> str:
    return sha256_bytes(ruta.read_bytes())


def ejecutar(input_csv: Path, raiz_salida: Path) -> dict[str, Any]:
    raiz_proyecto = Path(__file__).resolve().parents[2]
    esquema_raw = raiz_proyecto / "04_DATOS" / "metadata" / "schema_raw.json"
    exigir(input_csv.is_file(), f"no existe el CSV de entrada: {input_csv}")
    exigir(esquema_raw.is_file(), f"no existe el esquema bruto: {esquema_raw}")
    bytes_brutos = input_csv.read_bytes()
    exigir(bool(bytes_brutos), "el CSV de entrada está vacío")
    hash_bruto = sha256_bytes(bytes_brutos)
    columnas_esperadas = json.loads(esquema_raw.read_text(encoding="utf-8"))["required"]
    try:
        tabla = pd.read_csv(input_csv)
    except Exception as exc:
        raise ErrorContrato(f"no se pudo leer el CSV: {exc}") from exc
    validar_bruto(tabla, columnas_esperadas)
    tabla = derivar_variables(tabla)
    validar_derivadas(tabla)
    _, publico = construir_publico(tabla)
    mapa, resumen_bonos = construir_mapa_bonos(tabla, hash_bruto)
    resultados, descriptiva, _, modelo = analizar(tabla, mapa)

    ruta_publico = raiz_salida / "04_DATOS" / "publicos" / "velocidad_frutas_publico.csv"
    ruta_mapa = raiz_salida / "04_DATOS" / "restringidos" / "mapa_bonificaciones_sintetico.csv"
    directorio_resultados = raiz_salida / "05_ANALISIS" / "resultados"
    ruta_json = directorio_resultados / "resultados_analisis.json"
    ruta_descriptiva = directorio_resultados / "tabla_descriptiva.csv"
    ruta_hash = directorio_resultados / "sha256_bruto.txt"
    directorio_figuras = directorio_resultados / "figuras"

    escribir_bytes(ruta_publico, csv_bytes(publico, float_format="%.3f"))
    escribir_bytes(ruta_mapa, csv_bytes(mapa))
    escribir_bytes(ruta_descriptiva, csv_bytes(descriptiva, float_format="%.12g"))
    escribir_bytes(ruta_hash, f"{hash_bruto}  {input_csv.name}\n".encode("utf-8"))
    rutas_figuras = generar_figuras(tabla, resultados, modelo, directorio_figuras)

    productos = [ruta_publico, ruta_mapa, ruta_descriptiva, ruta_hash, *rutas_figuras]
    resultados["entrada"] = {
        "archivo": input_csv.name,
        "sha256": hash_bruto,
        "bytes": len(bytes_brutos),
    }
    resultados["bonificaciones_sinteticas"] = resumen_bonos
    resultados["productos"] = {
        str(ruta.relative_to(raiz_salida)).replace("\\", "/"): {
            "sha256": hash_archivo(ruta),
            "bytes": ruta.stat().st_size,
        }
        for ruta in productos
    }
    escribir_bytes(
        ruta_json,
        (json.dumps(resultados, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    return {
        "rotulo": ETIQUETA,
        "hash_bruto": hash_bruto,
        "filas_publicas": len(publico),
        "filas_incluidas": int(tabla["incluida"].sum()),
        "parejas_bonificadas": resumen_bonos["parejas_coincidentes"],
        "personas_bonificadas": resumen_bonos["personas_bonificadas"],
        "importe_total_eur": resumen_bonos["importe_total_eur"],
        "resultados_json": str(ruta_json),
    }


def argumentos(argv: list[str] | None = None) -> argparse.Namespace:
    raiz_proyecto = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(
        description="Analiza la SIMULACIÓN DOCENTE de velocidad de frutas sin interacción.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=raiz_proyecto / "04_DATOS" / "sinteticos_raw" / "respuestas_sinteticas_500.csv",
        help="CSV bruto de entrada (por defecto, el sintético del proyecto).",
    )
    parser.add_argument(
        "--raiz-salida",
        type=Path,
        default=raiz_proyecto,
        help="Raíz bajo la que se crean 04_DATOS y 05_ANALISIS.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = argumentos(argv)
    try:
        resumen = ejecutar(args.input.resolve(), args.raiz_salida.resolve())
    except ErrorContrato as exc:
        print(f"ERROR DE CONTRATO: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - red de seguridad de la CLI
        print(f"ERROR INESPERADO ({type(exc).__name__}): {exc}", file=sys.stderr)
        return 1
    print(json.dumps(resumen, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
