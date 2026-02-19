# Documentacion de Codigo Avanzado (Estado Actual)

Fecha de corte: 2026-02-18

## 1. Vision tecnica
CatalogIA evoluciono de un pipeline mock a un flujo trazable con revision XML y motor IA intercambiable con soporte multimodal.

## 2. Modulos principales
## Backend
- API principal: `backend/app/main.py`
- Persistencia: `backend/app/db.py`
- Seguridad/autorizacion: `backend/app/auth.py`, `backend/app/security.py`
- Pipeline de imagen: `backend/app/pipeline/image.py`
- Almacenamiento local: `backend/app/storage.py`
- Motor IA:
  - contrato: `backend/app/ai/base.py`
  - factory: `backend/app/ai/factory.py`
  - proveedores: `backend/app/ai/mock_engine.py`, `backend/app/ai/openai_engine.py`, `backend/app/ai/azure_engine.py`, `backend/app/ai/local_engine.py`
  - builder RDF DC: `backend/app/dublin_core_xml.py`

## Frontend
- Login/token: `frontend/app/login/page.tsx`
- Upload/pipeline: `frontend/app/upload/page.tsx`
- Revision XML: `frontend/app/xml/page.tsx`
- Cliente utilitario: `frontend/app/lib/catalogia.ts`

## 3. Capacidades implementadas
- Ciclo de vida de jobs:
  - creacion automatica
  - estados `queued/running/completed/failed`
- Trazabilidad:
  - archivos y logs ligados a `job_id`
- Revision XML:
  - formulario editable
  - guardado de version revisada `*_reviewed.xml`
  - normalizacion de nombre revisado para evitar cadenas repetidas
- IA:
  - seleccion por entorno de proveedor real o mock
  - timeout/retry configurables
  - fallback a mock controlado y restringido
  - envio de imagen al proveedor (multimodal) cuando aplica

## 4. Pruebas existentes
- Backend:
  - `backend/tests/test_health.py`
  - `backend/tests/test_logs.py`
  - `backend/tests/test_pipeline_jobs.py`
  - `backend/tests/test_xml_revision.py`
  - `backend/tests/test_ai_engine.py`
- Frontend:
  - `frontend/app/upload/page.test.tsx`
  - `frontend/app/xml/page.test.tsx`
- Evidencia adicional:
  - `docs/_build/test_frontend_iter3.log`

## 5. Referencias funcionales
- Flujo pipeline: `docs/pipeline_image.md`
- Motor IA: `docs/ai_engine.md`
- Seguridad y acceso: `docs/security_access.md`
- Observabilidad: `docs/observability.md`
- Storage: `docs/storage.md`
- Checklist validacion: `docs/validation_checklist.md`
- CI/CD: `docs/ci_cd.md`

## 6. Brechas tecnicas pendientes
- Cobertura E2E integral de cierre MVP.
- Reglas de calidad semantica avanzadas para metadata.
- Endurecimiento de seguridad final (rate-limit/politicas operativas de produccion).

