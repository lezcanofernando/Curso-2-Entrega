# Pre-entrega 2: Pipeline de extracción de entidades técnicas

Recibe un texto técnico (por ejemplo, un log de error) y devuelve un objeto validado con Pydantic, usando LangChain (LCEL) y Claude.

- `schemas.py`: modelo Pydantic de la respuesta.
- `chain.py`: prompt, modelo, cadena LCEL con reintentos y `process_text()`.
- `demo.py`: mini-script asíncrono de prueba.

## Cómo funciona

```python
chain = (
    prompt
    | model.with_structured_output(ExtraccionTecnica, include_raw=True)
    | RunnableLambda(validar_respuesta)
).with_retry(stop_after_attempt=3)
```

`validar_respuesta` lanza un error si la respuesta se cortó por tokens (`stop_reason == "max_tokens"`) o si el JSON es inválido, y `with_retry` reintenta hasta 3 veces.

## Uso

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env    # pegar la ANTHROPIC_API_KEY en .env
python demo.py
```

## Ejemplo de salida

Entrada: *"El servicio de pagos usa FastAPI y PostgreSQL. Desde el último despliegue, las conexiones a la base de datos se agotan bajo carga y los pagos fallan con errores 503."*

```json
{
  "tecnologias": ["FastAPI", "PostgreSQL"],
  "nivel_de_criticidad": "alta",
  "resumen_tecnico": "Agotamiento de conexiones a PostgreSQL tras despliegue, causando fallos en pagos con errores 503 bajo carga."
}
```

Con un texto ambiguo, sin tecnologías mencionadas, el modelo devuelve `["No identificada en el texto"]` y la respuesta igual pasa la validación.
