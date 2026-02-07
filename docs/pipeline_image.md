# Pipeline Imagen (mock)

## Objetivo
Recepcion de imagen, orquestacion basica y salida XML Dublin Core (mock editable).

## Flujo
1. Recibe imagen por `/internal/pipeline/image`.
2. Guarda archivo en storage (tipo y fecha).
3. Genera XML Dublin Core mock.
4. Guarda XML como archivo y registra metadata en `files`.

## Endpoint
`POST /internal/pipeline/image`

Campos (multipart/form-data):
- `file` (required)
- `storage_type` (optional, default `images`)
- `creator` (optional)
- `job_id` (optional)
- `user_id` (optional)

Respuesta:
- `image_file_id`, `xml_file_id`
- `xml_relative_path`
- `xml_content` (editable en cliente)

## Prueba rapida
```
curl.exe -X POST http://localhost:8000/internal/pipeline/image \
  -F "storage_type=images" \
  -F "creator=Prueba" \
  -F "file=@./docs/_build/Errores.txt"
```