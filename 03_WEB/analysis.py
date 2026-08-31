"""Funciones puras para el panel docente de la miniweb.

Las fuentes sintética y recibida se validan y analizan por rutas distintas. Este
módulo nunca concatena ambas y no recibe HMAC, texto abierto ni timestamps.
"""

from __future__ import annotations

import json
import math
import re
import unicodedata
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


VELOCIDADES = (30, 50, 70, 90, 110, 130)
ORDENES = ("naranja_primero", "platano_primero")
COLUMNAS_PUBLICAS_SINTETICAS = (
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
)
CATEGORIAS = (
    "forma",
    "color",
    "fisica",
    "cultura",
    "contraste",
    "azar",
    "sin_clasificar",
)
PATRONES = {
    "forma": re.compile(r"\b(forma|redond\w*|curv\w*|alarg\w*|punta\w*|geometri\w*|siluet\w*)\b"),
    "color": re.compile(r"\b(color|amarill\w*|negro|negra|oscur\w*)\b"),
    "fisica": re.compile(r"\b(peso|pesad\w*|liger\w*|rodar|rued\w*|aerodin\w*|fricci\w*)\b"),
    "cultura": re.compile(r"\b(cultur\w*|costumbre\w*|trafic\w*|carretera\w*|deporte\w*|marca\w*)\b"),
    "contraste": re.compile(r"\b(contraste|compar\w*|diferent\w*|primero|segundo)\b"),
    "azar": re.compile(r"\b(azar|aleatori\w*|intuici\w*|ningun\w*|porque si)\b"),
}


class ErrorAnalisis(ValueError):
    """La fuente no cumple el contrato mínimo del panel."""


def _normalizar_texto(valor: Any) -> str:
    texto = unicodedata.normalize("NFKD", "" if valor is None else str(valor))
    return "".join(c for c in texto if not unicodedata.combining(c)).lower()


def categorizar_motivo(texto: str | None) -> list[str]:
    normalizado = _normalizar_texto(texto).strip()
    if not normalizado:
        return []
    halladas = [nombre for nombre, patron in PATRONES.items() if patron.search(normalizado)]
    return halladas or ["sin_clasificar"]


