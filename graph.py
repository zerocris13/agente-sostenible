"""
LangGraph de clasificación con feedback y autocorrección.

Flujo:
START -> agente_evidencia -> clasificador -> validacion_determinista
      -> verificador_semantico -> APROBADO
                           -> feedback -> agente_evidencia (loop)
                           -> REVISION_HUMANA al llegar al límite
"""

from __future__ import annotations

import json
import os
from typing import TypedDict
from functools import lru_cache
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from agent import ejecutar_agente_evidencia
from guardrails import (
    validar_candidato_basico,
    validar_citas_recuperadas,
    validar_cui,
    obtener_alertas_documentales,
)
from schemas import (
    ClasificacionPropuesta,
    ResultadoFinal,
    VeredictoVerificador,
)

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-terra")
JUDGE_MODEL = os.getenv("OPENAI_JUDGE_MODEL", MODEL)
MAX_ITERACIONES = int(os.getenv("MAX_AGENT_ITERATIONS", "3"))


class AgentState(TypedDict, total=False):
    cui: str
    iteracion: int
    feedback: str
    dossier: str
    tool_calls: list[dict]
    consultas_marco: list[str]
    tool_outputs: list[dict]
    candidato: dict
    validacion_ok: bool
    problemas_validacion: list[str]
    veredicto: dict
    resultado: dict
    trajectory: list[dict]
    alertas_documentales: list[str]


# Actualicé _classifier_model y _judge_model
@lru_cache(maxsize=1)
def get_classifier_model():
    return ChatOpenAI(
        model=MODEL,
        use_responses_api=True,
        reasoning_effort="medium",
    ).with_structured_output(ClasificacionPropuesta)


@lru_cache(maxsize=1)
def get_judge_model():
    return ChatOpenAI(
        model=JUDGE_MODEL,
        use_responses_api=True,
        reasoning_effort="medium",
    ).with_structured_output(VeredictoVerificador)



def nodo_agente(state: AgentState) -> dict:
    cui = validar_cui(state["cui"])
    iteracion = state.get("iteracion", 0) + 1

    run = ejecutar_agente_evidencia(
        cui=cui,
        feedback=state.get("feedback", ""),
    )

    alertas_documentales = list(dict.fromkeys(
        list(state.get("alertas_documentales", []))
        + obtener_alertas_documentales(run["tool_outputs"])
    ))

    trajectory = list(state.get("trajectory", []))
    trajectory.append(
        {
            "iteracion": iteracion,
            "fase": "agente_evidencia",
            "tool_calls": run["tool_calls"],
            "consultas_marco": run["consultas_marco"],
        }
    )

    return {
        "cui": cui,
        "iteracion": iteracion,
        "dossier": run["dossier"],
        "tool_calls": list(state.get("tool_calls", [])) + run["tool_calls"],
        "consultas_marco": list(state.get("consultas_marco", [])) + run["consultas_marco"],
        "tool_outputs": (
            list(state.get("tool_outputs", []))
            + list(run["tool_outputs"])
        ),
        "trajectory": trajectory,
        "feedback": "",
        "alertas_documentales": alertas_documentales,
    }
    # cambié tools para que el clasificador y el verificador podrán consultar hasta las doce salidas más recientes


def _contexto_tools(state: AgentState) -> str:
    bloques = []
    for item in state.get("tool_outputs", []):
        content = item.get("content", "")
        # Límite defensivo para evitar que una tool monopolice el contexto.
        if len(content) > 15000:
            content = content[:15000] + "\n[TRUNCADO]"
        bloques.append(f"TOOL: {item.get('tool')}\n{content}")
    return "\n\n".join(bloques)


