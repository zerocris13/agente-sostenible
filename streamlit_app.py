
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import streamlit as st


# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DEMO_DIR = BASE_DIR / "demo_results"
OUTPUTS_DIR = BASE_DIR / "outputs"
IMAGES_DIR = BASE_DIR / "data" / "marcos_logicos"

st.set_page_config(
    page_title="Evaluador de Bonos Sostenibles",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# 2. ESTILO VISUAL
# ============================================================

st.html(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=DM+Sans:wght@400;500;600&display=swap');

:root {
    --verde: #5D7869;
    --verde-oscuro: #395548;
    --verde-claro: #E1EAE1;
    --beige: #EFEAE0;
    --marfil: #F8F7F2;
    --linea: #B6C7BA;
    --texto: #354B3D;
    --texto-secundario: #526B5A;
}

[data-testid="stAppViewContainer"] {
    background-color: var(--marfil);
    color: var(--texto);
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1060px;
    padding-top: 2.4rem;
    padding-bottom: 3rem;
}

/* Tipografía */

h1, h2, h3 {
    font-family: "Cormorant Garamond", Georgia, serif !important;
    color: var(--verde-oscuro) !important;
    font-weight: 500 !important;
    letter-spacing: -0.015em;
}

h1 { font-size: 3.4rem !important; }
h2 { font-size: 2.3rem !important; }
h3 { font-size: 2rem !important; }

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    color: var(--texto);
    font-family: "DM Sans", "Segoe UI", sans-serif;
    font-size: 1rem;
    line-height: 1.8;
}

[data-testid="stCaptionContainer"] p,
[data-testid="stCaptionContainer"] span {
    color: var(--texto-secundario) !important;
    font-size: 0.98rem !important;
    line-height: 1.7 !important;
    opacity: 1 !important;
}

/* Separadores */

hr {
    border: 0 !important;
    border-top: 2px solid var(--linea) !important;
    opacity: 1 !important;
    margin: 2rem 0 !important;
}

/* Bandas de sección */

div.st-key-section_inicio,
div.st-key-section_resultado,
div.st-key-section_evidencias,
div.st-key-section_auditoria {
    padding: 0.85rem 1.35rem 0.95rem;
    border-left: 5px solid var(--verde);
    border-bottom: 2px solid var(--linea);
    border-radius: 0;
    margin: 0.75rem 0 1.4rem;
}

div.st-key-section_inicio,
div.st-key-section_evidencias {
    background: var(--beige);
}

div.st-key-section_resultado,
div.st-key-section_auditoria {
    background: var(--verde-claro);
}

div[class*="st-key-section_"] h3 {
    color: var(--verde-oscuro) !important;
    font-size: 2.15rem !important;
    line-height: 1.2 !important;
    margin: 0 !important;
}

div[class*="st-key-section_"]
[data-testid="stCaptionContainer"] p {
    color: #445E4E !important;
    font-size: 1.04rem !important;
    line-height: 1.7 !important;
}

/* Inputs */

[data-testid="stWidgetLabel"] p {
    color: #3B5947 !important;
    font-size: 1.03rem !important;
    font-weight: 600 !important;
}

[data-baseweb="input"] > div,
[data-baseweb="select"] > div {
    background: #FFFFFF !important;
    border: 1px solid #CBD5CB !important;
    border-radius: 3px !important;
}

[data-baseweb="input"] input {
    color: #344F40 !important;
    -webkit-text-fill-color: #344F40 !important;
    font-size: 1.05rem !important;
}

/* Botones principales: blanco sobre verde */

button[data-testid="stBaseButton-primary"],
.stButton > button[kind="primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"] {
    background-color: #496957 !important;
    border: 1px solid #496957 !important;
    border-radius: 3px !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    min-height: 2.9rem;
    padding: 0.55rem 1.5rem !important;
}

button[data-testid="stBaseButton-primary"] *,
.stButton > button[kind="primary"] *,
[data-testid="stFormSubmitButton"] button[kind="primary"] * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

button[data-testid="stBaseButton-primary"]:hover,
.stButton > button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] button[kind="primary"]:hover {
    background-color: #344F40 !important;
    border-color: #344F40 !important;
}

