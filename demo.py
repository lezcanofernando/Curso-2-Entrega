import asyncio
import logging

from chain import process_text

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

textos = [
    # Un log de error claro.
    "El servicio de pagos usa FastAPI y PostgreSQL. Desde el último despliegue, "
    "las conexiones a la base de datos se agotan bajo carga y los pagos fallan con errores 503.",
    # Un texto ambiguo (prueba de estrés).
    "Algo anda raro con el sistema desde ayer, a veces tarda y a veces no. "
    "Alguien tocó la config pero no sabemos qué.",
]


async def main():
    for texto in textos:
        resultado = await process_text(texto)
        print(resultado.model_dump_json(indent=2))


asyncio.run(main())
