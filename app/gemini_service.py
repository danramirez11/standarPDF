import os
import json

from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv(
        "GEMINI_API_KEY"
    )
)

prompt_base = f"""
Eres un sistema especializado en normalización de fichas técnicas de envases, tapas y productos de empaque.

Tu tarea es transformar la información extraída de un PDF en una estructura JSON estandarizada.

REGLAS IMPORTANTES:

1. Conserva exactamente todos los datos técnicos.
2. No inventes información.
3. No resumas información.
4. No traduzcas información.
5. Mantén los valores exactamente como aparecen en el documento.
6. Si una sección parece una tabla, conviértela a formato de tabla.
7. Si una sección parece texto descriptivo, conviértela a formato de texto.
8. El título de una sección es opcional.
9. Algunas tablas o textos pueden no tener título.
10. El nombre del producto debe ubicarse en header.productName.
11. Los datos generales del encabezado deben ubicarse en header.fields.
12. Ignora completamente firmas, aprobaciones, responsables, revisiones, sellos internos y nombres de empleados.
13. Ignora secciones como:

    * Elaboró
    * Revisó
    * Aprobó
    * Nombre y firma
    * Cargo
    * Control de calidad
    * Firmas
    * Sellos
14. No incluyas información relacionada con proveedores o personal interno.
15. Devuelve únicamente JSON válido.
16. No envuelvas la respuesta en markdown.

Utiliza exactamente esta estructura:
"""

schema = {
    "header": {
        "productName": "string",
        "fields": [
            {
            "label": "string",
            "value": "string"
            }
        ]
    },
    "sections": [
        {
        "type": "table",
        "title": "string opcional",
        "rows": [
            ["columna1", "columna2"]
            ]
        },
        {
        "type": "text",
        "title": "string opcional",
        "content": "string"
        }
    ]
}


def normalize_document(
    extracted_document
):

    prompt = f"""
        {prompt_base}
        {json.dumps(schema, ensure_ascii=False)}
        
        Este es el documento extraído:
        {json.dumps(extracted_document, ensure_ascii=False)}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",

        contents=prompt,

        config={
            "response_mime_type":
                "application/json"
        }
    )
    return json.loads(
        response.text
    )