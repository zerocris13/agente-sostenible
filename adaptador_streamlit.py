"""
Adaptador de resultados LangGraph a Streamlit.

No ejecuta modelos ni realiza llamadas a OpenAI.
"""


def convertir_a_dict(valor):
    """Convierte modelos Pydantic o diccionarios."""

    if valor is None:
        return {}

    if hasattr(valor, "model_dump"):
        return valor.model_dump(mode="json")

    if isinstance(valor, dict):
        return valor

    raise TypeError(
        f"Tipo de resultado no compatible: {type(valor).__name__}"
    )


def adaptar_estado(cui: str, final_state: dict) -> dict:
    """
    Adapta el estado final de LangGraph al formato
    de los expedientes utilizados en Streamlit.
    """

    if not isinstance(final_state, dict):
        raise TypeError("final_state debe ser un diccionario.")

    resultado = convertir_a_dict(
        final_state.get("resultado")
    )

    if not resultado:
        raise ValueError(
            "LangGraph no devolvio un resultado final."
        )

    veredicto = convertir_a_dict(
        final_state.get("veredicto")
    )

    trayectoria = final_state.get(
        "trajectory",
        final_state.get("trayectoria", []),
    ) or []

    if not isinstance(trayectoria, list):
        raise TypeError("La trayectoria debe ser una lista.")

    # No trasladamos dossier, tool_outputs ni otros
    # contenidos internos extensos al frontend.

    llamadas = []

    for llamada in final_state.get("tool_calls", []) or []:

        if isinstance(llamada, dict):
            nombre = llamada.get("name") or llamada.get("tool")

            if nombre:
                llamadas.append({"name": str(nombre)})

    return {
        "cui": str(cui),
        "resultado": resultado,
        "trayectoria": trayectoria,
        "veredicto": veredicto,
        "tool_calls": llamadas,
        "consultas_marco": (
            final_state.get("consultas_marco") or []
        ),
    }
