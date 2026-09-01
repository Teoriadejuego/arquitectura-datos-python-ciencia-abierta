#!/usr/bin/env python3
"""Detiene la publicación si el repositorio cruza su frontera pública."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_SPEEDS = {30, 50, 70, 90, 110, 130}


def fail(message: str) -> None:
    print(f"FALLO: {message}")
    raise SystemExit(1)


required = [
    "README.md",
    "CITATION.cff",
    "00_PRESENTACION/ARQUITECTURA_DATOS_PROYECCION.pptx",
    "00_CUADERNO_Y_MANUAL/CUADERNO_ESTUDIANTE_FINAL_IMPRIMIR.pdf",
    "04_DATOS/sinteticos_raw/respuestas_sinteticas_500.csv",
    "04_DATOS/publicos/velocidad_frutas_publico.csv",
    "05_ANALISIS/laboratorio_velocidad_frutas.ipynb",
    "03_WEB/app.py",
]
for relative in required:
    if not (ROOT / relative).is_file():
        fail(f"falta {relative}")

forbidden_names = {
    "secrets.toml",
    ".env",
    ".venv",
    "__pycache__",
    "mapa_bonificaciones_sintetico.csv",
}
for path in ROOT.rglob("*"):
    if path.name.casefold() in {name.casefold() for name in forbidden_names}:
        fail(f"archivo o carpeta no publicable: {path.relative_to(ROOT)}")
    if path.is_file() and path.suffix.casefold() in {".sqlite", ".sqlite3", ".db", ".pem", ".key"}:
        fail(f"formato restringido: {path.relative_to(ROOT)}")

raw_path = ROOT / "04_DATOS/sinteticos_raw/respuestas_sinteticas_500.csv"
with raw_path.open(encoding="utf-8", newline="") as fh:
    raw = list(csv.DictReader(fh))

if len(raw) != 500:
    fail(f"el bruto sintético contiene {len(raw)} filas, no 500")
if not all(row["origen_dato"] == "sintetico_docente" for row in raw):
    fail("aparece un origen distinto de sintetico_docente")
if not all(not row["PROLIFIC_PID"] and not row["STUDY_ID"] and not row["SESSION_ID"] for row in raw):
    fail("hay identificadores de plataforma en la capa sintética")

speed_columns = ("velocidad_primera_kmh", "velocidad_naranja_kmh", "velocidad_platano_kmh")
if not all(int(row[column]) in ALLOWED_SPEEDS for row in raw for column in speed_columns):
    fail("aparece una velocidad fuera del contrato")

speeders = [
    row
    for row in raw
    if float(row["tiempo_primera_s"]) < 2.0 or float(row["tiempo_segunda_s"]) < 2.0
]
if len(speeders) != 20:
    fail(f"la regla temporal identifica {len(speeders)} speeders, no 20")

public_path = ROOT / "04_DATOS/publicos/velocidad_frutas_publico.csv"
with public_path.open(encoding="utf-8", newline="") as fh:
    reader = csv.DictReader(fh)
    public_rows = list(reader)
    fields = set(reader.fieldnames or [])

forbidden_fields = {
    "PROLIFIC_PID",
    "STUDY_ID",
    "SESSION_ID",
    "respuesta_abierta",
    "participante_hmac",
    "session_hmac",
    "pair_id",
}
if fields & forbidden_fields:
    fail(f"columnas restringidas en el CSV público: {sorted(fields & forbidden_fields)}")
if len(public_rows) != 500:
    fail(f"el CSV público contiene {len(public_rows)} filas, no 500")

for json_path in ROOT.rglob("*.json"):
    try:
        json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"JSON inválido: {json_path.relative_to(ROOT)} ({exc})")

text_suffixes = {".md", ".txt", ".py", ".toml", ".cff"}
residue_a = "ki" + "ki"
residue_b = "bou" + "ba"
for path in ROOT.rglob("*"):
    if path.is_file() and path.suffix.casefold() in text_suffixes:
        text = path.read_text(encoding="utf-8", errors="ignore").casefold()
        if re.search(rf"\b({residue_a}|{residue_b})\b", text):
            fail(f"residuo del caso anterior: {path.relative_to(ROOT)}")

print("AUDITORÍA PÚBLICA: SUPERADA")
print("500 filas sintéticas · 20 speeders · 0 identificadores · 0 secretos")
sys.exit(0)