/* Botón secundario: verde sobre marfil */

button[data-testid="stBaseButton-secondary"] {
    background: transparent !important;
    border: 1px solid var(--linea) !important;
    color: var(--verde-oscuro) !important;
}

button[data-testid="stBaseButton-secondary"] * {
    color: var(--verde-oscuro) !important;
}

/* Métricas: sin cards */

[data-testid="stMetric"] {
    padding: 0.5rem 0 1rem;
    border-bottom: 2px solid var(--linea);
    background: transparent !important;
}

[data-testid="stMetricLabel"] p {
    color: var(--texto-secundario) !important;
    font-size: 0.98rem !important;
}

[data-testid="stMetricValue"] {
    color: var(--verde-oscuro) !important;
    font-family: "Cormorant Garamond", Georgia, serif !important;
}

/* Pestañas */

.stTabs [data-baseweb="tab-list"] {
    gap: 1.2rem;
    border-bottom: 2px solid var(--linea);
}

.stTabs [data-baseweb="tab"] {
    color: #506A58 !important;
    font-size: 1rem !important;
}

.stTabs [aria-selected="true"] {
    color: var(--verde-oscuro) !important;
    font-weight: 600 !important;
}

/* Expanders */

[data-testid="stExpander"] {
    border: 1px solid #CBD5CB;
    background: #FFFFFF;
    border-radius: 3px;
}

[data-testid="stExpander"] summary * {
    color: var(--verde-oscuro) !important;
}

/* Responsive */

