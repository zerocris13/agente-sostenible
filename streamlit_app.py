
from __future__ import annotations

import json
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
# 4. ESTADO DE NAVEGACIÓN
# ============================================================

if "vista_actual" not in st.session_state:
    st.session_state["vista_actual"] = "inicio"

if "cui_elegido" not in st.session_state:
    st.session_state["cui_elegido"] = None

catalogo = cargar_catalogo()


# ============================================================
# PANTALLA 1. CONSULTA DE PROYECTOS
# ============================================================

if st.session_state["vista_actual"] == "inicio":

    st.title("Evaluador de Bonos Sostenibles")

    st.caption(
        "Clasificación preliminar de proyectos de inversión "
        "pública según el Marco del Bono Sostenible del Perú (2021)."
    )

    st.divider()

    mostrar_seccion(
        titulo="Consultar proyecto",
        clave="section_inicio",
        descripcion=(
            "Seleccione un expediente evaluado o ingrese "
            "manualmente un Código Único de Inversión."
        ),
    )

    if not catalogo:
        st.warning(
            "No hay resultados disponibles en demo_results/ "
            "ni en outputs/."
        )
        st.stop()

    modo = st.radio(
        "Forma de consulta",
        [
            "Seleccionar un proyecto disponible",
            "Ingresar un CUI manualmente",
        ],
        horizontal=True,
    )

    cuis_disponibles = sorted(catalogo)

    with st.form("formulario_consulta"):

        if modo == "Seleccionar un proyecto disponible":

            indice = (
                cuis_disponibles.index("2304889")
                if "2304889" in cuis_disponibles
                else 0
            )

            cui = st.selectbox(
                "Código Único de Inversión (CUI)",
                options=cuis_disponibles,
                index=indice,
            )

        else:

            cui = st.text_input(
                "Código Único de Inversión (CUI)",
                value="2304889",
                max_chars=15,
                placeholder="Ej. 2304889",
            )

        consultar = st.form_submit_button(
            "Consultar proyecto",
            type="primary",
        )

    if consultar:

        cui_limpio = cui.strip()

        if not re.fullmatch(r"\d+", cui_limpio):

            st.error("Ingrese un CUI numérico válido.")

        elif cui_limpio not in catalogo:

            st.warning(
                "No existe una clasificación guardada "
                "para este CUI."
            )

        else:

            st.session_state["cui_elegido"] = cui_limpio
            st.session_state["vista_actual"] = "resultado"

            st.rerun()

    st.caption(
        f"{len(catalogo)} expedientes disponibles. "
        "La consulta no consume créditos de OpenAI."
    )

    st.divider()

    st.subheader("Expedientes disponibles")

    st.caption(
        "Seleccione un proyecto en el formulario anterior "
        "para abrir su informe individual."
    )

    filas = []

    for codigo in sorted(catalogo):

        resultado_lista = catalogo[codigo]["resultado"]

        categoria = resultado_lista.get(
            "clasificacion",
            "No disponible",
        )

        estado = resultado_lista.get(
            "estado",
            "No disponible",
        )

        filas.append({
            "CUI": codigo,
            "Categoría": abreviar_categoria(categoria),
            "Estado": (
                "Revisión humana"
                if estado == "REVISION_HUMANA"
                else "Aprobado"
                if estado == "APROBADO"
                else estado
            ),
        })

    st.dataframe(
        filas,
        width="stretch",
        hide_index=True,
    )

    st.divider()

    st.caption(
        "Los expedientes disponibles corresponden a "
        "evaluaciones preliminares previamente almacenadas. "
        "No representan la totalidad de proyectos del dataset."
    )


# ============================================================
# PANTALLA 2. INFORME DE CLASIFICACIÓN
# ============================================================

