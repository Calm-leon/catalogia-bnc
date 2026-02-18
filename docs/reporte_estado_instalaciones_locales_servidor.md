# Reporte Estado de Instalaciones en Equipos Locales

Fecha de corte: 2026-02-18  
Ambiente evaluado: equipo local de desarrollo (Windows + Docker Desktop)

## 1. Estado general
- Estado: operativo para desarrollo y pruebas del MVP actual.
- Evidencia: ejecucion de `docker compose`, pruebas backend/frontend, y corridas de flujo UI.

## 2. Componentes validados
- Docker Desktop / Docker Compose: operativo.
  - servicios `db`, `backend`, `frontend` levantan correctamente.
- Python:
  - disponible `3.13` y `3.11`.
  - backend validado en `backend/.venv311` por compatibilidad de dependencias.
- Node.js / npm:
  - frontend con dependencias instaladas.
  - `lint` y `test` ejecutables en entorno local.

## 3. Dependencias y observaciones
- Backend:
  - dependencias instaladas desde `backend/requirements.txt`.
  - observacion: `asyncpg` falla en `3.13` y se usa `3.11` para pruebas locales.
- Frontend:
  - dependencias instaladas desde `frontend/package.json`.
  - advertencias de paquetes deprecados/vulnerabilidades reportadas por `npm audit` (no bloqueantes para MVP).

## 4. Variables de entorno requeridas (resumen)
- Base:
  - `DATABASE_URL`, `STORAGE_PATH`, tokens de rol, `CORS_ALLOW_ORIGINS`.
- Frontend:
  - `NEXT_PUBLIC_BACKEND_URL` o `NEXT_PUBLIC_API_BASE_URL`.
- IA:
  - `AI_ENGINE_PROVIDER`, `AI_ENGINE_TIMEOUT_SECONDS`, `AI_ENGINE_MAX_RETRIES`,
  - `AI_ENGINE_FALLBACK_TO_MOCK`, `APP_ENV`,
  - proveedor segun caso (`OPENAI_*`, `AZURE_*`, `LOCAL_AI_ENGINE_URL`).

## 5. Recomendaciones de operacion local
- Mantener pruebas backend en `Python 3.11`.
- Verificar variables de IA dentro del contenedor backend despues de cambios en `.env`.
- Usar `docker compose up -d --build backend` al cambiar configuracion del motor IA.

## 6. Referencias
- `README.md`
- `.env.example`
- `docs/ai_engine.md`
- `docs/security_access.md`

---

## Entorno Servidor (VM Ubuntu)

**Sistema Operativo:** Ubuntu 24.04.3 LTS  
**Kernel:** 6.8.0-90-generic  
**Tipo de instalación:** Server mínima (sin entorno gráfico)  
**Infraestructura:** Máquina Virtual (VM)

### 1. Herramientas instaladas
- build-essential (gcc, g++, make)
- git
- curl
- jq
- htop
- open-vm-tools
- cloud-init

### 2. Servicios activos
- ssh
- cron
- rsyslog
- unattended-upgrades
- systemd-networkd

**Estado general:** Servidor base limpio.