@media (max-width: 720px) {
    .block-container {
        padding-top: 1.2rem;
    }

    h1 {
        font-size: 2.55rem !important;
    }

    div[class*="st-key-section_"] {
        padding: 0.75rem 1rem;
    }

    div[class*="st-key-section_"] h3 {
        font-size: 1.85rem !important;
    }
}
</style>
    """
)



# 7E56_CONTRASTE_BOTONES
st.html("""
<style>
button[data-testid="stBaseButton-primary"]:not(:disabled),
.stButton button[kind="primary"]:not(:disabled),
[data-testid="stFormSubmitButton"] button[kind="primary"]:not(:disabled) {
    background-color: #496957 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

button[data-testid="stBaseButton-primary"]:not(:disabled) *,
.stButton button[kind="primary"]:not(:disabled) *,
[data-testid="stFormSubmitButton"] button[kind="primary"]:not(:disabled) * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
</style>
""")


# CONTRASTE_FORMULARIO_ANALISTA
st.html("""
<style>
[data-testid="stFormSubmitButton"] button:not(:disabled),
button[kind="primaryFormSubmit"]:not(:disabled),
button[data-testid="stBaseButton-primaryFormSubmit"]:not(:disabled) {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

[data-testid="stFormSubmitButton"] button:not(:disabled) *,
button[kind="primaryFormSubmit"]:not(:disabled) *,
button[data-testid="stBaseButton-primaryFormSubmit"]:not(:disabled) * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
</style>
""")

# ============================================================
# 3. FUNCIONES AUXILIARES
# ============================================================

def obtener_carpeta_resultados() -> Path:
    """Prioriza los expedientes reducidos de demostración."""

    if DEMO_DIR.is_dir():
        if any(DEMO_DIR.glob("piloto_*.json")):
            return DEMO_DIR

    return OUTPUTS_DIR


def cargar_catalogo() -> dict[str, dict]:
    """Carga resultados guardados sin ejecutar OpenAI."""

    carpeta = obtener_carpeta_resultados()
    catalogo = {}

    if not carpeta.is_dir():
        return catalogo

    for archivo in sorted(carpeta.glob("piloto_*.json")):

        coincidencia = re.fullmatch(
            r"piloto_(\d+)\.json",
            archivo.name,
        )

        if not coincidencia:
            continue

        try:
            registro = json.loads(
                archivo.read_text(encoding="utf-8")
            )

        except (OSError, json.JSONDecodeError):
            continue

        if not isinstance(registro, dict):
            continue

        if not isinstance(registro.get("resultado"), dict):
            continue

        catalogo[coincidencia.group(1)] = registro

    return catalogo


def mostrar_seccion(
    titulo: str,
    clave: str,
    descripcion: str = "",
):
    """Crea una franja con controles nativos de Streamlit."""

    with st.container(key=clave):
        st.subheader(titulo)

        if descripcion:
            st.caption(descripcion)


def mostrar_evidencias(elementos):
    """Presenta evidencia documental numerada."""

    if not elementos:
        st.caption("No se registró evidencia.")
        return

    if not isinstance(elementos, list):
        elementos = [elementos]

    for numero, elemento in enumerate(elementos, 1):

        if isinstance(elemento, str):
            st.write(f"**{numero}.** {elemento}")

        else:
            st.markdown(f"**Evidencia {numero}**")
            st.write(elemento)


def buscar_imagenes(cui: str):
    """Encuentra las imágenes originales de un proyecto."""

    if not IMAGES_DIR.is_dir():
        return []

    patron = re.compile(
        rf"{re.escape(cui)}(?:[ _-]+\d+)?",
        re.IGNORECASE,
    )

    imagenes = []

    for archivo in IMAGES_DIR.iterdir():

        if not archivo.is_file():
            continue

        if archivo.suffix.lower() not in {
            ".png", ".jpg", ".jpeg"
        }:
            continue

        if patron.fullmatch(archivo.stem):
            imagenes.append(archivo)

    return sorted(
        imagenes,
        key=lambda p: p.name.lower(),
    )


def abreviar_categoria(nombre: str) -> str:
    """Utiliza nombres breves únicamente en el catálogo."""

    nombres = {
        "Gestión eficiente y resiliente de aguas y aguas residuales":
            "Gestión de aguas",

        "Gestión sostenible de recursos naturales, uso de suelos y áreas marinas protegidas":
            "Recursos naturales",
    }

    return nombres.get(nombre, nombre)



# ============================================================
# 4. DATOS Y NAVEGACIÓN
# ============================================================

@st.cache_data(show_spinner=False)
def cargar_proyectos():
    import pandas as pd

    ruta = (
        BASE_DIR
        / "data"
        / "dataset_limpio_agente_sostenible.xlsx"
    )

    tabla = pd.read_excel(
        ruta,
        sheet_name="PROYECTOS",
        dtype=str,
    ).fillna("")

    tabla["CUI"] = (
        tabla["CUI"]
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )

    tabla = tabla.drop_duplicates(subset="CUI")

    return tabla.set_index("CUI")


def leer_informe_existente(cui):
    """Recupera un informe sin ejecutar OpenAI."""

    rutas = [
        BASE_DIR / ".runtime" / "resultados"
        / f"piloto_{cui}.json",
        DEMO_DIR / f"piloto_{cui}.json",
    ]

    for ruta in rutas:
        if not ruta.is_file():
            continue

        try:
            registro = json.loads(
                ruta.read_text(encoding="utf-8")
            )

            if (
                isinstance(registro, dict)
                and str(registro.get("cui")) == cui
                and isinstance(
                    registro.get("resultado"), dict
                )
            ):
                return registro

        except (OSError, ValueError, TypeError):
            continue

    return None


def abrir_informe(registro):
    st.session_state["registro_actual"] = registro
    st.session_state["vista_actual"] = "informe"
    st.rerun()


def texto_informe(registro):
    """Informe descargable para el analista."""

    resultado = registro["resultado"]
    cui = str(registro["cui"])

    secciones = [
        "INFORME DE EVALUACIÓN DE SOSTENIBILIDAD",
        f"CUI: {cui}",
        "Marco del Bono Sostenible del Perú (2021)",
        "",
        "RESULTADO PRELIMINAR",
        str(resultado.get("estado", "No disponible")),
        "",
        "CATEGORÍA PROPUESTA",
        str(resultado.get("clasificacion", "No disponible")),
        "",
        "CRITERIO NORMATIVO",
        str(resultado.get("criterio_principal", "No determinado")),
        "",
        "JUSTIFICACIÓN",
        str(resultado.get("justificacion", "No disponible")),
    ]

    fuentes = [
        ("PROYECTO", "evidencia_proyecto"),
        ("BRECHAS", "evidencia_brechas"),
        ("MARCO 2021", "evidencia_marco"),
        ("MARCO LÓGICO", "evidencia_marco_logico"),
    ]

    for titulo, campo in fuentes:
        secciones.extend(["", f"EVIDENCIAS: {titulo}"])

        elementos = resultado.get(campo) or []

        if not isinstance(elementos, list):
            elementos = [elementos]

        if not elementos:
            secciones.append("Sin evidencia registrada.")

        for numero, elemento in enumerate(elementos, 1):
            secciones.append(f"{numero}. {elemento}")

    secciones.extend([
        "",
        "Este informe es preliminar y no constituye "
        "una aprobación oficial ni una certificación "
        "de elegibilidad financiera.",
    ])

    return "\n".join(secciones)


if "vista_actual" not in st.session_state:
    st.session_state["vista_actual"] = "inicio"

if "cui_seleccionado" not in st.session_state:
    st.session_state["cui_seleccionado"] = None


try:
    proyectos = cargar_proyectos()
except Exception:
    st.error(
        "No fue posible cargar el registro de proyectos."
    )
    st.stop()


# ============================================================
# PANTALLA 1. CONSULTA Y EVALUACIÓN
# ============================================================

if st.session_state["vista_actual"] == "inicio":

    st.title("Evaluador de Proyectos Sostenibles")

    st.caption(
        "Herramienta de apoyo para la clasificación preliminar "
        "de proyectos de inversión pública conforme al "
        "Marco del Bono Sostenible del Perú (2021)."
    )

    st.divider()

    mostrar_seccion(
        titulo="Consultar proyecto de inversión",
        clave="section_inicio",
        descripcion=(
            "Ingrese el Código Único de Inversión (CUI) "
            "para recuperar la información del proyecto."
        ),
    )

    with st.form("consulta_proyecto"):

        cui_ingresado = st.text_input(
            "Código Único de Inversión (CUI)",
            placeholder="Ingrese un código de 7 dígitos",
            max_chars=7,
            key="campo_cui",
        )

        consultar = st.form_submit_button(
            "Consultar proyecto",
            type="primary",
        )

    if consultar:

        cui = cui_ingresado.strip()

        if not re.fullmatch(r"[0-9]{7}", cui):

            st.error(
                "Ingrese un CUI válido de siete dígitos."
            )

            st.session_state["cui_seleccionado"] = None

        elif cui not in proyectos.index:

            st.warning(
                "El CUI no figura en el registro de proyectos "
                "disponible para esta evaluación."
            )

            st.session_state["cui_seleccionado"] = None

        else:

            st.session_state["cui_seleccionado"] = cui

    cui = st.session_state["cui_seleccionado"]

    if cui is not None and cui in proyectos.index:

        proyecto = proyectos.loc[cui]

        st.divider()

        st.subheader("Información del proyecto")

        st.caption(f"Código Único de Inversión: {cui}")

        st.markdown("**Nombre de la inversión**")

        st.write(
            proyecto.get("NOMBRE_INVERSION")
            or "Información no disponible"
        )

        izquierda, derecha = st.columns(2)

        with izquierda:

            st.markdown("**Sector o nivel de gobierno**")
            st.write(
                proyecto.get("SECTOR")
                or "No registrado"
            )

            st.markdown("**Entidad responsable**")
            st.write(
                proyecto.get("ENTIDAD")
                or "No registrada"
            )

        with derecha:

            st.markdown("**Ubicación**")

            ubicacion = ", ".join(
                str(proyecto.get(campo, "")).strip()
                for campo in [
                    "DISTRITO",
                    "PROVINCIA",
                    "DEPARTAMENTO",
                ]
                if str(
                    proyecto.get(campo, "")
                ).strip()
            )

            st.write(
                ubicacion or "No registrada"
            )

            st.markdown("**Función**")
            st.write(
                proyecto.get("FUNCION")
                or "No registrada"
            )

        alternativa = str(
            proyecto.get("ALTERNATIVA", "")
        ).strip()

        if alternativa:

            with st.expander(
                "Ver componentes de la intervención",
                expanded=False,
            ):

                texto_original = re.sub(
                    r"\s+", " ", alternativa
                ).strip()

                def mejorar_lectura(fragmento):

                    fragmento = fragmento.strip(" ,;.")

                    if fragmento.isupper():
                        fragmento = fragmento.lower()

                    correcciones = {
                        "lineas": "líneas",
                        "instalacion": "instalación",
                        "construccion": "construcción",
                        "aduccion": "aducción",
                        "distribucion": "distribución",
                        "rehabilitacion": "rehabilitación",
                        "ampliacion": "ampliación",
                    }

                    for palabra, correccion in correcciones.items():

                        fragmento = re.sub(
                            rf"\b{palabra}\b",
                            correccion,
                            fragmento,
                            flags=re.IGNORECASE,
                        )

                    fragmento = re.sub(
                        r"\bpvc\b", "PVC",
                        fragmento,
                        flags=re.IGNORECASE,
                    )

                    return (
                        fragmento[:1].upper()
                        + fragmento[1:]
                    )

                patron_componentes = re.compile(
                    r"\bCOMPONENTE(?:\s+DE)?\s+"
                    r"(?:AGUA POTABLE|ALCANTARILLADO)"
                    r"\b",
                    re.IGNORECASE,
                )

                componentes = list(
                    patron_componentes.finditer(
                        texto_original
                    )
                )

                if componentes:

                    prefijo = texto_original[
                        :componentes[0].start()
                    ].strip()

                    if prefijo:
                        st.write(
                            mejorar_lectura(prefijo)
                        )

                    for indice, componente in enumerate(
                        componentes
                    ):

                        fin = (
                            componentes[indice + 1].start()
                            if indice + 1 < len(componentes)
                            else len(texto_original)
                        )

                        contenido = texto_original[
                            componente.end():fin
                        ].strip()

                        titulo_componente = (
                            mejorar_lectura(
                                componente.group()
                            )
                        )

                        st.markdown(
                            f"**{titulo_componente}**"
                        )

                        actividades = re.split(
                            r"(?=\b(?:INSTALACION|"
                            r"INSTALACIÓN|CONSTRUCCION|"
                            r"CONSTRUCCIÓN)\b)",
                            contenido,
                            flags=re.IGNORECASE,
                        )

                        actividades = [
                            a.strip()
                            for a in actividades
                            if a.strip()
                        ]

                        if actividades:

                            for actividad in actividades:

                                st.write(
                                    "• "
                                    + mejorar_lectura(actividad)
                                    + "."
                                )

                        else:
                            st.caption(
                                "Sin actividades desglosadas."
                            )

                else:

                    # Si no existe una estructura clara,
                    # conservamos el contenido fuente.
                    st.write(
                        mejorar_lectura(texto_original)
                    )

                st.caption(
                    "Información reorganizada a partir "
                    "de la descripción original del proyecto."
                )

                if st.checkbox(
                    "Consultar texto original",
                    key=f"texto_original_{cui}",
                ):
                    st.write(alternativa)

        st.divider()

        mostrar_seccion(
            titulo="Evaluación de sostenibilidad",
            clave="section_resultado",
            descripcion=(
                "El sistema analiza la información disponible "
                "del proyecto y contrasta sus características "
                "con los criterios del Marco 2021."
            ),
        )

        anterior = leer_informe_existente(cui)

        if anterior is not None:

            st.info(
                "Este proyecto cuenta con un informe "
                "de evaluación previamente generado."
            )

            if st.button(
                "Consultar informe existente",
                type="secondary",
                key="consultar_informe",
            ):
                abrir_informe(anterior)

        habilitado = (
            os.getenv(
                "ENABLE_LIVE_CLASSIFICATION", "0"
            ) == "1"
        )

        if not habilitado:

            st.info(
                "La generación de nuevas evaluaciones "
                "no está disponible temporalmente. "
                "Puede consultar los informes existentes."
            )

        else:

            with st.form(
                "solicitar_evaluacion",
                clear_on_submit=True,
            ):

                codigo = st.text_input(
                    "Código de autorización",
                    type="password",
                    help=(
                        "Código proporcionado al personal "
                        "autorizado para solicitar evaluaciones."
                    ),
                )

                confirmado = st.checkbox(
                    "Confirmo que deseo solicitar una "
                    "nueva evaluación de este proyecto."
                )

                enviar = st.form_submit_button(
                    "Evaluar sostenibilidad",
                    type="primary",
                )

            if enviar:

                if not confirmado:

                    st.warning(
                        "Confirme la solicitud de evaluación."
                    )

                elif not codigo:

                    st.warning(
                        "Ingrese su código de autorización."
                    )

                else:

                    from ejecutor_streamlit import (
                        ejecutar_clasificacion,
                    )

                    try:

                        with st.spinner(
                            "Analizando el proyecto y "
                            "contrastando sus evidencias..."
                        ):

                            registro = ejecutar_clasificacion(
                                cui=cui,
                                confirmado=True,
                                codigo_acceso=codigo,
                            )

                    except PermissionError as error:

                        st.error(
                            "No se pudo autorizar la evaluación. "
                            + str(error)
                        )

                    except ValueError:

                        st.error(
                            "No fue posible validar la solicitud."
                        )

                    except Exception:

                        st.error(
                            "No se pudo completar la evaluación. "
                            "No vuelva a enviarla de inmediato: "
                            "solicite revisar el estado del proceso."
                        )

                    else:

                        # Copia temporal. No reemplaza
                        # un almacenamiento persistente.
                        try:
                            carpeta = (
                                BASE_DIR
                                / ".runtime"
                                / "resultados"
                            )

                            carpeta.mkdir(
                                parents=True,
                                exist_ok=True,
                            )

                            destino = (
                                carpeta
                                / f"piloto_{cui}.json"
                            )

                            destino.write_text(
                                json.dumps(
                                    registro,
                                    ensure_ascii=False,
                                    indent=2,
                                    default=str,
                                ),
                                encoding="utf-8",
                            )

                        except OSError:
                            pass

                        abrir_informe(registro)

    st.divider()

    st.caption(
        "Las evaluaciones son preliminares y están "
        "sujetas a revisión por personal competente."
    )


# ============================================================
# PANTALLA 2. INFORME PARA EL ANALISTA
# ============================================================

else:

    registro = st.session_state.get("registro_actual")

    if not (
        isinstance(registro, dict)
        and isinstance(registro.get("resultado"), dict)
    ):
        st.session_state["vista_actual"] = "inicio"
        st.rerun()

    resultado = registro["resultado"]
    cui = str(registro.get("cui", ""))

    if st.button(
        "← Volver a la consulta",
        type="secondary",
    ):
        st.session_state["vista_actual"] = "inicio"
        st.rerun()

    st.title("Informe de evaluación")

    st.caption(
        f"Proyecto CUI {cui} · "
        "Marco del Bono Sostenible del Perú (2021)"
    )

    st.divider()

    mostrar_seccion(
        titulo="Resultado de la evaluación",
        clave="section_resultado",
        descripcion=(
            "Clasificación preliminar sustentada "
            "en la información disponible."
        ),
    )

    estado = resultado.get("estado", "")

    estados = {
        "APROBADO": "Clasificación sustentada",
        "REVISION_HUMANA": "Requiere revisión humana",
    }

    etiqueta_estado = estados.get(
        estado,
        "Evaluación preliminar",
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric("CUI", cui)

    with col2:
        st.metric("Resultado", etiqueta_estado)

    if (
        estado == "REVISION_HUMANA"
        or resultado.get("requiere_revision_humana")
    ):
        st.warning(
            "El proyecto requiere revisión por un analista "
            "antes de adoptar una decisión."
        )

    st.subheader("Categoría propuesta")

    st.write(
        "**"
        + str(
            resultado.get("clasificacion")
            or "No determinada"
        )
        + "**"
    )

    st.subheader("Criterio normativo principal")

    st.write(
        resultado.get("criterio_principal")
        or "No determinado"
    )

    st.subheader("Justificación")

    st.write(
        resultado.get("justificacion")
        or "No se registró una justificación."
    )

    paginas = resultado.get("paginas_marco") or []

    if paginas:
        st.caption(
            "Referencia al Marco 2021, página(s): "
            + ", ".join(map(str, paginas))
        )

    st.divider()

    mostrar_seccion(
        titulo="Sustento documental",
        clave="section_evidencias",
        descripcion=(
            "Evidencias utilizadas o registradas "
            "durante la evaluación del proyecto."
        ),
    )

    t1, t2, t3, t4 = st.tabs([
        "Proyecto",
        "Brechas",
        "Marco normativo",
        "Marco lógico",
    ])

    with t1:
        mostrar_evidencias(
            resultado.get("evidencia_proyecto") or []
        )

    with t2:
        mostrar_evidencias(
            resultado.get("evidencia_brechas") or []
        )

    with t3:
        mostrar_evidencias(
            resultado.get("evidencia_marco") or []
        )

    with t4:

        mostrar_evidencias(
            resultado.get("evidencia_marco_logico") or []
        )

        imagenes = buscar_imagenes(cui)

        if imagenes:

            st.caption(
                f"Documentos visuales disponibles: {len(imagenes)}. "
                "Su disponibilidad no implica que hayan "
                "sido utilizados por el evaluador."
            )

            if st.checkbox(
                "Mostrar documentos del marco lógico",
                key=f"ver_imagenes_{cui}",
            ):

                for imagen in imagenes[:6]:

                    st.image(
                        str(imagen),
                        caption=imagen.name,
                        width="stretch",
                    )

        else:

            st.caption(
                "No se dispone de imágenes del "
                "marco lógico de este proyecto."
            )

    st.divider()

    mostrar_seccion(
        titulo="Observaciones y control de calidad",
        clave="section_auditoria",
        descripcion=(
            "Información de apoyo para revisar "
            "la consistencia del resultado."
        ),
    )

    veredicto = registro.get("veredicto") or {}

    if isinstance(veredicto, dict):

        aprobado = veredicto.get("aprobado")

        if aprobado is True:

            st.success(
                "La evaluación superó la verificación "
                "interna de consistencia."
            )

        elif aprobado is False:

            st.warning(
                "La verificación interna identificó "
                "aspectos que requieren revisión."
            )

        problemas = veredicto.get("problemas") or []

        if problemas:

            st.markdown("**Observaciones registradas**")

            if isinstance(problemas, list):

                for problema in problemas:
                    st.write(f"• {problema}")

            else:
                st.write(problemas)

    if (
        not resultado.get("evidencia_marco_logico")
        and not buscar_imagenes(cui)
    ):

        st.info(
            "El proyecto no cuenta con evidencia visual "
            "del marco lógico en los archivos disponibles."
        )

    st.download_button(
        "Descargar informe del proyecto",
        data=texto_informe(registro),
        file_name=f"informe_{cui}.txt",
        mime="text/plain",
        type="primary",
        key="descargar_informe_proyecto",
    )

    st.divider()

    st.caption(
        "Este resultado es una evaluación preliminar "
        "de apoyo al análisis documental. No constituye "
        "una certificación de elegibilidad financiera "
        "ni una aprobación oficial."
    )
