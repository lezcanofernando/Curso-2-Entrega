import logging

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from schemas import ExtraccionTecnica

load_dotenv()  # lee ANTHROPIC_API_KEY del archivo .env

logger = logging.getLogger(__name__)

# 1. Prompt con dos variables que LangChain completa en cada llamada:
#    {instrucciones_formato} y {texto}.
prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un analista de software. Extrae información técnica del texto, "
               "sin inventar datos.\n{instrucciones_formato}"),
    ("human", "{texto}"),
])

INSTRUCCIONES_FORMATO = """Criticidad: alta = caída o falla en producción; media = errores parciales o lentitud; baja = sin impacto.
Si no se menciona ninguna tecnología, responde ["No identificada en el texto"].
El resumen técnico debe ser breve y en español."""

# 2. Modelo de Anthropic.
model = ChatAnthropic(model="claude-sonnet-4-5", max_tokens=800)


def validar_respuesta(respuesta):
    """Revisa la respuesta del modelo. Si algo está mal, lanza un error y with_retry reintenta."""
    # stop_reason == "max_tokens" significa que la respuesta se cortó por falta de tokens.
    if respuesta["raw"].response_metadata.get("stop_reason") == "max_tokens":
        logger.warning("Respuesta incompleta (se cortó por tokens). Reintentando...")
        raise ValueError("Respuesta incompleta")

    # parsing_error tiene un valor si el JSON no cumple con el esquema de schemas.py.
    if respuesta["parsing_error"]:
        logger.warning("JSON inválido: %s. Reintentando...", respuesta["parsing_error"])
        raise ValueError("JSON inválido")

    logger.info("Respuesta validada correctamente.")
    return respuesta["parsed"]


# 3. Cadena LCEL: prompt -> modelo con salida estructurada -> validación.
#    include_raw=True devuelve también el mensaje original, para poder ver el stop_reason.
# 4. with_retry: si algún paso falla, repite la cadena (hasta 3 intentos).
chain = (
    prompt
    | model.with_structured_output(ExtraccionTecnica, include_raw=True)
    | RunnableLambda(validar_respuesta)
).with_retry(stop_after_attempt=3)


# 5. Función asíncrona que ejecuta la cadena.
async def process_text(text: str) -> ExtraccionTecnica:
    logger.info("Procesando texto...")
    return await chain.ainvoke({"texto": text, "instrucciones_formato": INSTRUCCIONES_FORMATO})
