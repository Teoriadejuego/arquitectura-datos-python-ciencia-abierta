"""Persistencia SQLite restringida para la miniweb.

La base recibida es deliberadamente independiente del CSV sintético docente.
Solo almacena HMAC de los identificadores de plataforma, nunca los valores
brutos. Cada cambio de estado se ejecuta dentro de una transacción inmediata.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import re
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from numbers import Integral, Real
from pathlib import Path
from typing import Any, Iterator, Mapping


SEMILLA_ASIGNACION = 20260902
TAMANO_BLOQUE = 10
NUMERO_BLOQUES = 50
CAPACIDAD = TAMANO_BLOQUE * NUMERO_BLOQUES
VELOCIDADES = (30, 50, 70, 90, 110, 130)
ORDENES = ("naranja_primero", "platano_primero")
ESTADOS = ("asignado", "primera_completa", "segunda_completa", "completo")
VERSION_APP = "1.0.0-miniweb"
_HMAC_RE = re.compile(r"^[0-9a-f]{64}$")
_BLOQUEO_INICIALIZACION = threading.Lock()
_RUTAS_INICIALIZADAS: dict[Path, tuple[int, int, int]] = {}


class ErrorAlmacenamiento(RuntimeError):
    """Error controlado y presentable en la interfaz."""


class ConflictoIdempotencia(ErrorAlmacenamiento):
    """Un reenvío intenta modificar una respuesta ya confirmada."""


class ParticipacionDuplicada(ErrorAlmacenamiento):
    """La persona ya está asociada con otra sesión."""


class CupoAgotado(ErrorAlmacenamiento):
    """La secuencia cerrada de 500 asignaciones está agotada."""


@dataclass(frozen=True)
class EstadoRegistro:
    registro_id: str
    indice_asignacion: int
    orden: str
    simbolo_primero: str
    estado: str
    primera_render_utc: str | None
    segunda_render_utc: str | None


def ahora_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def orden_para_indice(indice: int) -> str:
    """Reproduce los 50 bloques permutados de cinco secuencias por brazo."""
    if not 0 <= indice < CAPACIDAD:
        raise CupoAgotado(f"índice fuera de la secuencia cerrada 0..{CAPACIDAD - 1}")
    rng = random.Random(SEMILLA_ASIGNACION)
    bloque_objetivo = indice // TAMANO_BLOQUE
    bloque: list[str] = []
    for _ in range(bloque_objetivo + 1):
        bloque = ["naranja_primero"] * 5 + ["platano_primero"] * 5
        rng.shuffle(bloque)
    return bloque[indice % TAMANO_BLOQUE]


def secuencia_completa() -> list[str]:
    return [orden_para_indice(i) for i in range(CAPACIDAD)]


def _validar_hmac(nombre: str, valor: str) -> None:
    if not _HMAC_RE.fullmatch(valor):
        raise ErrorAlmacenamiento(f"{nombre} no es un HMAC SHA-256 hexadecimal válido")


def _validar_timestamp(nombre: str, valor: str) -> None:
    try:
        datetime.fromisoformat(valor.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ErrorAlmacenamiento(f"timestamp inválido en {nombre}") from exc


def _estado_desde_fila(fila: sqlite3.Row) -> EstadoRegistro:
    return EstadoRegistro(
        registro_id=str(fila["registro_id"]),
        indice_asignacion=int(fila["indice_asignacion"]),
        orden=str(fila["orden"]),
        simbolo_primero=str(fila["simbolo_primero"]),
        estado=str(fila["estado"]),
        primera_render_utc=fila["primera_render_utc"],
        segunda_render_utc=fila["segunda_render_utc"],
    )


def _conectar(ruta_bd: Path) -> sqlite3.Connection:
    ruta_bd.parent.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(str(ruta_bd), timeout=15.0, isolation_level=None)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    conexion.execute("PRAGMA busy_timeout = 15000")
    conexion.execute("PRAGMA synchronous = FULL")
    return conexion


def _firma_archivo(ruta_bd: Path) -> tuple[int, int, int] | None:
    """Identifica el archivo sin depender de tamaño o fecha de modificación."""
    try:
        estado = ruta_bd.stat()
    except FileNotFoundError:
        return None
    return (int(estado.st_dev), int(estado.st_ino), int(estado.st_ctime_ns))


def _configurar_wal(ruta_bd: Path) -> None:
    """Activa WAL una sola vez, con reintento ante otro inicializador."""
    ultimo_error: sqlite3.OperationalError | None = None
    for intento in range(8):
        conexion = sqlite3.connect(str(ruta_bd), timeout=15.0, isolation_level=None)
        try:
            conexion.execute("PRAGMA busy_timeout = 15000")
            modo = conexion.execute("PRAGMA journal_mode = WAL").fetchone()
            if modo is None or str(modo[0]).casefold() != "wal":
                raise sqlite3.OperationalError("SQLite no confirmó journal_mode=WAL")
            return
        except sqlite3.OperationalError as exc:
            if "locked" not in str(exc).casefold():
                raise
            ultimo_error = exc
        finally:
            conexion.close()
        time.sleep(0.05 * (intento + 1))
    if ultimo_error is not None:
        raise ultimo_error


@contextmanager
def _transaccion(ruta_bd: Path) -> Iterator[sqlite3.Connection]:
    conexion = _conectar(ruta_bd)
    try:
        conexion.execute("BEGIN IMMEDIATE")
        yield conexion
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def inicializar_bd(ruta_bd: str | Path) -> None:
    ruta = Path(ruta_bd).resolve()
    try:
        # `PRAGMA journal_mode=WAL` requiere un bloqueo exclusivo breve. Si se
        # ejecuta en cada conexión, dos primeras solicitudes pueden colisionar.
        # Serializamos la creación dentro del proceso, reintentamos el WAL ante
        # otro proceso y recordamos la identidad del archivo ya preparado.
        with _BLOQUEO_INICIALIZACION:
            firma_actual = _firma_archivo(ruta)
            if firma_actual is not None and _RUTAS_INICIALIZADAS.get(ruta) == firma_actual:
                return
            _configurar_wal(ruta)
            with _transaccion(ruta) as conexion:
                conexion.execute(
                """
                CREATE TABLE IF NOT EXISTS estado_asignacion (
                    clave TEXT PRIMARY KEY,
                    valor_entero INTEGER NOT NULL CHECK (valor_entero >= 0)
                )
                """
            )
                conexion.execute(
                    "INSERT OR IGNORE INTO estado_asignacion(clave, valor_entero) VALUES ('siguiente_indice', 0)"
                )
                conexion.execute(
                    f"""
                CREATE TABLE IF NOT EXISTS respuestas (
                    registro_id TEXT PRIMARY KEY,
                    participant_hmac TEXT NOT NULL UNIQUE CHECK (length(participant_hmac) = 64),
                    study_hmac TEXT NOT NULL CHECK (length(study_hmac) = 64),
                    session_hmac TEXT NOT NULL UNIQUE CHECK (length(session_hmac) = 64),
                    hmac_version TEXT NOT NULL,
                    origen_captura TEXT NOT NULL CHECK (origen_captura IN ('respuesta_demo', 'respuesta_recibida')),
                    indice_asignacion INTEGER NOT NULL UNIQUE CHECK (indice_asignacion >= 0 AND indice_asignacion < {CAPACIDAD}),
                    orden TEXT NOT NULL CHECK (orden IN ('naranja_primero', 'platano_primero')),
                    simbolo_primero TEXT NOT NULL CHECK (simbolo_primero IN ('naranja', 'platano')),
                    estado TEXT NOT NULL CHECK (estado IN ('asignado', 'primera_completa', 'segunda_completa', 'completo')),
                    consentimiento INTEGER NOT NULL CHECK (consentimiento = 1),
                    edad_18_mas INTEGER NOT NULL CHECK (edad_18_mas = 1),
                    permiso_vigente INTEGER NOT NULL CHECK (permiso_vigente = 1),
                    comprende_espanol INTEGER NOT NULL CHECK (comprende_espanol = 1),
                    no_conduce_ahora INTEGER NOT NULL CHECK (no_conduce_ahora = 1),
                    velocidad_primera_kmh INTEGER CHECK (velocidad_primera_kmh IN {VELOCIDADES}),
                    velocidad_naranja_kmh INTEGER CHECK (velocidad_naranja_kmh IN {VELOCIDADES}),
                    velocidad_platano_kmh INTEGER CHECK (velocidad_platano_kmh IN {VELOCIDADES}),
                    confianza_naranja INTEGER CHECK (confianza_naranja BETWEEN 0 AND 100),
                    confianza_platano INTEGER CHECK (confianza_platano BETWEEN 0 AND 100),
                    tiempo_primera_s REAL CHECK (tiempo_primera_s >= 0),
                    tiempo_segunda_s REAL CHECK (tiempo_segunda_s >= 0),
                    respuesta_abierta TEXT,
                    categoria_motivo_json TEXT,
                    inicio_utc TEXT NOT NULL,
                    primera_render_utc TEXT,
                    primera_aceptada_utc TEXT,
                    segunda_render_utc TEXT,
                    segunda_aceptada_utc TEXT,
                    fin_utc TEXT,
                    payload_sha256 TEXT,
                    version_app TEXT NOT NULL,
                    CHECK (
                        (orden = 'naranja_primero' AND simbolo_primero = 'naranja') OR
                        (orden = 'platano_primero' AND simbolo_primero = 'platano')
                    ),
                    CHECK (
                        velocidad_primera_kmh IS NULL OR
                        (simbolo_primero = 'naranja' AND velocidad_primera_kmh = velocidad_naranja_kmh) OR
                        (simbolo_primero = 'platano' AND velocidad_primera_kmh = velocidad_platano_kmh)
                    )
                )
                    """
                )
            firma_inicializada = _firma_archivo(ruta)
            if firma_inicializada is None:
                raise sqlite3.OperationalError("SQLite no creó el archivo esperado")
            _RUTAS_INICIALIZADAS[ruta] = firma_inicializada
    except sqlite3.Error as exc:
        raise ErrorAlmacenamiento(f"no se pudo inicializar SQLite: {exc}") from exc


def obtener_estado_por_sesion(ruta_bd: str | Path, session_hmac: str) -> EstadoRegistro | None:
    _validar_hmac("session_hmac", session_hmac)
    inicializar_bd(ruta_bd)
    try:
        conexion = _conectar(Path(ruta_bd))
        try:
            fila = conexion.execute(
                """
                SELECT registro_id, indice_asignacion, orden, simbolo_primero, estado,
                       primera_render_utc, segunda_render_utc
                FROM respuestas WHERE session_hmac = ?
                """,
                (session_hmac,),
            ).fetchone()
        finally:
            conexion.close()
    except sqlite3.Error as exc:
        raise ErrorAlmacenamiento(f"no se pudo consultar la sesión: {exc}") from exc
    return _estado_desde_fila(fila) if fila is not None else None


def obtener_o_crear_asignacion(
    ruta_bd: str | Path,
    *,
    participant_hmac: str,
    study_hmac: str,
    session_hmac: str,
    hmac_version: str,
    origen_captura: str,
    inicio_utc: str,
) -> EstadoRegistro:
    for nombre, valor in (
        ("participant_hmac", participant_hmac),
        ("study_hmac", study_hmac),
        ("session_hmac", session_hmac),
    ):
        _validar_hmac(nombre, valor)
    if not hmac_version.strip() or len(hmac_version) > 64:
        raise ErrorAlmacenamiento("hmac_version es obligatorio y debe tener como máximo 64 caracteres")
    if origen_captura not in {"respuesta_demo", "respuesta_recibida"}:
        raise ErrorAlmacenamiento("origen_captura no permitido")
    _validar_timestamp("inicio_utc", inicio_utc)
    inicializar_bd(ruta_bd)
    ruta = Path(ruta_bd)
    try:
        with _transaccion(ruta) as conexion:
            por_sesion = conexion.execute(
                "SELECT * FROM respuestas WHERE session_hmac = ?", (session_hmac,)
            ).fetchone()
            if por_sesion is not None:
                if (
                    por_sesion["participant_hmac"] != participant_hmac
                    or por_sesion["study_hmac"] != study_hmac
                    or por_sesion["hmac_version"] != hmac_version
                ):
                    raise ConflictoIdempotencia("la sesión ya está vinculada con otra identidad pseudonimizada")
                return _estado_desde_fila(por_sesion)

            por_participante = conexion.execute(
                "SELECT * FROM respuestas WHERE participant_hmac = ?", (participant_hmac,)
            ).fetchone()
            if por_participante is not None:
                raise ParticipacionDuplicada("esta participación ya está vinculada con otra sesión")

            contador = conexion.execute(
                "SELECT valor_entero FROM estado_asignacion WHERE clave = 'siguiente_indice'"
            ).fetchone()
            if contador is None:
                raise ErrorAlmacenamiento("falta el contador transaccional de asignaciones")
            indice = int(contador["valor_entero"])
            if indice >= CAPACIDAD:
                raise CupoAgotado("se alcanzó la capacidad cerrada de 500 asignaciones")
            orden = orden_para_indice(indice)
            simbolo = "naranja" if orden == "naranja_primero" else "platano"
            registro_id = "REC-" + uuid.uuid4().hex.upper()
            conexion.execute(
                "UPDATE estado_asignacion SET valor_entero = ? WHERE clave = 'siguiente_indice'",
                (indice + 1,),
            )
            conexion.execute(
                """
                INSERT INTO respuestas (
                    registro_id, participant_hmac, study_hmac, session_hmac, hmac_version,
                    origen_captura, indice_asignacion, orden, simbolo_primero, estado,
                    consentimiento, edad_18_mas, permiso_vigente, comprende_espanol,
                    no_conduce_ahora, inicio_utc, version_app
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'asignado', 1, 1, 1, 1, 1, ?, ?)
                """,
                (
                    registro_id,
                    participant_hmac,
                    study_hmac,
                    session_hmac,
                    hmac_version,
                    origen_captura,
                    indice,
                    orden,
                    simbolo,
                    inicio_utc,
                    VERSION_APP,
                ),
            )
            fila = conexion.execute("SELECT * FROM respuestas WHERE registro_id = ?", (registro_id,)).fetchone()
            if fila is None:
                raise ErrorAlmacenamiento("la asignación no pudo releerse antes del commit")
            return _estado_desde_fila(fila)
    except ErrorAlmacenamiento:
        raise
    except sqlite3.IntegrityError as exc:
        raise ConflictoIdempotencia(f"conflicto de unicidad al reservar la asignación: {exc}") from exc
    except sqlite3.Error as exc:
        raise ErrorAlmacenamiento(f"falló la reserva atómica de la asignación: {exc}") from exc


def _marcar_render(ruta_bd: str | Path, session_hmac: str, numero: int, timestamp_utc: str) -> EstadoRegistro:
    _validar_hmac("session_hmac", session_hmac)
    _validar_timestamp("render_utc", timestamp_utc)
    if numero not in (1, 2):
        raise ErrorAlmacenamiento("el número de pantalla debe ser 1 o 2")
    inicializar_bd(ruta_bd)
    columna = "primera_render_utc" if numero == 1 else "segunda_render_utc"
    estado_requerido = "asignado" if numero == 1 else "primera_completa"
    ruta = Path(ruta_bd)
    try:
        with _transaccion(ruta) as conexion:
            fila = conexion.execute("SELECT * FROM respuestas WHERE session_hmac = ?", (session_hmac,)).fetchone()
            if fila is None:
                raise ErrorAlmacenamiento("no existe una asignación para esta sesión")
            if fila[columna] is None:
                if fila["estado"] != estado_requerido:
                    raise ConflictoIdempotencia("la secuencia de pantallas no permite marcar este render")
                conexion.execute(
                    f"UPDATE respuestas SET {columna} = ? WHERE session_hmac = ? AND {columna} IS NULL",
                    (timestamp_utc, session_hmac),
                )
            actualizada = conexion.execute("SELECT * FROM respuestas WHERE session_hmac = ?", (session_hmac,)).fetchone()
            return _estado_desde_fila(actualizada)
    except ErrorAlmacenamiento:
        raise
    except sqlite3.Error as exc:
        raise ErrorAlmacenamiento(f"no se pudo confirmar el render de la pantalla {numero}: {exc}") from exc


def marcar_render_primera(ruta_bd: str | Path, session_hmac: str, timestamp_utc: str) -> EstadoRegistro:
    return _marcar_render(ruta_bd, session_hmac, 1, timestamp_utc)


def marcar_render_segunda(ruta_bd: str | Path, session_hmac: str, timestamp_utc: str) -> EstadoRegistro:
    return _marcar_render(ruta_bd, session_hmac, 2, timestamp_utc)


def _validar_eleccion(velocidad: int, confianza: int, tiempo_s: float) -> None:
    if (
        isinstance(velocidad, bool)
        or not isinstance(velocidad, Integral)
        or int(velocidad) not in VELOCIDADES
    ):
        raise ErrorAlmacenamiento(f"velocidad fuera de las categorías permitidas: {velocidad}")
    if (
        isinstance(confianza, bool)
        or not isinstance(confianza, Integral)
        or not 0 <= int(confianza) <= 100
    ):
        raise ErrorAlmacenamiento("la confianza debe ser un entero de 0 a 100")
    if (
        isinstance(tiempo_s, bool)
        or not isinstance(tiempo_s, Real)
        or not math.isfinite(float(tiempo_s))
        or not 0 <= float(tiempo_s) < 86_400
    ):
        raise ErrorAlmacenamiento("el tiempo debe ser numérico, no negativo y menor de 24 horas")


def _guardar_eleccion(
    ruta_bd: str | Path,
    *,
    session_hmac: str,
    numero: int,
    velocidad: int,
    confianza: int,
    tiempo_s: float,
    aceptada_utc: str,
) -> EstadoRegistro:
    _validar_hmac("session_hmac", session_hmac)
    _validar_eleccion(velocidad, confianza, tiempo_s)
    _validar_timestamp("aceptada_utc", aceptada_utc)
    inicializar_bd(ruta_bd)
    ruta = Path(ruta_bd)
    try:
        with _transaccion(ruta) as conexion:
            fila = conexion.execute("SELECT * FROM respuestas WHERE session_hmac = ?", (session_hmac,)).fetchone()
            if fila is None:
                raise ErrorAlmacenamiento("no existe una asignación para esta sesión")
            if numero == 1:
                simbolo = str(fila["simbolo_primero"])
                estado_previo, estado_nuevo = "asignado", "primera_completa"
                columna_tiempo, columna_aceptada = "tiempo_primera_s", "primera_aceptada_utc"
            elif numero == 2:
                simbolo = "platano" if fila["simbolo_primero"] == "naranja" else "naranja"
                estado_previo, estado_nuevo = "primera_completa", "segunda_completa"
                columna_tiempo, columna_aceptada = "tiempo_segunda_s", "segunda_aceptada_utc"
            else:
                raise ErrorAlmacenamiento("el número de respuesta debe ser 1 o 2")
            columna_velocidad = f"velocidad_{simbolo}_kmh"
            columna_confianza = f"confianza_{simbolo}"
            if fila["estado"] != estado_previo:
                ya_guardada = (
                    fila[columna_velocidad] == int(velocidad)
                    and fila[columna_confianza] == int(confianza)
                    and fila[columna_tiempo] is not None
                    and abs(float(fila[columna_tiempo]) - round(float(tiempo_s), 3)) < 0.0005
                )
                if ya_guardada and ESTADOS.index(str(fila["estado"])) >= ESTADOS.index(estado_nuevo):
                    return _estado_desde_fila(fila)
                raise ConflictoIdempotencia("una respuesta ya confirmada no puede modificarse")
            columna_render = "primera_render_utc" if numero == 1 else "segunda_render_utc"
            if fila[columna_render] is None:
                raise ErrorAlmacenamiento("el estímulo no consta como renderizado")
            asignacion_primera = ", velocidad_primera_kmh = ?" if numero == 1 else ""
            parametros: list[Any] = [
                int(velocidad),
                int(confianza),
                round(float(tiempo_s), 3),
                aceptada_utc,
                estado_nuevo,
            ]
            if numero == 1:
                parametros.append(int(velocidad))
            parametros.extend([session_hmac, estado_previo])
            cursor = conexion.execute(
                f"""
                UPDATE respuestas
                SET {columna_velocidad} = ?, {columna_confianza} = ?,
                    {columna_tiempo} = ?, {columna_aceptada} = ?, estado = ?
                    {asignacion_primera}
                WHERE session_hmac = ? AND estado = ?
                """,
                parametros,
            )
            if cursor.rowcount != 1:
                raise ConflictoIdempotencia("la respuesta no pudo confirmarse una sola vez")
            actualizada = conexion.execute("SELECT * FROM respuestas WHERE session_hmac = ?", (session_hmac,)).fetchone()
            return _estado_desde_fila(actualizada)
    except ErrorAlmacenamiento:
        raise
    except sqlite3.Error as exc:
        raise ErrorAlmacenamiento(f"no se pudo guardar la respuesta {numero}: {exc}") from exc


def guardar_primera_respuesta(
    ruta_bd: str | Path,
    *,
    session_hmac: str,
    velocidad: int,
    confianza: int,
    tiempo_s: float,
    aceptada_utc: str,
) -> EstadoRegistro:
    return _guardar_eleccion(
        ruta_bd,
        session_hmac=session_hmac,
        numero=1,
        velocidad=velocidad,
        confianza=confianza,
        tiempo_s=tiempo_s,
        aceptada_utc=aceptada_utc,
    )


def guardar_segunda_respuesta(
    ruta_bd: str | Path,
    *,
    session_hmac: str,
    velocidad: int,
    confianza: int,
    tiempo_s: float,
    aceptada_utc: str,
) -> EstadoRegistro:
    return _guardar_eleccion(
        ruta_bd,
        session_hmac=session_hmac,
        numero=2,
        velocidad=velocidad,
        confianza=confianza,
        tiempo_s=tiempo_s,
        aceptada_utc=aceptada_utc,
    )


def finalizar_registro(
    ruta_bd: str | Path,
    *,
    session_hmac: str,
    respuesta_abierta: str,
    categorias_motivo: list[str],
    fin_utc: str,
) -> EstadoRegistro:
    _validar_hmac("session_hmac", session_hmac)
    _validar_timestamp("fin_utc", fin_utc)
    texto = respuesta_abierta.strip()
    if len(texto) > 1000:
        raise ErrorAlmacenamiento("la explicación supera 1000 caracteres")
    categorias_permitidas = {
        "forma", "color", "fisica", "cultura", "contraste", "azar", "sin_clasificar"
    }
    if len(categorias_motivo) != len(set(categorias_motivo)) or not set(categorias_motivo).issubset(categorias_permitidas):
        raise ErrorAlmacenamiento("las categorías derivadas del motivo no son válidas")
    inicializar_bd(ruta_bd)
    ruta = Path(ruta_bd)
    try:
        with _transaccion(ruta) as conexion:
            fila = conexion.execute("SELECT * FROM respuestas WHERE session_hmac = ?", (session_hmac,)).fetchone()
            if fila is None:
                raise ErrorAlmacenamiento("no existe una asignación para esta sesión")
            contenido_hash: Mapping[str, Any] = {
                "registro_id": fila["registro_id"],
                "orden": fila["orden"],
                "velocidad_naranja_kmh": fila["velocidad_naranja_kmh"],
                "velocidad_platano_kmh": fila["velocidad_platano_kmh"],
                "confianza_naranja": fila["confianza_naranja"],
                "confianza_platano": fila["confianza_platano"],
                "tiempo_primera_s": fila["tiempo_primera_s"],
                "tiempo_segunda_s": fila["tiempo_segunda_s"],
                "respuesta_abierta": texto,
                "categorias_motivo": categorias_motivo,
            }
            payload_sha256 = hashlib.sha256(
                json.dumps(contenido_hash, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            if fila["estado"] == "completo":
                if fila["payload_sha256"] != payload_sha256:
                    raise ConflictoIdempotencia("el registro ya se completó con otro contenido")
                return _estado_desde_fila(fila)
            if fila["estado"] != "segunda_completa":
                raise ConflictoIdempotencia("no se puede finalizar antes de confirmar ambas señales")
            cursor = conexion.execute(
                """
                UPDATE respuestas
                SET respuesta_abierta = ?, categoria_motivo_json = ?, fin_utc = ?,
                    payload_sha256 = ?, estado = 'completo'
                WHERE session_hmac = ? AND estado = 'segunda_completa'
                """,
                (
                    texto or None,
                    json.dumps(categorias_motivo, ensure_ascii=False, separators=(",", ":")),
                    fin_utc,
                    payload_sha256,
                    session_hmac,
                ),
            )
            if cursor.rowcount != 1:
                raise ConflictoIdempotencia("el envío final no pudo confirmarse una sola vez")
            actualizada = conexion.execute("SELECT * FROM respuestas WHERE session_hmac = ?", (session_hmac,)).fetchone()
            return _estado_desde_fila(actualizada)
    except ErrorAlmacenamiento:
        raise
    except sqlite3.Error as exc:
        raise ErrorAlmacenamiento(f"falló el guardado final atómico: {exc}") from exc


def listar_respuestas_publicables(ruta_bd: str | Path) -> list[dict[str, Any]]:
    """Lista positiva: excluye HMAC, texto abierto y timestamps exactos."""
    inicializar_bd(ruta_bd)
    columnas = (
        "registro_id, origen_captura, orden, simbolo_primero, velocidad_primera_kmh, "
        "velocidad_naranja_kmh, velocidad_platano_kmh, confianza_naranja, confianza_platano, "
        "tiempo_primera_s, tiempo_segunda_s, categoria_motivo_json, version_app"
    )
    try:
        conexion = _conectar(Path(ruta_bd))
        try:
            filas = conexion.execute(
                f"SELECT {columnas} FROM respuestas WHERE estado = 'completo' ORDER BY indice_asignacion"
            ).fetchall()
        finally:
            conexion.close()
    except sqlite3.Error as exc:
        raise ErrorAlmacenamiento(f"no se pudo preparar la vista pública recibida: {exc}") from exc
    return [dict(fila) for fila in filas]


def resumen_restringido(ruta_bd: str | Path) -> dict[str, int]:
    """Solo recuentos; no devuelve identificadores ni texto."""
    inicializar_bd(ruta_bd)
    try:
        conexion = _conectar(Path(ruta_bd))
        try:
            filas = conexion.execute(
                "SELECT origen_captura, estado, COUNT(*) AS n FROM respuestas GROUP BY origen_captura, estado"
            ).fetchall()
        finally:
            conexion.close()
    except sqlite3.Error as exc:
        raise ErrorAlmacenamiento(f"no se pudo resumir la base recibida: {exc}") from exc
    salida: dict[str, int] = {}
    for fila in filas:
        salida[f"{fila['origen_captura']}:{fila['estado']}"] = int(fila["n"])
    return salida
