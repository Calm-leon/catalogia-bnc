# CI/CD Basico

## Objetivo
Automatizar validaciones de calidad sin desplegar a produccion.

## Pipeline
Archivo: `.github/workflows/ci.yml`

Jobs incluidos:
- `Backend Lint and Tests`: instala dependencias Python, ejecuta `ruff` y `pytest`.
- `Frontend Lint and Build`: instala dependencias Node, corre `npm run lint` y `npm run build`.
- `Validate SQL Migrations`: levanta Postgres temporal y aplica migraciones SQL.
- `Validate Docker Compose`: ejecuta `docker compose config`.

## Criterio de fallo rapido
Cada job falla en el primer error de su bloque.

## Alcance actual
- Sin despliegue automatico.
- Enfocado en PRs y pushes a `develop`.

## Evidencias esperadas en PR
- Log de job backend en verde.
- Log de job frontend en verde.
- Log de migraciones aplicadas sin error.
- Log de validacion de compose sin error.
