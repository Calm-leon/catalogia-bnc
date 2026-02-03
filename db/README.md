# Migrations

Las migraciones viven en `db/migrations/` y se aplican en orden numerico.

Ejemplo (desde la carpeta del repo, con contenedores arriba):
```bash
docker compose exec -T db psql -U catalogia -d catalogia -f /migrations/001_create_users.sql
docker compose exec -T db psql -U catalogia -d catalogia -f /migrations/002_create_jobs.sql
docker compose exec -T db psql -U catalogia -d catalogia -f /migrations/003_create_logs.sql
```

Nota: No se incluyen datos mock permanentes.