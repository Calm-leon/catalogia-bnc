# Motor IA intercambiable

## Interfaz comun
- Contrato: `app.ai.base.AIEngine`
- Entrada: `DublinCoreInput`
- Salida: `generate_dublin_core_xml(...) -> str`

## Adaptador actual
- Implementacion activa: `app.ai.mock_engine.MockAIEngine`
- Seleccion por variable de entorno `AI_ENGINE_PROVIDER`.

## Proveedores soportados por contrato
- `mock` (implementado)
- `openai` (placeholder)
- `azure` (placeholder)
- `local` (placeholder)

## Puntos de reemplazo
1. Crear un nuevo adaptador en `app/ai/` que implemente `AIEngine`.
2. Registrar el proveedor en `app.ai.factory.get_ai_engine()`.
3. Configurar `AI_ENGINE_PROVIDER` en entorno.
4. Validar swap con `backend/tests/test_ai_engine.py`.

## Prueba de intercambio
- Default: sin `AI_ENGINE_PROVIDER` usa `mock`.
- Con `AI_ENGINE_PROVIDER=openai` devuelve error controlado de no implementado.
- Con proveedor invalido devuelve error controlado de unsupported.