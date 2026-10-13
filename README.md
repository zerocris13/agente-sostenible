# Evaluador de Proyectos Sostenibles

Sistema multiagente para la clasificación preliminar de proyectos de inversión pública según el **Marco del Bono Sostenible del Perú (2021)**.

Proyecto académico grupal desarrollado con Python, LangGraph, modelos de OpenAI, recuperación aumentada por generación (RAG) y Streamlit.

## Aplicación desplegada

https://agente-sostenible-jhm8ig5ry93v9ogdr9ltam.streamlit.app/

La aplicación permite consultar proyectos por su Código Único de Inversión (CUI), visualizar informes existentes y, cuando está habilitado y autorizado, ejecutar nuevas evaluaciones.

## Arquitectura

El sistema integra los siguientes componentes:

1. **Recuperación de información:** obtiene los datos del proyecto de inversión y sus brechas asociadas.
2. **Agente ReAct:** selecciona y utiliza herramientas para reunir evidencia.
3. **RAG normativo:** recupera información pertinente del Marco del Bono Sostenible del Perú (2021).
4. **Procesamiento multimodal adaptativo:** puede analizar imágenes de marcos lógicos cuando el agente considera necesario utilizar esa evidencia.
5. **Clasificación:** propone una categoría y un criterio normativo cuando la evidencia lo permite.
6. **Validación y verificación:** comprueba la sustentación documental y determina si corresponde revisión humana.
7. **Interfaz Streamlit:** presenta la clasificación, evidencias, trazabilidad y auditoría multimodal.

La presencia de imágenes no garantiza que el agente las consulte. La interfaz distingue disponibilidad documental, invocación de la herramienta visual, procesamiento y evidencia registrada.

## Tecnologías

- Python
- LangGraph y LangChain
- OpenAI GPT-5.4-mini
- Embeddings para recuperación normativa
- Streamlit
- Pandas y OpenPyXL

## Estructura principal

- `streamlit_app.py`: interfaz web.
- `ejecutor_streamlit.py`: ejecución autorizada de clasificaciones.
- `adaptador_streamlit.py`: adaptación de resultados y auditoría multimodal.
- `graph.py`: orquestación de la clasificación, validación y verificación.
- `agent.py`: agente ReAct con herramientas.
- `toolbox.py`: consulta de proyectos, recuperación normativa y análisis visual.
- `control_ejecuciones.py`: límites de ejecución.
- `data/`: documentos y datos utilizados en el proyecto.

## Datos

El archivo `data/dataset_limpio_agente_sostenible.xlsx` contiene cuatro hojas:

- `README`: documentación del dataset.
- `PROYECTOS`: información de 423 proyectos identificados por CUI.
- `BRECHAS`: 640 registros de brechas.
- `GROUND_TRUTH`: etiquetas históricas para evaluación.

**Importante:** `GROUND_TRUTH` no debe incorporarse al contexto de inferencia del agente. Se utiliza exclusivamente para comparar las predicciones después de ejecutar la evaluación.

El dataset contiene decisiones de limpieza y supuestos operativos documentados en su hoja `README`, incluidos los relacionados con el valor 85 y los casos de etiquetas históricas en conflicto.

## Evaluación experimental

La versión evaluada utilizó GPT-5.4-mini, un máximo de tres iteraciones externas, un límite de recursión de 16 pasos para el grafo principal y 20 pasos para el agente ReAct.

En una muestra exploratoria estratificada de diez proyectos con etiquetas históricas de 2021 se obtuvieron:

| Indicador | Resultado |
|---|---:|
| Coincidencia con categoría histórica | 10/10 (100 %) |
| Macro-F1 | 1.000 |
| Cobertura autónoma | 5/10 (50 %) |
| Casos que solicitaron revisión humana | 5/10 (50 %) |
| Fallos técnicos | 0/10 |
| Latencia media | 60.8 segundos |

Estos resultados no constituyen una estimación representativa de todos los proyectos. La muestra es pequeña y se seleccionó sin imágenes de marco lógico para controlar los costos.

La coincidencia con una categoría histórica no equivale a una certificación oficial de elegibilidad. La calidad del RAG y el procesamiento multimodal requieren evaluaciones específicas.

## Ejecución local

Crear un entorno virtual e instalar las dependencias:

```bash
python -m venv .venv
pip install -r requirements.txt
```

Ejecutar la interfaz:

```bash
streamlit run streamlit_app.py
```

Para habilitar clasificaciones reales se necesita configurar las credenciales y controles de ejecución correspondientes en variables de entorno o secretos privados del despliegue.

**Nunca publicar claves de OpenAI ni códigos de autorización.** La consulta de informes existentes no requiere ejecutar una nueva clasificación pagada.

## Seguridad

Las evaluaciones en vivo están restringidas mediante autorización explícita y límites de solicitudes.

Los resultados nuevos guardados en el sistema de archivos local de Streamlit Cloud pueden desaparecer al reiniciar o reemplazar la instancia. Este almacenamiento no constituye persistencia garantizada.

## Uso y limitaciones

Este sistema es una herramienta académica de apoyo a la evaluación documental. Sus resultados son preliminares y no sustituyen la revisión de especialistas ni constituyen una aprobación oficial o certificación financiera.

La procedencia, atribución y los permisos de redistribución del dataset, el PDF normativo y las imágenes deben verificarse antes de distribuir públicamente esos materiales.

No se ha establecido todavía una licencia de reutilización para el repositorio.
