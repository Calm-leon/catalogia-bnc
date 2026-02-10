# Seguridad y accesos

## Variables sensibles
Definir los tokens por entorno. Ejemplo (no versionar en git):
- `ADMIN_TOKEN`
- `CATALOGER_TOKEN`
- `VIEWER_TOKEN`

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