def nodo_clasificador(state: AgentState) -> dict:
    prompt = f"""
Clasifica el CUI {state['cui']} exclusivamente a partir de la evidencia recuperada
por el agente y el Marco 2021.

DOSSIER DEL AGENTE
------------------
{state.get('dossier', '')}

SALIDAS DE TOOLS
----------------
{_contexto_tools(state)}

REGLAS
- No uses conocimiento sobre clasificaciones históricas.
- Distingue evidencia del proyecto de criterio normativo.
- Una palabra clave por sí sola no basta: debe existir correspondencia material
  entre la intervención y el criterio del Marco.
- Si existe ambigüedad relevante entre dos categorías y no puede resolverse,
  usa "Información insuficiente".
- "No aplica" significa que hay información suficiente para concluir que no
  corresponde a ninguna categoría verde del Marco.
- Cita solo páginas realmente recuperadas.
- No inventes información.

- Distingue la certeza de la categoría general de la certeza del criterio
  específico. No confundas ambas decisiones.
- Si la evidencia respalda una categoría, pero existe ambigüedad entre dos
  criterios de esa misma categoría, conserva la categoría sustentada y
  registra expresamente la incertidumbre sobre el criterio específico.
- En proyectos forestales, distingue USCUSS-6 (plantaciones forestales
  comerciales) de USCUSS-7 (plantaciones forestales con fines de protección
  y/o restauración).
- La palabra "producción" no demuestra por sí sola finalidad comercial;
  una brecha de recuperación de ecosistemas tampoco demuestra por sí sola
  que la plantación tenga una finalidad exclusiva de restauración.
- Selecciona un criterio principal específico únicamente cuando los datos
  recuperados permitan justificar su correspondencia material.
- Si el criterio específico sigue siendo incierto, explica las alternativas
  y marca requiere_revision_humana=True. No presentes un criterio dudoso
  como si estuviera confirmado.
- No extiendas los requisitos de las notas 45, 46 y 47 del Marco 2021 a
  actividades distintas de los apartados a los que pertenecen.
- No expongas cadena de pensamiento; la justificación debe ser breve y auditable.
"""

    candidato = get_classifier_model().invoke(prompt)
    payload = candidato.model_dump()

    # Comprobar si existe una extracción multimodal válida.
    marco_logico_procesado = False

    for item in state.get("tool_outputs", []):
        if item.get("tool") != "consultar_marco_logico":
            continue

        try:
            contenido = item.get("content", "")
            datos = (
                json.loads(contenido)
                if isinstance(contenido, str)
                else contenido
            )
        except (json.JSONDecodeError, TypeError):
            continue

        if (
            isinstance(datos, dict)
            and datos.get("procesado") is True
            and datos.get("encontrado") is not False
        ):
            marco_logico_procesado = True
            break

    # No aceptar evidencia de imágenes que no se procesaron.
    if not marco_logico_procesado:
        payload["evidencia_marco_logico"] = []

    return {"candidato": payload}




def nodo_validacion(state: AgentState) -> dict:
    # 1. Validación estructural y de evidencia.
    ok_basico, problemas_basicos = validar_candidato_basico(
        state["candidato"],
        state["cui"],
    )

    # 2. Validación de trazabilidad normativa.
    ok_citas, problemas_citas = validar_citas_recuperadas(
        state["candidato"],
        state.get("tool_outputs", []),
    )

    # La propuesta solo pasa si supera ambas validaciones.
    ok = ok_basico and ok_citas

    problemas = list(dict.fromkeys(
        problemas_basicos + problemas_citas
    ))

    trajectory = list(state.get("trajectory", []))
    trajectory.append({
        "iteracion": state.get("iteracion", 0),
        "fase": "validacion_determinista",
        "aprobado": ok,
        "validacion_basica_ok": ok_basico,
        "validacion_citas_ok": ok_citas,
        "problemas": problemas,
    })

    if not ok:
        return {
            "validacion_ok": False,
            "problemas_validacion": problemas,
            "feedback": (
                "Corrige estos problemas formales y evidenciales: "
                + "; ".join(problemas)
            ),
            "trajectory": trajectory,
        }

    return {
        "validacion_ok": True,
        "problemas_validacion": [],
        "feedback": "",
        "trajectory": trajectory,
    }



def ruta_post_validacion(state: AgentState) -> str:
    if state.get("validacion_ok"):
        return "verificador"
    if state.get("iteracion", 0) >= MAX_ITERACIONES:
        return "revision_humana"
    return "agente"


def nodo_verificador(state: AgentState) -> dict:
    prompt = f"""
Actúa como verificador independiente de evidencia normativa.

CUI: {state['cui']}

CANDIDATO
---------
{json.dumps(state['candidato'], ensure_ascii=False, indent=2)}

DOSSIER
-------
{state.get('dossier', '')}

EVIDENCIA RECUPERADA
--------------------
{_contexto_tools(state)}

Evalúa únicamente:
1. Si la categoría propuesta está sustentada por los hechos recuperados.
2. Si los criterios normativos citados corresponden al Marco 2021 recuperado.
3. Si la conclusión va más allá de la evidencia.
4. Si debería abstenerse por información insuficiente.
5. Si existe una categoría alternativa que deba contrastarse antes de cerrar.

CRITERIOS DE AUDITORÍA NORMATIVA
- Evalúa por separado la correspondencia de la categoría y la del
  criterio principal seleccionado.
- Si la categoría está sustentada, pero el criterio específico no puede
  determinarse, establece categoria_sustentada=True. Explica la
  incertidumbre y solicita revisión cuando afecte la aprobación.
- No rechaces la categoría general únicamente porque existen dos
  criterios plausibles dentro de ella.
- Verifica el alcance de cada nota normativa antes de exigir documentos.
  En la página 36 del Marco 2021:
  * La nota 45 corresponde al apartado i, manejo comercial sostenible
    de bosques naturales, y exige certificación FSC o PEFC.
  * La nota 46 corresponde al apartado ii, programas de conservación y
    restauración de bosques nativos y exóticos, y señala Plan de Manejo
    Forestal o certificación FSC/PEFC.
  * La nota 47 corresponde al apartado iii, gestión y mantenimiento de
    parques nacionales y áreas de conservación.
- No presupongas que estas tres notas se aplican automáticamente a
  cualquier proyecto USCUSS-6 o USCUSS-7.
- Distingue los requisitos expresamente establecidos en la disposición
  aplicable de la documentación adicional que sería útil para resolver
  una incertidumbre técnica.
- Para USCUSS-6 y USCUSS-7, contrasta la finalidad comercial frente a la
  finalidad de protección o restauración. Si no puede determinarse,
  conserva la revisión humana y explica qué información permitiría
  resolverla.
No uses ground truth, reportes de asignación ni conocimiento histórico del proyecto.
No expongas cadena de pensamiento. Entrega problemas concretos y feedback accionable.
"""
    veredicto = get_judge_model().invoke(prompt)
    payload = veredicto.model_dump()

    trajectory = list(state.get("trajectory", []))
    trajectory.append(
        {
            "iteracion": state.get("iteracion", 0),
            "fase": "verificador_semantico",
            "aprobado": payload["aprobado"],
            "categoria_sustentada": payload["categoria_sustentada"],
            "evidencia_suficiente": payload["evidencia_suficiente"],
            "problemas": payload["problemas"],
            "feedback": payload["feedback_para_agente"],
            "siguiente_accion": (
                "finalizar" if payload["aprobado"]
                else (
                    "revision_humana"
                    if state.get("iteracion", 0) >= MAX_ITERACIONES
                    else "replanificar"
                )
            ),
        }
    )

    return {
        "veredicto": payload,
        "feedback": payload["feedback_para_agente"] if not payload["aprobado"] else "",
        "trajectory": trajectory,
    }


