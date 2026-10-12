"""
Ejecución controlada de LangGraph desde Streamlit.

No realiza llamadas a OpenAI al importarse.
"""

import os
import re
from hmac import compare_digest
from pathlib import Path

from adaptador_streamlit import adaptar_estado


BASE_DIR = Path(__file__).resolve().parent


def ejecutar_clasificacion(
    cui: str,
    confirmado: bool = False,
    clasificador=None,
    codigo_acceso: str | None = None,
) -> dict:
    """
    Ejecuta una clasificación solamente si el usuario
    ha confirmado expresamente la operación.

    clasificador permite probar el flujo sin OpenAI.
    """

    cui = str(cui).strip()

    # 1. Validar el identificador.

    if not re.fullmatch(r"\d{7}", cui):
        raise ValueError(
            "El CUI debe contener exactamente 7 dígitos."
        )

    # 2. Exigir autorización.

    if not confirmado:
        raise PermissionError(
            "La clasificación requiere confirmación explícita."
        )

    # 3. Comprobar documentos necesarios.

    archivos = [
        BASE_DIR / "data" /
        "dataset_limpio_agente_sostenible.xlsx",

        BASE_DIR / "data" /
        "marco_bono_sostenible_peru_2021.pdf",
    ]

    for archivo in archivos:
        if not archivo.is_file():
            raise FileNotFoundError(
                f"Falta un documento requerido: {archivo.name}"
            )

    # 4. Configuración predeterminada del piloto.
    # Se respetan variables ya configuradas.

    os.environ.setdefault(
        "OPENAI_MODEL",
        "gpt-5.4-mini",
    )

    os.environ.setdefault(
        "OPENAI_JUDGE_MODEL",
        "gpt-5.4-mini",
    )

    os.environ.setdefault(
        "OPENAI_VISION_MODEL",
        "gpt-5.4-mini",
    )

    os.environ.setdefault(
        "OPENAI_EMBEDDING_MODEL",
        "text-embedding-3-small",
    )

    os.environ.setdefault(
        "MAX_AGENT_ITERATIONS",
        "3",
    )

    # 5. Importar el backend solamente cuando
    # realmente se vaya a ejecutar.

    if clasificador is None:

        if os.getenv("ENABLE_LIVE_CLASSIFICATION", "0") != "1":
            raise PermissionError(
                "La clasificacion real esta deshabilitada "
                "por configuracion del servidor."
            )

        secreto = os.getenv(
            "LIVE_CLASSIFICATION_ACCESS_CODE", ""
        )

        if len(secreto) < 12:
            raise RuntimeError(
                "No se ha configurado un codigo de acceso "
                "seguro para la clasificacion real."
            )

        if not compare_digest(
            str(codigo_acceso or ""),
            secreto,
        ):
            raise PermissionError(
                "Codigo de acceso incorrecto."
            )

        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError(
                "No se ha configurado OPENAI_API_KEY."
            )

        # Reservar antes de ejecutar llamadas pagadas.
        from control_ejecuciones import reservar_ejecucion
        reservar_ejecucion(cui)

        from graph import clasificar_cui

        clasificador = clasificar_cui

    # 6. Ejecutar el clasificador.

    final_state = clasificador(cui)

    # 7. Adaptar la respuesta a Streamlit.

    return adaptar_estado(
        cui=cui,
        final_state=final_state,
    )
