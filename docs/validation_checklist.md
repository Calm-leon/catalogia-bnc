# Checklist de validacion continua

## Antes de cada ejecucion
- [ ] Verificar servicios activos
  - `docker compose ps`
- [ ] Ejecutar tests existentes
  - Backend: `cd backend` y `pytest`
  - Frontend: (pendiente de definir)
- [ ] Confirmar compatibilidad
  - No romper endpoints existentes
  - No cambiar contratos sin documentar

## Despues de cada ejecucion
- [ ] Revisar logs
  - `docker compose logs --tail 100 backend`
  - `docker compose logs --tail 100 frontend`
- [ ] Validar endpoints
  - `GET http://localhost:8000/health`
  - `POST http://localhost:8000/internal/logs`
  - `POST http://localhost:8000/internal/storage/upload`
  - `POST http://localhost:8000/internal/pipeline/image`
- [ ] Confirmar frontend funcional
  - `http://localhost:3000/`
  - `http://localhost:3000/login`
  - `http://localhost:3000/select`
  - `http://localhost:3000/upload`
  - `http://localhost:3000/xml`

## Reglas
- Si algo falla, NO continuar.
- Corregir antes de avanzar.

## Notas
- Tests backend basicos disponibles en `backend/tests`.
- Reemplazar los tests pendientes cuando se definan suites completas.