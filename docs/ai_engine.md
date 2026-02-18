# Motor IA intercambiable

## Interfaz comun
- Contrato: `app.ai.base.AIEngine`
- Entrada: `DublinCoreInput`
- Contexto opcional: `image_bytes`, `image_mime_type`
- Salida: `generate_dublin_core_xml(...) -> str`

## Adaptadores disponibles
- `mock`: `app.ai.mock_engine.MockAIEngine`
- `openai`: `app.ai.openai_engine.OpenAIEngine`
- `azure`: `app.ai.azure_engine.AzureAIEngine`
- `local`: `app.ai.local_engine.LocalAIEngine`

Seleccion por variable de entorno `AI_ENGINE_PROVIDER`.

## Configuracion principal
- `AI_ENGINE_PROVIDER=mock|openai|azure|local`
- `AI_ENGINE_TIMEOUT_SECONDS` (default: `20`)
- `AI_ENGINE_MAX_RETRIES` (default: `2`)
- `AI_ENGINE_FALLBACK_TO_MOCK` (`true|false`, default: `false`)
- `APP_ENV` (`development|production|...`)

### OpenAI
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (default: `gpt-4.1-mini`)

### Azure OpenAI
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION` (default: `2024-02-15-preview`)

### Local provider
- `LOCAL_AI_ENGINE_URL`

## Puntos de reemplazo
1. Crear un nuevo adaptador en `app/ai/` que implemente `AIEngine`.
2. Registrar el proveedor en `app.ai.factory.get_ai_engine()`.
3. Configurar `AI_ENGINE_PROVIDER` en entorno.
4. Validar swap con `backend/tests/test_ai_engine.py`.

## Comportamiento de fallback
- Por defecto no hay fallback: si un proveedor real falla por configuracion/conectividad, el pipeline falla controlado.
- `AI_ENGINE_FALLBACK_TO_MOCK=true` permite fallback **solo** en entorno local (`APP_ENV=development|dev|local`).
- En `APP_ENV=production`, fallback a `mock` es rechazado.

## Soporte visual (vision)
- El pipeline de imagen envia bytes reales de la imagen al proveedor cuando estan disponibles.
- OpenAI y Azure pueden usar contenido multimodal (`text + image_url data:`).
- Si no hay imagen disponible, el proveedor opera con metadatos basicos.

## Prueba de intercambio
- Default: sin `AI_ENGINE_PROVIDER` usa `mock`.
- Con proveedor real y configuracion valida, `factory` retorna el adaptador correspondiente.
- Con proveedor invalido, devuelve error controlado de `Unsupported`.
