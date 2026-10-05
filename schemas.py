from enum import Enum

from pydantic import BaseModel, Field


class NivelCriticidad(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


class ExtraccionTecnica(BaseModel):
    """Forma que debe tener la respuesta del modelo."""

    tecnologias: list[str] = Field(
        min_length=1,  # la lista no puede estar vacía
        description="Tecnologías mencionadas en el texto.",
    )
    nivel_de_criticidad: NivelCriticidad = Field(
        description="Criticidad del problema: baja, media o alta.",
    )
    resumen_tecnico: str = Field(
        min_length=10,
        description="Resumen técnico breve, en español.",
    )