else:

    cui_actual = st.session_state.get("cui_elegido")

    if not cui_actual or cui_actual not in catalogo:

        st.session_state["vista_actual"] = "inicio"
        st.session_state["cui_elegido"] = None

        st.rerun()

    registro = catalogo[cui_actual]
    resultado = registro["resultado"]

    # --------------------------------------------------------
    # NAVEGACIÓN
    # --------------------------------------------------------

    if st.button(
        "← Volver a los proyectos",
        type="secondary",
    ):

        st.session_state["vista_actual"] = "inicio"
        st.session_state["cui_elegido"] = None

        st.rerun()

    st.title("Informe de clasificación")

    st.caption(
        f"Expediente CUI {cui_actual} · "
        "Marco del Bono Sostenible del Perú (2021)"
    )

    st.divider()

    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

    mostrar_seccion(
        titulo="Resultado de clasificación",
        clave="section_resultado",
        descripcion=(
            "Dictamen preliminar del sistema multiagente."
        ),
    )

    estado = resultado.get(
        "estado",
        "No disponible",
    )

    etiqueta_estado = {
        "APROBADO": "Aprobado",
        "REVISION_HUMANA": "Revisión humana",
    }.get(estado, estado)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("CUI", cui_actual)

    with col2:
        st.metric("Estado", etiqueta_estado)

    with col3:
        st.metric(
            "Iteraciones",
            resultado.get("iteraciones", 0),
        )

    # --------------------------------------------------------
    # DICTAMEN
    # --------------------------------------------------------

    st.subheader("Categoría propuesta")

    st.write(
        f"**{resultado.get('clasificacion', 'No disponible')}**"
    )

    st.subheader("Criterio normativo principal")

    st.write(
        resultado.get("criterio_principal")
        or "Criterio no determinado"
    )

    st.subheader("Justificación")

    st.write(
        resultado.get("justificacion")
        or "No se registró justificación."
    )

    paginas = resultado.get("paginas_marco") or []

    st.caption(
        "Páginas del Marco 2021: "
        + (
            ", ".join(map(str, paginas))
            if paginas
            else "No registradas"
        )
    )

    if (
        resultado.get("requiere_revision_humana")
        or estado == "REVISION_HUMANA"
    ):
        st.warning(
            "Este proyecto requiere revisión humana."
        )

    # --------------------------------------------------------
    # EVIDENCIAS
    # --------------------------------------------------------

    st.divider()

    mostrar_seccion(
        titulo="Evidencias recuperadas",
        clave="section_evidencias",
        descripcion=(
            "Información del proyecto y fuentes documentales "
            "utilizadas para sustentar la clasificación."
        ),
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "Proyecto",
        "Brechas",
        "Marco 2021",
        "Marco lógico",
    ])

    with tab1:

        mostrar_evidencias(
            resultado.get("evidencia_proyecto") or []
        )

    with tab2:

        mostrar_evidencias(
            resultado.get("evidencia_brechas") or []
        )

    with tab3:

        mostrar_evidencias(
            resultado.get("evidencia_marco") or []
        )

    with tab4:

        mostrar_evidencias(
            resultado.get("evidencia_marco_logico") or []
        )

        imagenes = buscar_imagenes(cui_actual)

        if imagenes:

            with st.expander(
                f"Ver imágenes originales ({len(imagenes)})"
            ):

                st.caption(
                    "La disponibilidad de las imágenes no "
                    "implica que el agente las haya consultado."
                )

                for imagen in imagenes[:6]:

                    st.image(
                        str(imagen),
                        caption=imagen.name,
                        width="stretch",
                    )

                if len(imagenes) > 6:

                    st.caption(
                        "Se muestran las primeras seis imágenes."
                    )

        else:

            st.caption(
                "No hay imágenes originales disponibles "
                "en este entorno."
            )

    # --------------------------------------------------------
    # AUDITORÍA
    # --------------------------------------------------------

    st.divider()

    mostrar_seccion(
        titulo="Auditoría de la ejecución",
        clave="section_auditoria",
        descripcion=(
            "Decisiones, herramientas y verificaciones "
            "del flujo LangGraph."
        ),
    )

    with st.expander("Trayectoria de LangGraph"):
        st.json(
            registro.get("trayectoria") or []
        )

    with st.expander("Veredicto semántico"):
        st.json(
            registro.get("veredicto") or {}
        )

    with st.expander("Herramientas utilizadas"):
        st.json(
            registro.get("tool_calls") or []
        )

    with st.expander("Consultas al Marco 2021"):
        st.json(
            registro.get("consultas_marco") or []
        )

    st.divider()

    st.caption(
        "Sistema académico de clasificación documental. "
        "Los resultados son preliminares y no constituyen "
        "certificaciones de elegibilidad financiera "
        "ni autorizaciones de financiamiento."
    )