def _a_booleano(serie: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(serie):
        return serie.astype(bool)
    valores = serie.astype("string").str.strip().str.lower()
    if not valores.isin(["true", "false"]).all():
        raise ErrorAnalisis("la columna 'incluida' debe contener true/false")
    return valores.eq("true")


def _validar_velocidades(tabla: pd.DataFrame) -> None:
    for columna in ("velocidad_primera_kmh", "velocidad_naranja_kmh", "velocidad_platano_kmh"):
        valores = pd.to_numeric(tabla[columna], errors="coerce")
        enteros = valores.notna() & valores.map(lambda valor: math.isfinite(float(valor))) & valores.mod(1).eq(0)
        if not enteros.all() or not set(valores.astype(int).unique()).issubset(VELOCIDADES):
            raise ErrorAnalisis(f"valores inválidos en {columna}")
        tabla[columna] = valores.astype(int)
    for columna in ("confianza_naranja", "confianza_platano"):
        valores = pd.to_numeric(tabla[columna], errors="coerce")
        enteros = valores.notna() & valores.map(lambda valor: math.isfinite(float(valor))) & valores.mod(1).eq(0)
        if not (enteros & valores.between(0, 100)).all():
            raise ErrorAnalisis(f"valores inválidos en {columna}")
        tabla[columna] = valores.astype(int)


def _parsear_categorias(valor: Any, nombre_columna: str) -> list[str]:
    if not isinstance(valor, str):
        raise ErrorAnalisis(f"{nombre_columna} debe ser un array JSON")
    try:
        categorias = json.loads(valor)
    except json.JSONDecodeError as exc:
        raise ErrorAnalisis(f"{nombre_columna} contiene JSON inválido") from exc
    if (
        not isinstance(categorias, list)
        or not all(isinstance(categoria, str) for categoria in categorias)
        or len(categorias) != len(set(categorias))
        or not set(categorias).issubset(CATEGORIAS)
    ):
        raise ErrorAnalisis(f"{nombre_columna} contiene categorías no permitidas o repetidas")
    return categorias


def _validar_tiempos(tabla: pd.DataFrame) -> None:
    for columna in ("tiempo_primera_s", "tiempo_segunda_s"):
        valores = pd.to_numeric(tabla[columna], errors="coerce")
        validos = valores.notna() & valores.map(lambda valor: math.isfinite(float(valor))) & valores.ge(0)
        if not validos.all():
            raise ErrorAnalisis(f"valores inválidos en {columna}")
        tabla[columna] = valores.astype(float)


def _validar_coherencia(tabla: pd.DataFrame) -> None:
    if not tabla["orden"].isin(ORDENES).all():
        raise ErrorAnalisis("orden fuera del contrato")
    esperado_simbolo = tabla["orden"].map(
        {"naranja_primero": "naranja", "platano_primero": "platano"}
    )
    if not tabla["simbolo_primero"].eq(esperado_simbolo).all():
        raise ErrorAnalisis("incoherencia entre orden y simbolo_primero")
    esperado_primera = tabla["velocidad_naranja_kmh"].where(
        tabla["simbolo_primero"].eq("naranja"), tabla["velocidad_platano_kmh"]
    )
    if not tabla["velocidad_primera_kmh"].eq(esperado_primera).all():
        raise ErrorAnalisis("incoherencia entre simbolo_primero y velocidad_primera_kmh")


def cargar_sinteticos(ruta_csv: str | Path) -> pd.DataFrame:
    ruta = Path(ruta_csv)
    if not ruta.is_file():
        raise ErrorAnalisis(f"no se encuentra la copia sintética: {ruta.name}")
    tabla = pd.read_csv(ruta)
    if tuple(tabla.columns) != COLUMNAS_PUBLICAS_SINTETICAS:
        raise ErrorAnalisis("la copia sintética no conserva la lista positiva pública")
    if len(tabla) != 500 or not tabla["registro_id"].is_unique:
        raise ErrorAnalisis("la copia sintética debe contener 500 IDs únicos")
    if not tabla["origen_dato"].eq("sintetico_docente").all():
        raise ErrorAnalisis("la pestaña SINTÉTICA solo admite origen_dato=sintetico_docente")
    _validar_velocidades(tabla)
    _validar_tiempos(tabla)
    _validar_coherencia(tabla)
    ids = tabla["registro_id"].astype("string")
    if not ids.str.fullmatch(r"SIM-[0-9]{6}").all():
        raise ErrorAnalisis("registro_id no cumple el patrón público SIM-000000")
    diferencia = pd.to_numeric(tabla["diferencia_platano_menos_naranja"], errors="coerce")
    esperada = tabla["velocidad_platano_kmh"] - tabla["velocidad_naranja_kmh"]
    if diferencia.isna().any() or not diferencia.eq(esperada).all():
        raise ErrorAnalisis("diferencia_platano_menos_naranja no coincide con las velocidades")
    tabla["categoria_motivo"] = tabla["categoria_motivo"].map(
        lambda valor: _parsear_categorias(valor, "categoria_motivo")
    )
    tabla["incluida"] = _a_booleano(tabla["incluida"])
    esperada_inclusion = tabla["tiempo_primera_s"].ge(2.0) & tabla["tiempo_segunda_s"].ge(2.0)
    if not tabla["incluida"].eq(esperada_inclusion).all():
        raise ErrorAnalisis("incluida no respeta la frontera estricta <2.0")
    motivos_permitidos = {
        "tiempo_primera_menor_2",
        "tiempo_segunda_menor_2",
        "tiempos_ambos_menor_2",
        "incompleto",
        "duplicado_posterior",
    }
    motivos = tabla["motivo_exclusion"]
    if not motivos.loc[tabla["incluida"]].isna().all():
        raise ErrorAnalisis("una fila incluida no puede tener motivo_exclusion")
    if not motivos.loc[~tabla["incluida"]].isin(motivos_permitidos).all():
        raise ErrorAnalisis("una fila excluida requiere un motivo_exclusion permitido")
    if not tabla["version_app"].astype(str).str.fullmatch(
        r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?"
    ).all():
        raise ErrorAnalisis("version_app no cumple el patrón esperado")
    tabla.attrs["fuente"] = "SINTÉTICA — SIMULACIÓN DOCENTE"
    return tabla


def preparar_recibidas(filas: Iterable[dict[str, Any]]) -> pd.DataFrame:
    tabla = pd.DataFrame(list(filas))
    if tabla.empty:
        return tabla
    requeridas = {
        "registro_id",
        "origen_captura",
        "orden",
        "simbolo_primero",
        "velocidad_primera_kmh",
        "velocidad_naranja_kmh",
        "velocidad_platano_kmh",
        "confianza_naranja",
        "confianza_platano",
        "tiempo_primera_s",
        "tiempo_segunda_s",
        "categoria_motivo_json",
        "version_app",
    }
    if set(tabla.columns) != requeridas:
        raise ErrorAnalisis("la vista recibida no coincide con su lista positiva restringida")
    if not tabla["origen_captura"].isin(["respuesta_demo", "respuesta_recibida"]).all():
        raise ErrorAnalisis("la pestaña RECIBIDA contiene un origen inesperado")
    _validar_velocidades(tabla)
    _validar_tiempos(tabla)
    _validar_coherencia(tabla)
    if not tabla["registro_id"].astype("string").is_unique:
        raise ErrorAnalisis("la vista recibida contiene registro_id duplicado")
    tabla["incluida"] = tabla["tiempo_primera_s"].ge(2.0) & tabla["tiempo_segunda_s"].ge(2.0)
    tabla["diferencia_platano_menos_naranja"] = (
        tabla["velocidad_platano_kmh"] - tabla["velocidad_naranja_kmh"]
    ).astype(int)
    tabla["categoria_motivo"] = tabla["categoria_motivo_json"].map(
        lambda valor: _parsear_categorias(valor, "categoria_motivo_json")
    )
    tabla.attrs["fuente"] = "RECIBIDA — RESTRINGIDA, NO MEZCLADA CON SINTÉTICA"
    return tabla


def resumen(tabla: pd.DataFrame) -> dict[str, float | int | None]:
    if tabla.empty:
        return {
            "n_total": 0,
            "n_incluidas": 0,
            "media_primera_naranja": None,
            "media_primera_platano": None,
            "media_naranja": None,
            "media_platano": None,
        }
    if "incluida" not in tabla:
        raise ErrorAnalisis("falta la derivación de inclusión")
    validas = tabla.loc[tabla["incluida"]]
    naranjas = validas.loc[validas["orden"].eq("naranja_primero"), "velocidad_primera_kmh"]
    platanos = validas.loc[validas["orden"].eq("platano_primero"), "velocidad_primera_kmh"]
    return {
        "n_total": int(len(tabla)),
        "n_incluidas": int(len(validas)),
        "media_primera_naranja": float(naranjas.mean()) if len(naranjas) else None,
        "media_primera_platano": float(platanos.mean()) if len(platanos) else None,
        "media_naranja": float(validas["velocidad_naranja_kmh"].mean()) if len(validas) else None,
        "media_platano": float(validas["velocidad_platano_kmh"].mean()) if len(validas) else None,
    }


def figura_distribuciones(tabla: pd.DataFrame, rotulo: str) -> plt.Figure:
    validas = tabla.loc[tabla["incluida"]].copy()
    larga = validas.melt(
        value_vars=["velocidad_naranja_kmh", "velocidad_platano_kmh"],
        var_name="simbolo",
        value_name="velocidad_kmh",
    )
    larga["simbolo"] = larga["simbolo"].map(
        {"velocidad_naranja_kmh": "Naranja", "velocidad_platano_kmh": "Plátano"}
    )
    sns.set_theme(style="whitegrid")
    figura, eje = plt.subplots(figsize=(7.4, 4.2))
    sns.countplot(
        data=larga,
        x="velocidad_kmh",
        hue="simbolo",
        order=list(VELOCIDADES),
        hue_order=["Naranja", "Plátano"],
        palette=["#E07A1F", "#D4B000"],
        ax=eje,
    )
    eje.set(xlabel="Velocidad (km/h)", ylabel="Frecuencia", title=f"{rotulo} · distribuciones")
    figura.tight_layout()
    return figura


def figura_primera_respuesta(tabla: pd.DataFrame, rotulo: str) -> plt.Figure:
    validas = tabla.loc[tabla["incluida"]].copy()
    etiquetas = {
        "naranja_primero": "Naranja primero",
        "platano_primero": "Plátano primero",
    }
    validas["grupo"] = validas["orden"].map(etiquetas)
    sns.set_theme(style="whitegrid")
    figura, eje = plt.subplots(figsize=(7.4, 4.2))
    sns.countplot(
        data=validas,
        x="velocidad_primera_kmh",
        hue="grupo",
        order=list(VELOCIDADES),
        hue_order=["Naranja primero", "Plátano primero"],
        palette=["#E07A1F", "#7768AE"],
        ax=eje,
    )
    eje.set(
        xlabel="Primera velocidad (km/h)",
        ylabel="Frecuencia",
        title=f"{rotulo} · solo primera respuesta",
    )
    figura.tight_layout()
    return figura


def bytes_csv_publico_sintetico(ruta_csv: str | Path) -> bytes:
    """Devuelve la copia exacta tras validarla; no reserializa ni mezcla fuentes."""
    cargar_sinteticos(ruta_csv)
    return Path(ruta_csv).read_bytes()
