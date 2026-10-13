"""
Adaptador de resultados LangGraph a Streamlit.

No ejecuta modelos ni realiza llamadas a OpenAI.
"""


import json


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


    # Auditoría compacta: no exponer respuestas extensas.
    invocaciones_vision = sum(
        x["name"] == "consultar_marco_logico"
        for x in llamadas
    )

    extracciones_completadas = 0
    archivos_visuales = []

    for salida in final_state.get("tool_outputs", []) or []:
        if not isinstance(salida, dict):
            continue

        if salida.get("tool") != "consultar_marco_logico":
            continue

        contenido = salida.get("content")

        try:
            datos = (
                json.loads(contenido)
                if isinstance(contenido, str)
                else contenido
            )
        except (ValueError, TypeError):
            continue

        if not isinstance(datos, dict):
            continue

        if datos.get("procesado") is True:
            extracciones_completadas += 1

            for nombre in datos.get("archivos_analizados") or []:
                if (
                    isinstance(nombre, str)
                    and nombre not in archivos_visuales
                ):
                    archivos_visuales.append(nombre)

    evidencias = resultado.get("evidencia_marco_logico") or []

    auditoria_multimodal = {
        "invocaciones_vision": invocaciones_vision,
        "extracciones_completadas": extracciones_completadas,
        "procesado": extracciones_completadas > 0,
        "archivos_analizados": archivos_visuales,
        "evidencia_visual_registrada": bool(evidencias),
    }

    return {
        "cui": str(cui),
        "resultado": resultado,
        "trayectoria": trayectoria,
        "veredicto": veredicto,
        "tool_calls": llamadas,
        "auditoria_multimodal": auditoria_multimodal,
        "consultas_marco": (
            final_state.get("consultas_marco") or []
        ),
    }
