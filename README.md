# CatalogIA

Bootstrap tecnico del monolito orquestado para CatalogIA.

## Estructura
- backend: FastAPI
- frontend: Next.js
- db: recursos de base de datos (placeholder)
- storage: almacenamiento de archivos
- docs: documentacion

## Requisitos
- Docker y Docker Compose

## Arranque rapido
```bash
docker compose up --build
```

Servicios:
- Backend: http://localhost:8000/health
- Frontend: http://localhost:3000
- Postgres: localhost:5432 (usuario: catalogia, clave: catalogia, db: catalogia)

## Notas
- El backend expone `/health` con verificacion de base de datos.
- Motor IA intercambiable habilitado: `mock`, `openai`, `azure`, `local`.

## Frontend MVP (iteracion 1)
- Configura `NEXT_PUBLIC_BACKEND_URL` para que el navegador llame al backend.
  - Ejemplo local: `http://localhost:8000`
- Flujo minimo habilitado:
  1. Ir a `/login` e ingresar un token valido (ejemplo: `CATALOGER_TOKEN`).
  2. Ir a `/upload`, subir archivo y ejecutar pipeline.
  3. Ir a `/xml` para visualizar el XML real de la ultima ejecucion en sesion.

### Variable de entorno frontend
- `NEXT_PUBLIC_BACKEND_URL`: URL publica del backend para requests desde navegador.
- Compatibilidad temporal: tambien se acepta `NEXT_PUBLIC_API_BASE_URL`.

### Prueba manual sugerida
1. Levantar stack con `docker compose up --build`.
2. Confirmar backend en `http://localhost:8000/health`.
3. Abrir frontend en `http://localhost:3000/login`.
4. Ingresar token catalogador.
5. Ejecutar upload en `/upload` y validar respuesta de exito.
6. Abrir `/xml` y validar que renderiza `xml_content` retornado por backend.
7. Abrir `/select` y validar historial + detalle de job (calidad/logs/files).

## Hardening MVP (iteracion 6)
Variables de entorno:
- `SECURITY_HEADERS_ENABLED=true|false`
- `SECURITY_CSP`
- `SECURITY_HSTS_ENABLED=true|false`
- `RATE_LIMIT_ENABLED=true|false`
- `RATE_LIMIT_WINDOW_SECONDS`
- `RATE_LIMIT_PIPELINE_IMAGE_PER_MINUTE` (default 5)
- `RATE_LIMIT_LOGS_PER_MINUTE` (default 60)

Rate limit sensible:
- `POST /internal/pipeline/image`
- `POST /internal/logs`

## Pruebas
Backend (incluye e2e y hardening):
```bash
cd backend
pytest
```

Frontend:
```bash
cd frontend
npm run lint
npm run build
npm test -- --runInBand app/upload/page.test.tsx app/xml/page.test.tsx app/select/page.test.tsx
```
