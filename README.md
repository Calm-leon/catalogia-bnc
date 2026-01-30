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
- No hay logica de IA ni modelos en esta version.