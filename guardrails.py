from __future__ import annotations
import json
import re

CUI_RE = re.compile(r"^\d{6,10}$")

SUSPICIOUS_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous",
    "disregard previous",
    "system prompt",
    "developer message",
    "act as system",
    "jailbreak",
]


def validar_cui(cui: str) -> str:
    cui = str(cui).strip().replace(".0", "")
    if not CUI_RE.fullmatch(cui):
        raise ValueError("El CUI debe contener únicamente entre 6 y 10 dígitos.")
    return cui


def detectar_inyeccion(texto: str) -> list[str]:
    lower = (texto or "").lower()
    return [p for p in SUSPICIOUS_PATTERNS if p in lower]

# Cambio para evitar que una categoria positiva pase la validacion formal con evidencia_suficiente=False

def validar_candidato_basico(
    candidato: dict,
    cui: str
) -> tuple[bool, list[str]]:
    """
    Valida la estructura, categoría y evidencia mínima
    de una propuesta de clasificación.

    Retorna:
        (True, []) si supera todas las validaciones.
        (False, problemas) si existen inconsistencias.
    """
    from rag import PAGINAS_CATEGORIA

    problemas: list[str] = []

    # 1. Comprobar correspondencia del CUI.
    if str(candidato.get("cui")) != str(cui):
        problemas.append("El CUI no coincide.")

    # 2. Comprobar que la categoría sea válida.
    clasificacion = candidato.get("clasificacion")
    categorias = set(PAGINAS_CATEGORIA.values())
    especiales = {"No aplica", "Información insuficiente"}

    if clasificacion not in categorias | especiales:
        problemas.append("Categoría desconocida.")
        return False, problemas

    suficiente = candidato.get("evidencia_suficiente")
    paginas = candidato.get("paginas_marco") or []

    # 3. Comprobar suficiencia y evidencia del proyecto.
    if clasificacion == "Información insuficiente":
        if suficiente is not False:
            problemas.append(
                "Una abstención debe indicar evidencia insuficiente."
            )
    else:
        if suficiente is not True:
            problemas.append(
                "No se puede clasificar con evidencia insuficiente."
            )

        if not (
            candidato.get("evidencia_proyecto")
            or candidato.get("evidencia_brechas")
            or candidato.get("evidencia_marco_logico")
        ):
            problemas.append("Falta evidencia del proyecto.")

    # 4. Comprobar evidencia normativa para categorías verdes.
    if clasificacion in categorias:
        pagina_esperada = next(
            p for p, c in PAGINAS_CATEGORIA.items()
            if c == clasificacion
        )

        if pagina_esperada not in paginas:
            problemas.append(
                f"La categoría requiere citar la página "
                f"{pagina_esperada} del Marco."
            )

        if not candidato.get("evidencia_marco"):
            problemas.append("Falta evidencia normativa.")

    # 5. Comprobar páginas normativas válidas.
    invalidas = [
        p for p in paginas
        if type(p) is not int or p < 30 or p > 38
    ]

    if invalidas:
        problemas.append(
            f"Páginas normativas inválidas: {invalidas}"
        )

    # 6. Exigir justificación.
    justificacion = candidato.get("justificacion") or ""

    if not isinstance(justificacion, str) or not justificacion.strip():
        problemas.append("Falta justificación.")

    # 7. Devolver siempre el resultado de la validación.
    return len(problemas) == 0, problemas




def obtener_alertas_documentales(tool_outputs: list[dict]) -> list[str]:
    """
    Detecta advertencias en los resultados de
    consultar_marco_logico sin utilizar un LLM.

    Las advertencias críticas deben activar
    revisión humana en el flujo LangGraph.
    """
    alertas = []

    for item in tool_outputs:
        if item.get("tool") != "consultar_marco_logico":
            continue

        contenido = item.get("content", "")

        try:
            datos = (
                json.loads(contenido)
                if isinstance(contenido, str)
                else contenido
            )
        except (json.JSONDecodeError, TypeError):
            alertas.append(
                "Respuesta del marco lógico con JSON inválido."
            )
            continue

        if not isinstance(datos, dict):
            alertas.append(
                "La respuesta documental no es un objeto JSON."
            )
            continue

        cui = datos.get("cui", "desconocido")

        if datos.get("procesado") is False:
            alertas.append(
                f"CUI {cui}: documento no procesado completamente."
            )

        conflictos = datos.get("conflictos_numeracion", {})

        if conflictos:
            alertas.append(
                f"CUI {cui}: existen archivos con numeración "
                f"de página repetida: {conflictos}"
            )

        if datos.get("requiere_revision_humana") is True:
            alertas.append(
                f"CUI {cui}: revisión documental requerida."
            )

    return list(dict.fromkeys(alertas))


def validar_citas_recuperadas(
    candidato: dict,
    tool_outputs: list[dict]
) -> tuple[bool, list[str]]:
    """
    Comprueba que las páginas citadas por el clasificador
    estén presentes en las respuestas reales del RAG.

    No evalúa si la interpretación semántica es correcta.
    """
    import json
    from rag import PAGINAS_CATEGORIA

    problemas = []
    categoria = candidato.get("clasificacion")
    paginas_citadas = candidato.get("paginas_marco") or []

    # Registrar únicamente evidencia devuelta por el RAG.
    recuperadas = set()

    for item in tool_outputs:
        if item.get("tool") != "buscar_criterios_marco":
            continue

        contenido = item.get("content", "")

        try:
            datos = (
                json.loads(contenido)
                if isinstance(contenido, str)
                else contenido
            )
        except (json.JSONDecodeError, TypeError):
            continue

        if not isinstance(datos, dict):
            continue

        for resultado in datos.get("resultados", []):
            if not isinstance(resultado, dict):
                continue

            pagina = resultado.get("pagina")
            categoria_rag = resultado.get("categoria")
            texto = resultado.get("texto", "")
            fuente = resultado.get("fuente")

            if (
                type(pagina) is int
                and isinstance(texto, str)
                and texto.strip()
                and fuente == "Marco del Bono Sostenible del Perú"
            ):
                recuperadas.add((pagina, categoria_rag))

    paginas_recuperadas = {
        pagina for pagina, _ in recuperadas
    }

    # Todas las páginas citadas deben haber sido recuperadas.
    paginas_sin_respaldo = [
        pagina for pagina in paginas_citadas
        if pagina not in paginas_recuperadas
    ]

    if paginas_sin_respaldo:
        problemas.append(
            "Se citaron páginas no recuperadas por el RAG: "
            f"{paginas_sin_respaldo}"
        )

    # Para categorías verdes, exigir el criterio específico.
    if categoria in PAGINAS_CATEGORIA.values():
        pagina_oficial = next(
            pagina
            for pagina, nombre in PAGINAS_CATEGORIA.items()
            if nombre == categoria
        )

        if pagina_oficial not in paginas_citadas:
            problemas.append(
                f"No se citó la página normativa {pagina_oficial}."
            )

        if (pagina_oficial, categoria) not in recuperadas:
            problemas.append(
                f"No se recuperó evidencia normativa específica "
                f"de {categoria} en la página {pagina_oficial}."
            )

    return len(problemas) == 0, problemas
