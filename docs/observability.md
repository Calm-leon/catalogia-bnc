# Observabilidad y metricas

## Logging estructurado
El backend emite logs en JSON con campos:
- `timestamp`
- `level`
- `message`
- `logger`

## Metricas basicas
- `pipeline.total_runs`
- `pipeline.last_run_ts`
- `xml_quality.last_xml_size`
- `xml_quality.fields_present`

## Endpoint interno
`GET /internal/metrics`

Requiere token `admin` o `cataloger`:
```
Authorization: Bearer <TOKEN>
```

## Prueba rapida
1) Ejecutar pipeline:
```
curl.exe -X POST http://localhost:8000/internal/pipeline/image \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -F "storage_type=images" \
  -F "creator=Prueba" \
  -F "file=@./docs/_build/Errores.txt"
```

2) Consultar metricas:
```
curl.exe -X GET http://localhost:8000/internal/metrics \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```