def ruta_post_verificador(state: AgentState) -> str:
    if state["veredicto"].get("aprobado"):
        return "finalizar"
    if state.get("iteracion", 0) >= MAX_ITERACIONES:
        return "revision_humana"
    return "agente"


def _final_common(state: AgentState, estado: str) -> dict:
    cand = dict(state["candidato"])
    alertas = list(state.get("alertas_documentales", []))
    cand["requiere_revision_humana"] = bool(
        cand.get("requiere_revision_humana")
        or alertas
    )
    tools = [x.get("name") for x in state.get("tool_calls", []) if x.get("name")]
    resultado = ResultadoFinal(
        **cand,
        estado=estado,
        iteraciones=state.get("iteracion", 0),
        herramientas_utilizadas=list(dict.fromkeys(tools)),
        consultas_marco=list(dict.fromkeys(state.get("consultas_marco", []))),
        alertas_documentales=alertas,
    )
    return {"resultado": resultado.model_dump()}

# Cambié en nodo_finalizar para que "APROBADO" signifique que el sistema completó satisfactoriamente su revisión preliminar,
# no que el proyecto fue declarado oficialmente sostenible.

def nodo_finalizar(state: AgentState) -> dict:
    candidato = state["candidato"]
    veredicto = state.get("veredicto", {})
    alertas = state.get("alertas_documentales", [])

    requiere_revision = (
        candidato.get("requiere_revision_humana", False)
        or candidato.get("evidencia_suficiente") is not True
        or candidato.get("clasificacion") == "Información insuficiente"
        or veredicto.get("aprobado") is not True
        or veredicto.get("categoria_sustentada") is not True
        or veredicto.get("evidencia_suficiente") is not True
        or bool(alertas)
    )

    estado = (
        "REVISION_HUMANA"
        if requiere_revision
        else "APROBADO"
    )

    return _final_common(state, estado)



def nodo_revision_humana(state: AgentState) -> dict:
    cand = dict(state["candidato"])
    cand["requiere_revision_humana"] = True
    if not cand.get("evidencia_suficiente"):
        cand["clasificacion"] = "Información insuficiente"
    tmp = dict(state)
    tmp["candidato"] = cand
    return _final_common(tmp, "REVISION_HUMANA")


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("agente", nodo_agente)
    workflow.add_node("clasificador", nodo_clasificador)
    workflow.add_node("validacion", nodo_validacion)
    workflow.add_node("verificador", nodo_verificador)
    workflow.add_node("finalizar", nodo_finalizar)
    workflow.add_node("revision_humana", nodo_revision_humana)

    workflow.add_edge(START, "agente")
    workflow.add_edge("agente", "clasificador")
    workflow.add_edge("clasificador", "validacion")

    workflow.add_conditional_edges(
        "validacion",
        ruta_post_validacion,
        {
            "verificador": "verificador",
            "agente": "agente",
            "revision_humana": "revision_humana",
        },
    )

    workflow.add_conditional_edges(
        "verificador",
        ruta_post_verificador,
        {
            "finalizar": "finalizar",
            "agente": "agente",
            "revision_humana": "revision_humana",
        },
    )

    workflow.add_edge("finalizar", END)
    workflow.add_edge("revision_humana", END)

    return workflow.compile()


GRAPH = build_graph()


def clasificar_cui(cui: str) -> dict:
    final_state = GRAPH.invoke(
        {
            "cui": validar_cui(cui),
            "iteracion": 0,
            "feedback": "",
            "tool_calls": [],
            "consultas_marco": [],
            "trajectory": [],
        }
    )
    return final_state
