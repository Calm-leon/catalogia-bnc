CatalogIA

Proyecto de Precatalogación Asistida por IA

Biblioteca Nacional de Colombia
Fecha de actualización: febrero de 2026
Responsable: Camilo Andrés López León

1. Qué es

CatalogIA es un sistema de precatalogación asistida que procesa objetos digitales y genera XML Dublin Core para revisión humana antes de su validación final.

2. Resumen

La Biblioteca Nacional de Colombia (BNC) recibe un volumen alto de objetos bibliográficos por depósito legal, compra, donación y canje. El proyecto CatalogIA reduce la carga operativa del proceso manual al generar una propuesta inicial de metadatos y dejar la validación final al catalogador.

Estado actual del proyecto:
- Monolito operativo con Docker Compose (db + backend + frontend + storage local).
- Pipeline de imagen funcional con trazabilidad por job.
- Flujo UI operativo: login -> upload -> XML -> revisión -> guardado.
- XML en formato RDF + Dublin Core.
- Motor IA intercambiable con proveedores `mock`, `openai`, `azure`, `local`.
- Soporte multimodal para envío de imagen al proveedor IA (visión).

3. Contexto institucional, flujo actual y flujo propuesto

Flujo actual institucional (alto nivel):
- Conservación recibe, restaura y digitaliza.
- Se gestiona URL del objeto en repositorio institucional.
- Desarrollo de Colecciones cataloga y valida bajo normas vigentes.
- Conservación realiza carga final de metadatos.

Flujo propuesto con CatalogIA (estado de implementación):
- Conservación digitaliza y publica objeto.
- CatalogIA ejecuta precatalogación automática y genera XML preliminar.
- Catalogador revisa/edita XML en interfaz.
- Se guarda XML revisado y trazabilidad de ejecución.
- El proceso final de publicación institucional se mantiene bajo control humano.

4. Necesidades identificadas

4.1 Sincronización entre sistemas catalográficos y repositorio
- Sigue vigente la necesidad de conciliación entre fuentes de metadatos y repositorio final.
- CatalogIA ya produce trazabilidad técnica para apoyar esa conciliación.

4.2 Optimización del cargue XML
- Se avanzó en generación y versión revisada por job.
- La carga masiva al sistema final externo sigue fuera del alcance actual.

4.3 Automatización de catalogación (piloto)
- Avance significativo en automatización para imágenes.
- Ya existe motor IA intercambiable y canal visual para inferencia en proveedores reales.

5. Por qué usar IA en este proceso

Beneficios alcanzados/parciales:
- Eficiencia: el catalogador parte de una base XML automatizada.
- Trazabilidad: cada corrida queda registrada por `job_id` (estado, archivos, logs).
- Estandarización técnica: salida XML Dublin Core en RDF.
- Escalabilidad técnica: arquitectura desacoplada de proveedor IA.

6. Propuesta técnica

Arquitectura actual:
- Backend: FastAPI
- Frontend: Next.js
- Base de datos: PostgreSQL
- Storage: local (volumen Docker)
- Orquestación: Docker Compose

Capacidades implementadas:
- Seguridad por token y roles.
- Pipeline de imagen con estados `queued/running/completed/failed`.
- Edición de XML y guardado de revisión `_reviewed.xml` (sin historial múltiple en MVP).
- Proveedores IA configurables por entorno con timeout/retries.
- Fallback a mock solo permitido en local/dev y habilitado explícitamente.

7. Plan de trabajo (MVP)

Completado:
- Iteración 1: integración frontend-backend.
- Iteración 2: jobs y trazabilidad.
- Iteración 3: revisión y edición XML.
- Iteración 4: proveedor IA real + configuración/fallback.
- Mini-iteración adicional: salida RDF estándar + soporte multimodal.

Pendiente:
- Iteración 5: consulta operativa + calidad de metadatos.
- Iteración 6: hardening final + E2E de cierre MVP.

8. Limitaciones y cuellos de botella actuales

- La calidad semántica de metadatos aún depende de prompt/modelo y validación humana.
- Variabilidad de respuestas de proveedores IA.
- Integración con procesos externos de carga masiva no implementada en esta fase.
- Deuda técnica pendiente en endurecimiento y pruebas E2E completas de cierre.

9. Resultados preliminares y proyección 2026

Resultados preliminares:
- Plataforma funcional de precatalogación para imágenes.
- XML generado y revisado en RDF Dublin Core.
- Trazabilidad operativa por job.
- Base de pruebas backend/frontend y CI operativa.

Proyección 2026:
- Consolidar calidad semántica con reglas y validaciones ampliadas.
- Completar capa operativa de consulta/historial y cierre de MVP.
- Definir estrategia de integración con sistemas institucionales de publicación final.

10. Anexos

Documentación técnica relacionada:
- `README.md`
- `docs/ai_engine.md`
- `docs/pipeline_image.md`
- `docs/security_access.md`
- `docs/storage.md`
- `docs/observability.md`
- `docs/validation_checklist.md`
- `docs/ci_cd.md`
- `docs/reporte_estado_instalaciones_locales.md`
- `docs/documentacion_codigo_avanzado_actual.md`
- `docs/avances_entregables_plan_trabajo.md`
