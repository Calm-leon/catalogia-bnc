# Storage

## Estructura de directorios
Los archivos se guardan en `STORAGE_PATH` con la estructura:
```
{tipo}/{YYYY}/{MM}/{DD}/{uuid}.{ext}
```
- `tipo`: valor recibido en `storage_type` (normalizado a minusculas y guiones bajos).
- `uuid`: identificador unico para trazabilidad.
- `ext`: extension del archivo original (si existe).

Ejemplo:
```
images/2026/02/04/4b2b1c6c8c7b4a5f9a8f3c2d1e0a9b7c.jpg
```

## Metadata en BD
Solo se guarda metadata en la tabla `files`:
- `storage_type`, `original_name`, `stored_name`, `relative_path`
- `content_type`, `size_bytes`, `job_id`, `user_id`

No se guardan binarios en la base de datos.

## Prueba con archivo dummy
```
curl -X POST http://localhost:8000/internal/storage/upload \
  -F "storage_type=images" \
  -F "file=@./docs/_build/Errores.txt"
```