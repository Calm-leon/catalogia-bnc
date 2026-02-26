# Seguridad y accesos

## Variables sensibles
Definir los tokens por entorno. Ejemplo (no versionar en git):
- `ADMIN_TOKEN`
- `CATALOGER_TOKEN`
- `VIEWER_TOKEN`

## Endurecimiento configurable (MVP)
- `SECURITY_HEADERS_ENABLED=true|false`
- `SECURITY_CSP` (default: `default-src 'none'; frame-ancestors 'none'; base-uri 'none'`)
- `SECURITY_HSTS_ENABLED=true|false` (recomendado `false` en local HTTP)

Cabeceras aplicadas cuando `SECURITY_HEADERS_ENABLED=true`:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`
- `Content-Security-Policy` configurable por entorno

## Rate limiting MVP (configurable)
Aplicado por token (si existe) o IP:
- Endpoint `POST /internal/pipeline/image`: `RATE_LIMIT_PIPELINE_IMAGE_PER_MINUTE` (default `5`)
- Endpoint `POST /internal/logs`: `RATE_LIMIT_LOGS_PER_MINUTE` (default `60`)
- Ventana: `RATE_LIMIT_WINDOW_SECONDS` (default `60`)
- Global: `RATE_LIMIT_ENABLED=true|false`

En CI/smoke puede desactivarse (`RATE_LIMIT_ENABLED=false`) para evitar falsos bloqueos.

## Uso
Enviar header:
```
Authorization: Bearer <TOKEN>
```

## Roles
- `admin`: acceso completo.
- `cataloger`: acceso a logs, storage y pipeline.
- `viewer`: sin acceso a endpoints internos.

## Endpoints protegidos
- `POST /internal/logs`
- `POST /internal/storage/upload`
- `POST /internal/pipeline/image`
- `POST /internal/pipeline/image/review`
- `GET /internal/jobs`
- `GET /internal/jobs/{job_id}`
