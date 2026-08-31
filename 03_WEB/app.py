"""Miniweb Streamlit de «La velocidad de las frutas».

El modo predeterminado es una demostración local. La captura live y el panel
docente necesitan configuración explícita del servidor; un parámetro de URL no
concede por sí mismo privilegios.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re
import secrets
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import matplotlib.pyplot as plt
import streamlit as st

import analysis
import storage


BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
CSV_SINTETICO = DATA_DIR / "velocidad_frutas_publico.csv"
VELOCIDADES = storage.VELOCIDADES
ETAPAS = {
    "informacion": 0.05,
    "escenario": 0.22,
    "primera": 0.43,
    "segunda": 0.64,
    "explicacion": 0.82,
    "debriefing": 1.0,
    "rechazo": 0.0,
    "cierre": 1.0,
}
PATRON_ID = re.compile(r"^[A-Za-z0-9_-]{3,256}$")
PATRON_TOKEN_DEMO = re.compile(r"^[A-Za-z0-9_-]{20,128}$")
SECRETO_DEMO_LOCAL = "solo-demo-local-no-usar-en-live-2026"


class ErrorConfiguracion(RuntimeError):
    """Configuración ausente o insegura."""


def leer_config(nombre: str, predeterminado: str | None = None) -> str | None:
    valor_entorno = os.environ.get(nombre)
    if valor_entorno is not None:
        return str(valor_entorno)
    try:
        if nombre in st.secrets:
            return str(st.secrets[nombre])
    except Exception:
        pass
    return predeterminado


def config_booleana(nombre: str, predeterminado: bool = False) -> bool:
    valor = leer_config(nombre)
    if valor is None:
        return predeterminado
    return valor.strip().lower() in {"1", "true", "sí", "si", "yes", "on"}


def parametro_unico(nombre: str, *, obligatorio: bool = False) -> str | None:
    try:
        valores = list(st.query_params.get_all(nombre))
    except Exception:
        valor = st.query_params.get(nombre)
        valores = [] if valor is None else [valor]
    if len(valores) > 1:
        raise ErrorConfiguracion(f"el parámetro {nombre} aparece más de una vez")
    if not valores:
        if obligatorio:
            raise ErrorConfiguracion(f"falta el parámetro obligatorio {nombre}")
        return None
    valor = str(valores[0]).strip()
    if obligatorio and not valor:
        raise ErrorConfiguracion(f"el parámetro {nombre} está vacío")
    return valor or None


def modo_solicitado() -> str:
    modo = (parametro_unico("modo") or "demo").lower()
    if modo not in {"demo", "live", "docente"}:
        raise ErrorConfiguracion("modo desconocido; use demo, live o docente")
    return modo


def generar_hmac(secreto: str, dominio: str, valor: str) -> str:
    limpio = valor.strip()
    if not limpio:
        raise ErrorConfiguracion(f"{dominio} no puede estar vacío")
    return hmac.new(
        secreto.encode("utf-8"),
        f"{dominio}:{limpio}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _validar_id_plataforma(nombre: str, valor: str | None) -> str:
    if valor is None or not PATRON_ID.fullmatch(valor):
        raise ErrorConfiguracion(
            f"{nombre} falta o contiene caracteres no permitidos; no se ha iniciado la tarea"
        )
    return valor


def _url_finalizacion_valida(valor: str | None) -> bool:
    if not valor or "[" in valor or "]" in valor or "REEMPLACE" in valor.upper():
        return False
    partes = urlparse(valor)
    return (
        partes.scheme == "https"
        and partes.netloc == "app.prolific.com"
        and partes.path == "/submissions/complete"
        and partes.query.startswith("cc=")
        and len(partes.query) > 3
    )


def identidad_hmac(modo: str) -> dict[str, str]:
    """Transforma IDs inmediatamente y congela solo los HMAC en la sesión."""
    if modo == "live":
        if not config_booleana("LIVE_ENABLED", False):
            raise ErrorConfiguracion(
                "la captura live está deshabilitada en el servidor; el parámetro URL no puede activarla"
            )
        secreto_hmac = leer_config("HMAC_SECRET")
        if (
            secreto_hmac is None
            or len(secreto_hmac.encode("utf-8")) < 32
            or "REEMPLACE" in secreto_hmac.upper()
        ):
            raise ErrorConfiguracion("live requiere HMAC_SECRET externo de al menos 32 bytes")
        version = (leer_config("HMAC_VERSION") or "").strip()
        if not version:
            raise ErrorConfiguracion("live requiere HMAC_VERSION estable")
        completion_url = leer_config("PROLIFIC_COMPLETION_URL")
        if not _url_finalizacion_valida(completion_url):
            raise ErrorConfiguracion("live requiere una URL de finalización Prolific válida")
        soporte = (leer_config("SUPPORT_EMAIL") or "").strip()
        if "@" not in soporte or "[" in soporte or "example." in soporte.lower():
            raise ErrorConfiguracion("live requiere SUPPORT_EMAIL institucional")
        raw = {
            "PROLIFIC_PID": _validar_id_plataforma(
                "PROLIFIC_PID", parametro_unico("PROLIFIC_PID", obligatorio=True)
            ),
            "STUDY_ID": _validar_id_plataforma(
                "STUDY_ID", parametro_unico("STUDY_ID", obligatorio=True)
            ),
            "SESSION_ID": _validar_id_plataforma(
                "SESSION_ID", parametro_unico("SESSION_ID", obligatorio=True)
            ),
        }
        identidad = {
            "participant_hmac": generar_hmac(secreto_hmac, "PROLIFIC_PID", raw["PROLIFIC_PID"]),
            "study_hmac": generar_hmac(secreto_hmac, "STUDY_ID", raw["STUDY_ID"]),
            "session_hmac": generar_hmac(secreto_hmac, "SESSION_ID", raw["SESSION_ID"]),
            "hmac_version": version,
            "origen_captura": "respuesta_recibida",
        }
        del raw
    elif modo == "demo":
        token = parametro_unico("demo_session")
        if token is None:
            st.query_params["modo"] = "demo"
            st.query_params["demo_session"] = secrets.token_urlsafe(24)
            st.rerun()
        if not PATRON_TOKEN_DEMO.fullmatch(token):
            raise ErrorConfiguracion("demo_session no es un token local válido")
        secreto_demo = leer_config("DEMO_HMAC_SECRET", SECRETO_DEMO_LOCAL) or SECRETO_DEMO_LOCAL
        identidad = {
            "participant_hmac": generar_hmac(secreto_demo, "DEMO_PARTICIPANT", token),
            "study_hmac": generar_hmac(secreto_demo, "DEMO_STUDY", "MINIWEB-DEMO-LOCAL"),
            "session_hmac": generar_hmac(secreto_demo, "DEMO_SESSION", token),
            "hmac_version": "demo-v1",
            "origen_captura": "respuesta_demo",
        }
    else:
        raise ErrorConfiguracion("el panel docente no usa identidad de participante")

    congelada = st.session_state.get("_identidad_hmac")
    if congelada is not None and congelada != identidad:
        raise ErrorConfiguracion("la identidad de la URL cambió durante la sesión; recargue desde el enlace original")
    st.session_state["_identidad_hmac"] = identidad
    return identidad


def ruta_bd(modo: str) -> Path:
    configurada = leer_config("DATABASE_PATH", "data/respuestas_recibidas.sqlite3")
    ruta = Path(configurada or "data/respuestas_recibidas.sqlite3")
    if not ruta.is_absolute():
        ruta = (BASE_DIR / ruta).resolve()
    if modo == "live" and ruta.is_relative_to(BASE_DIR):
        raise ErrorConfiguracion(
            "live exige DATABASE_PATH absoluto fuera del código; SQLite local sigue sin ser persistencia de producción"
        )
    return ruta


def verificar_password_docente(password: str, especificacion: str | None) -> bool:
    """Comprueba pbkdf2_sha256$iteraciones$salt_hex$digest_hex."""
    if not password or not especificacion:
        return False
    try:
        algoritmo, iteraciones_txt, salt_hex, esperado_hex = especificacion.split("$", 3)
        iteraciones = int(iteraciones_txt)
        if algoritmo != "pbkdf2_sha256" or not 100_000 <= iteraciones <= 2_000_000:
            return False
        salt = bytes.fromhex(salt_hex)
        esperado = bytes.fromhex(esperado_hex)
        calculado = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iteraciones)
        return hmac.compare_digest(calculado, esperado)
    except (TypeError, ValueError):
        return False


def configurar_pagina() -> None:
    st.set_page_config(
        page_title="La velocidad de las frutas",
        page_icon="🍊",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    st.markdown(
        """
        <style>
        :root { --tinta: #18332f; --verde: #1f6f5f; --crema: #fffaf0; --naranja: #df741c; }
        .stApp { background: linear-gradient(180deg, #fffdf8 0%, #f6fbf8 100%); color: var(--tinta); }
        .block-container { max-width: 860px; padding-top: 2.2rem; padding-bottom: 4rem; }
        .vf-banner { border-left: 5px solid var(--naranja); background: #fff4df; padding: .8rem 1rem;
                     border-radius: .45rem; margin: .3rem 0 1.2rem; }
        .vf-stimulus { display: flex; justify-content: center; margin: 1.4rem auto 1.7rem; }
        .vf-stimulus img { width: min(420px, 78vw); height: auto; }
        .vf-note { color: #455a55; font-size: .92rem; }
        [data-testid="stForm"] { background: rgba(255,255,255,.76); border: 1px solid #d8e5df;
                                 padding: 1rem 1.2rem; border-radius: .75rem; }
        .stButton > button, .stDownloadButton > button { border-radius: 999px; font-weight: 650; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def cabecera_participante(modo: str) -> None:
    st.title("¿Qué velocidad tiene una fruta?")
    if modo == "demo":
        st.markdown(
            '<div class="vf-banner"><strong>DEMO LOCAL</strong> · Esta respuesta se guarda en una '
            "SQLite recibida separada y no se incorpora a los 500 registros sintéticos.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="vf-banner"><strong>CAPTURA RECIBIDA</strong> · Entorno live habilitado '
            "explícitamente por el servidor.</div>",
            unsafe_allow_html=True,
        )
    etapa = st.session_state.get("_etapa", "informacion")
    if etapa not in {"rechazo", "cierre"}:
        st.progress(ETAPAS.get(etapa, 0.0), text="Progreso de la tarea")


def svg_embebido(simbolo: str) -> None:
    ruta = ASSETS_DIR / f"senal_{simbolo}.svg"
    if not ruta.is_file():
        st.error("No se encuentra el estímulo controlado. No se ha guardado esta pantalla.")
        st.stop()
    textos_alt = {
        "naranja": "Señal circular blanca con borde rojo y una silueta negra de naranja centrada.",
        "platano": "Señal circular blanca con borde rojo y una silueta negra de plátano curvado centrada.",
    }
    datos = base64.b64encode(ruta.read_bytes()).decode("ascii")
    st.markdown(
        f'<div class="vf-stimulus"><img src="data:image/svg+xml;base64,{datos}" '
        f'alt="{textos_alt[simbolo]}"></div>',
        unsafe_allow_html=True,
    )


def _contacto() -> str:
    return leer_config("SUPPORT_EMAIL", "[CORREO INSTITUCIONAL]") or "[CORREO INSTITUCIONAL]"


def mostrar_informacion() -> None:
    st.subheader("Información y consentimiento")
    st.markdown(
        """
        Le invitamos a un estudio breve sobre cómo interpretamos símbolos nuevos. Verá una
        naranja y un plátano, uno después del otro, y asignará una velocidad a cada símbolo.
        La tarea dura aproximadamente cuatro minutos.

        **No responda mientras conduce ni opera maquinaria.** Las señales son ficticias;
        sus respuestas no se utilizarán para recomendar cambios reales en la circulación.
        No pediremos el número, una fotografía ni el país de su permiso de conducir.

        Después de cada velocidad indicará su confianza de 0 a 100. Al final puede explicar
        su criterio en una frase. El texto es opcional: no incluya nombres, direcciones ni
        otra información personal.
        """
    )
    with st.expander("Privacidad, retirada y remuneración"):
        st.markdown(
            f"""
            Participar es voluntario y puede abandonar antes del envío final. Los
            identificadores técnicos de plataforma, si existen, se transforman de inmediato
            mediante HMAC y no se guardan en bruto. Un HMAC es un seudónimo restringido, no
            anonimato. El texto abierto y las marcas temporales exactas permanecen restringidos.

            El pago base no depende de las elecciones ni de una exclusión analítica. Una de
            las respuestas podrá compararse con la de otra persona; una coincidencia exacta
            puede generar 0,50 € adicionales. Contacto para dudas o retirada: **{_contacto()}**.
            En una recogida real deben constar las aprobaciones y plazos institucionales.
            """
        )

    casillas = [
        ("edad", "Confirmo que tengo 18 años o más."),
        ("permiso", "Confirmo que tengo un permiso de conducir vigente."),
        ("espanol", "Comprendo las instrucciones en español."),
        ("no_conduce", "Confirmo que no estoy conduciendo ni operando maquinaria."),
        ("leido", "He leído la información y he podido decidir libremente."),
        ("ficticias", "Entiendo que las señales son ficticias y no ofrecen recomendación vial."),
        ("texto", "Entiendo que la explicación es opcional y no debo escribir información personal."),
        ("acepta", "Acepto participar en las condiciones descritas."),
    ]
    valores = [st.checkbox(etiqueta, value=False, key=f"consent_{clave}") for clave, etiqueta in casillas]
    columna_si, columna_no = st.columns(2)
    with columna_si:
        if st.button("ACEPTO Y CONTINÚO", type="primary", use_container_width=True):
            if not all(valores):
                st.error("Para participar debe confirmar todos los criterios. Puede salir sin enviar respuestas.")
            else:
                st.session_state["_inicio_utc"] = storage.ahora_utc()
                st.session_state["_etapa"] = "escenario"
                st.rerun()
    with columna_no:
        if st.button("NO ACEPTO · SALIR", use_container_width=True):
            st.session_state["_etapa"] = "rechazo"
            st.rerun()


def mostrar_rechazo() -> None:
    st.info(
        "No se ha iniciado el experimento ni se ha guardado una respuesta experimental. "
        "Gracias por considerar la invitación."
    )


def mostrar_escenario(ruta: Path, identidad: dict[str, str]) -> None:
    st.subheader("Un país con señales distintas")
    st.markdown(
        """
        Imagine que conduce en un país que nunca ha visitado. Allí, las señales de velocidad
        no muestran números: muestran símbolos. Cada símbolo corresponde a una velocidad
        máxima en kilómetros por hora, pero usted desconoce el código.

        Dé su mejor estimación. Cuando cierre la muestra, una respuesta podrá compararse con
        la de otra persona. Si ambas coinciden exactamente para el mismo símbolo, cada una
        recibe 0,50 € adicionales. El pago base no depende de coincidir.
        """
    )
    if st.button("COMENZAR", type="primary"):
        try:
            asignacion = storage.obtener_o_crear_asignacion(
                ruta,
                participant_hmac=identidad["participant_hmac"],
                study_hmac=identidad["study_hmac"],
                session_hmac=identidad["session_hmac"],
                hmac_version=identidad["hmac_version"],
                origen_captura=identidad["origen_captura"],
                inicio_utc=st.session_state.get("_inicio_utc", storage.ahora_utc()),
            )
        except storage.ErrorAlmacenamiento as exc:
            st.error(f"No se pudo reservar la tarea: {exc}. Contacte con {_contacto()}.")
            return
        st.session_state["_asignacion"] = asdict(asignacion)
        st.session_state["_etapa"] = "primera"
        st.rerun()


def _segundos_desde(timestamp_utc: str) -> float:
    inicio = datetime.fromisoformat(timestamp_utc.replace("Z", "+00:00"))
    return round(max(0.0, (datetime.now(timezone.utc) - inicio).total_seconds()), 3)


def mostrar_senal(ruta: Path, identidad: dict[str, str], numero: int) -> None:
    estado = storage.obtener_estado_por_sesion(ruta, identidad["session_hmac"])
    if estado is None:
        st.error("No existe una asignación confirmada; no se mostrará ningún estímulo.")
        return
    if numero == 1:
        simbolo = estado.simbolo_primero
        if estado.estado != "asignado":
            st.session_state["_etapa"] = "segunda"
            st.rerun()
        if estado.primera_render_utc is None:
            estado = storage.marcar_render_primera(ruta, identidad["session_hmac"], storage.ahora_utc())
        inicio_render = estado.primera_render_utc
        titulo = "Primera señal"
        transicion = "Ve la siguiente señal de velocidad."
    else:
        simbolo = "platano" if estado.simbolo_primero == "naranja" else "naranja"
        if estado.estado != "primera_completa":
            destino = "explicacion" if estado.estado in {"segunda_completa", "completo"} else "primera"
            st.session_state["_etapa"] = destino
            st.rerun()
        if estado.segunda_render_utc is None:
            estado = storage.marcar_render_segunda(ruta, identidad["session_hmac"], storage.ahora_utc())
        inicio_render = estado.segunda_render_utc
        titulo = "Segunda señal"
        transicion = "Unos kilómetros después, bajo las mismas condiciones, aparece otra señal."
    if inicio_render is None:
        st.error("No se pudo confirmar el inicio temporal de esta pantalla.")
        return

    nombres = {"naranja": "NARANJA", "platano": "PLÁTANO"}
    st.subheader(titulo)
    st.write(transicion)
    svg_embebido(simbolo)
    st.markdown(
        f"**Esta señal muestra un {nombres[simbolo]}. ¿Qué velocidad máxima cree que indica?**"
    )
    with st.form(f"form_senal_{numero}", clear_on_submit=False):
        velocidad = st.radio(
            "Velocidad",
            options=VELOCIDADES,
            index=None,
            horizontal=True,
            format_func=lambda valor: f"{valor} km/h",
            key=f"velocidad_widget_{numero}",
        )
        confianza = st.number_input(
            "¿Qué confianza tiene en que otra persona interprete esta señal del mismo modo?",
            min_value=0,
            max_value=100,
            value=None,
            step=1,
            placeholder="0 = ninguna · 100 = completa",
            key=f"confianza_widget_{numero}",
        )
        st.caption("Debe elegir explícitamente una velocidad y una confianza entera entre 0 y 100.")
        enviado = st.form_submit_button("CONFIRMAR Y CONTINUAR", type="primary")
    if enviado:
        if velocidad is None or confianza is None:
            st.error("Seleccione una velocidad y escriba una confianza antes de continuar.")
            return
        tiempo_s = _segundos_desde(inicio_render)
        try:
            if numero == 1:
                storage.guardar_primera_respuesta(
                    ruta,
                    session_hmac=identidad["session_hmac"],
                    velocidad=int(velocidad),
                    confianza=int(confianza),
                    tiempo_s=tiempo_s,
                    aceptada_utc=storage.ahora_utc(),
                )
                st.session_state["_etapa"] = "segunda"
            else:
                storage.guardar_segunda_respuesta(
                    ruta,
                    session_hmac=identidad["session_hmac"],
                    velocidad=int(velocidad),
                    confianza=int(confianza),
                    tiempo_s=tiempo_s,
                    aceptada_utc=storage.ahora_utc(),
                )
                st.session_state["_etapa"] = "explicacion"
        except storage.ErrorAlmacenamiento as exc:
            st.error(
                f"La respuesta no quedó confirmada: {exc}. No avance ni abra otra pestaña; "
                f"contacte con {_contacto()}."
            )
            return
        st.rerun()


def mostrar_explicacion(ruta: Path, identidad: dict[str, str]) -> None:
    estado = storage.obtener_estado_por_sesion(ruta, identidad["session_hmac"])
    if estado is None or estado.estado not in {"segunda_completa", "completo"}:
        st.error("La segunda respuesta todavía no está confirmada.")
        return
    if estado.estado == "completo":
        st.session_state["_etapa"] = "debriefing"
        st.rerun()
    st.subheader("Explicación opcional")
    st.warning(
        "No incluya nombres, direcciones, identificadores de plataforma ni otra información personal."
    )
    with st.form("form_explicacion", clear_on_submit=False):
        explicacion = st.text_area(
            "En una frase, ¿qué le hizo asociar cada símbolo con la velocidad elegida?",
            value="",
            max_chars=1000,
            placeholder="Puede dejar este campo vacío.",
            key="explicacion_widget",
        )
        enviado = st.form_submit_button("GUARDAR RESPUESTA", type="primary")
    if enviado:
        fin_utc = st.session_state.setdefault("_fin_intento_utc", storage.ahora_utc())
        try:
            confirmado = storage.finalizar_registro(
                ruta,
                session_hmac=identidad["session_hmac"],
                respuesta_abierta=explicacion,
                categorias_motivo=analysis.categorizar_motivo(explicacion),
                fin_utc=fin_utc,
            )
        except storage.ErrorAlmacenamiento as exc:
            st.error(
                f"No se pudo confirmar el guardado final: {exc}. No se le redirigirá. "
                f"Conserve esta pantalla y contacte con {_contacto()}."
            )
            return
        if confirmado.estado != "completo":
            st.error("El almacenamiento no confirmó un registro completo; no se habilita el retorno.")
            return
        st.session_state["_guardado_confirmado"] = True
        st.session_state["_etapa"] = "debriefing"
        st.rerun()


def mostrar_debriefing(ruta: Path, identidad: dict[str, str], modo: str) -> None:
    estado = storage.obtener_estado_por_sesion(ruta, identidad["session_hmac"])
    if estado is None or estado.estado != "completo":
        st.error("No existe confirmación de guardado. El debriefing y el retorno permanecen bloqueados.")
        return
    st.session_state["_guardado_confirmado"] = True
    st.subheader("No existía una velocidad correcta")
    st.markdown(
        """
        Gracias por participar. Las señales eran ficticias y no existía un código oficial que
        relacionara cada fruta con una velocidad.

        La hipótesis se revela ahora: esperamos que, al aparecer primero, la naranja reciba una
        velocidad media mayor que el plátano. El análisis principal compara **solo esa primera
        decisión** entre grupos asignados al azar. La segunda puede estar influida por anclaje o
        contraste y se estudia por separado.

        Ninguna elección se califica como correcta. Un patrón compartido no demostraría que la
        asociación sea universal, que funcione en otros países o idiomas ni que una señal frutal
        sea segura. Este estudio no recomienda velocidades ni cambios en señales reales.

        La exclusión estadística no elimina el pago base ni la oportunidad de bonificación. En el
        seminario, los resultados de referencia proceden de 500 registros totalmente sintéticos;
        no representan respuestas observadas ni pagos reales.
        """
    )
    st.success("El registro quedó confirmado una sola vez.")
    if modo == "live":
        url = leer_config("PROLIFIC_COMPLETION_URL")
        if _url_finalizacion_valida(url):
            st.link_button("FINALIZAR Y VOLVER A PROLIFIC", url, type="primary")
        else:
            st.error(f"Falta la ruta de retorno. El registro está guardado; contacte con {_contacto()}.")
    else:
        st.caption("Demo local: no se ejecutan pagos ni redirecciones de plataforma.")
        if st.button("CERRAR DEMOSTRACIÓN"):
            st.session_state["_etapa"] = "cierre"
            st.rerun()


def _mostrar_metricas(tabla: Any) -> None:
    datos = analysis.resumen(tabla)
    columnas = st.columns(4)
    columnas[0].metric("Registros", datos["n_total"])
    columnas[1].metric("Incluidos", datos["n_incluidas"])
    media_n = datos["media_primera_naranja"]
    media_p = datos["media_primera_platano"]
    columnas[2].metric("Media primera · naranja", "—" if media_n is None else f"{media_n:.2f}")
    columnas[3].metric("Media primera · plátano", "—" if media_p is None else f"{media_p:.2f}")


def panel_docente() -> None:
    st.title("Panel docente")
    st.caption("Acceso discreto · las fuentes SINTÉTICA y RECIBIDA nunca se combinan.")
    especificacion = leer_config("DOCENTE_PASSWORD_HASH")
    if not especificacion:
        st.error("El panel está cerrado: falta DOCENTE_PASSWORD_HASH en los secretos del servidor.")
        return
    if not st.session_state.get("_docente_autorizado", False):
        with st.form("login_docente"):
            password = st.text_input("Contraseña", type="password")
            enviado = st.form_submit_button("ENTRAR")
        if enviado:
            if verificar_password_docente(password, especificacion):
                st.session_state["_docente_autorizado"] = True
                st.rerun()
            else:
                st.error("Credenciales no válidas.")
        return

    if st.button("Cerrar sesión docente"):
        st.session_state["_docente_autorizado"] = False
        st.rerun()
    pestana_sintetica, pestana_recibida = st.tabs(
        ["SINTÉTICA · SIMULACIÓN DOCENTE", "RECIBIDA · RESTRINGIDA"]
    )
    with pestana_sintetica:
        st.info(
            "Fuente congelada: copia pública de 500 registros sintéticos. No contiene respuestas recibidas."
        )
        try:
            sinteticos = analysis.cargar_sinteticos(CSV_SINTETICO)
            _mostrar_metricas(sinteticos)
            figura_1 = analysis.figura_distribuciones(sinteticos, "SINTÉTICA")
            st.pyplot(figura_1, clear_figure=True)
            plt.close(figura_1)
            figura_2 = analysis.figura_primera_respuesta(sinteticos, "SINTÉTICA")
            st.pyplot(figura_2, clear_figure=True)
            plt.close(figura_2)
            st.download_button(
                "DESCARGAR CSV PÚBLICO SINTÉTICO",
                data=analysis.bytes_csv_publico_sintetico(CSV_SINTETICO),
                file_name="velocidad_frutas_publico.csv",
                mime="text/csv; charset=utf-8",
                on_click="ignore",
            )
        except analysis.ErrorAnalisis as exc:
            st.error(f"La copia sintética no superó la validación: {exc}")

    with pestana_recibida:
        st.warning(
            "Fuente restringida independiente. El panel solo muestra agregados; no expone HMAC, "
            "texto abierto ni timestamps. No publique estos datos sin revisión institucional."
        )
        try:
            ruta = ruta_bd("demo")
            recuentos = storage.resumen_restringido(ruta)
            st.caption("Estados restringidos: " + (", ".join(f"{k}={v}" for k, v in recuentos.items()) or "sin filas"))
            recibidas = analysis.preparar_recibidas(storage.listar_respuestas_publicables(ruta))
            if recibidas.empty:
                st.info("Todavía no hay registros recibidos completos.")
            else:
                origen = st.selectbox(
                    "Vista recibida",
                    options=["respuesta_demo", "respuesta_recibida"],
                    format_func=lambda x: "Demo local" if x == "respuesta_demo" else "Live autorizada",
                )
                vista = recibidas.loc[recibidas["origen_captura"].eq(origen)].copy()
                if vista.empty:
                    st.info("No hay registros completos para esta vista.")
                else:
                    _mostrar_metricas(vista)
                    if int(vista["incluida"].sum()) == 0:
                        st.info("Aún no hay registros recibidos que superen la regla temporal analítica.")
                    else:
                        figura_1 = analysis.figura_distribuciones(vista, "RECIBIDA")
                        st.pyplot(figura_1, clear_figure=True)
                        plt.close(figura_1)
                        figura_2 = analysis.figura_primera_respuesta(vista, "RECIBIDA")
                        st.pyplot(figura_2, clear_figure=True)
                        plt.close(figura_2)
                    st.caption(
                        "No se ofrece descarga de respuestas recibidas: una lista positiva no sustituye "
                        "la revisión de divulgación y el contrato real todavía no está versionado."
                    )
        except (storage.ErrorAlmacenamiento, analysis.ErrorAnalisis) as exc:
            st.error(f"No se pudo abrir la vista recibida: {exc}")


def sincronizar_etapa_con_bd(ruta: Path, identidad: dict[str, str]) -> None:
    estado = storage.obtener_estado_por_sesion(ruta, identidad["session_hmac"])
    if estado is None:
        st.session_state.setdefault("_etapa", "informacion")
        return
    st.session_state["_asignacion"] = asdict(estado)
    if estado.estado == "completo" and st.session_state.get("_etapa") == "cierre":
        return
    destino = {
        "asignado": "primera",
        "primera_completa": "segunda",
        "segunda_completa": "explicacion",
        "completo": "debriefing",
    }[estado.estado]
    st.session_state["_etapa"] = destino


def main() -> None:
    configurar_pagina()
    try:
        modo = modo_solicitado()
        if modo == "docente":
            panel_docente()
            return
        identidad = identidad_hmac(modo)
        ruta = ruta_bd(modo)
        sincronizar_etapa_con_bd(ruta, identidad)
    except (ErrorConfiguracion, storage.ErrorAlmacenamiento) as exc:
        st.error(f"La aplicación no puede iniciar esta sesión: {exc}")
        st.stop()
        return

    cabecera_participante(modo)
    etapa = st.session_state.get("_etapa", "informacion")
    if etapa == "informacion":
        mostrar_informacion()
    elif etapa == "escenario":
        mostrar_escenario(ruta, identidad)
    elif etapa == "primera":
        mostrar_senal(ruta, identidad, 1)
    elif etapa == "segunda":
        mostrar_senal(ruta, identidad, 2)
    elif etapa == "explicacion":
        mostrar_explicacion(ruta, identidad)
    elif etapa == "debriefing":
        mostrar_debriefing(ruta, identidad, modo)
    elif etapa == "rechazo":
        mostrar_rechazo()
    elif etapa == "cierre":
        st.success("Demostración cerrada. Puede cerrar esta pestaña.")
    else:
        st.error("Estado de interfaz desconocido; no se ha escrito ninguna respuesta nueva.")
    st.divider()
    st.markdown(
        '<p class="vf-note">Señales ficticias · sin recomendación vial · panel autorizado mediante '
        '<code>?modo=docente</code></p>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
