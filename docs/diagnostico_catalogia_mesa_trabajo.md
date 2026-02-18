# CatalogIA - Diagnostico ejecutivo para direccion y mesa de trabajo

Fecha: 18 de febrero de 2026  
Proyecto: CatalogIA (Biblioteca Nacional de Colombia)

## 1. Proposito de este documento
Este documento traduce el estado tecnico de CatalogIA a un lenguaje de gestion para alinear a direccion, catalogadores y equipo de desarrollo en: estado real, avances, riesgos, decisiones y proximos pasos.

## 2. Que es CatalogIA (en una frase)
CatalogIA es una herramienta que ayuda a generar una propuesta inicial de metadatos en XML (Dublin Core) para objetos digitales, de forma que el catalogador revise y apruebe el resultado final.

## 3. Estado actual del proyecto (resumen ejecutivo)
Estado general: **En avance, con base solida y MVP en consolidacion**.

Semaforo por frente:
- Infraestructura y despliegue local: **Verde**
- Backend (API y trazabilidad): **Verde**
- Frontend operativo para flujo basico: **Amarillo-Verde**
- Edicion y guardado de XML revisado: **Verde**
- Calidad semantica del XML por IA: **Amarillo**
- Hardening y cierre final MVP: **Amarillo**

## 4. Que ya funciona hoy
- Entorno integrado con Docker Compose (base de datos, backend, frontend y almacenamiento local).
- Flujo funcional de uso:
  1) ingreso por token,
  2) carga de imagen,
  3) generacion de XML,
  4) visualizacion en interfaz,
  5) edicion por catalogador,
  6) guardado de version revisada.
- Trazabilidad por ejecucion (`job_id`): estado, archivos y logs asociados.
- Motor IA desacoplado (intercambiable por proveedor): `mock`, `openai`, `azure`, `local`.
- Pruebas automatizadas base (backend y frontend) y pipeline CI.

## 5. Que NO esta cerrado todavia
- Consulta operativa avanzada (historial y vistas para seguimiento por usuario/periodo).
- Reglas de calidad semantica mas estrictas para metadatos (consistencia y enriquecimiento de campos).
- Endurecimiento final para cierre MVP (seguridad operativa, pruebas E2E integrales y guia de demo final).
- Integracion con sistemas institucionales externos para carga/publicacion masiva (fuera del alcance del MVP actual).

## 6. Valor para la operacion
- Reduce trabajo manual inicial del catalogador.
- Estandariza salida tecnica en RDF + Dublin Core.
- Permite revisar y corregir antes de publicar.
- Aporta trazabilidad para auditoria y control de calidad.

## 7. Riesgos principales y mitigacion
1. Calidad variable de salida IA.
Mitigacion: mantener revision humana, reforzar prompts, agregar reglas de validacion y checklist de calidad.

2. Expectativas altas sobre automatizacion total.
Mitigacion: comunicar que CatalogIA es asistente de precatalogacion, no reemplazo del criterio catalografico.

3. Diferencias entre ambientes locales.
Mitigacion: estandar de instalacion, verificacion por checklist y CI.

## 8. Avance del plan de trabajo (MVP)
Completado:
- Iteracion 1: Integracion UI -> pipeline.
- Iteracion 2: Jobs y trazabilidad.
- Iteracion 3: Revision/edicion XML.
- Iteracion 4: Proveedor IA real bajo contrato intercambiable.
- Mini-iteracion adicional: salida RDF estandar + mejora multimodal.

Pendiente:
- Iteracion 5: consulta operativa + calidad.
- Iteracion 6: hardening final + E2E de cierre.

## 9. Decisiones de direccion sugeridas (proxima mesa)
1. Confirmar alcance de MVP: uso piloto interno con revision humana obligatoria.
2. Aprobar criterios de salida minima aceptable para catalogador (campos obligatorios y nivel de detalle).
3. Definir ventana de cierre de iteraciones 5 y 6.
4. Acordar plan de adopcion piloto (usuarios, volumen de prueba, indicadores de exito).

## 10. Indicadores propuestos para seguimiento
- Tiempo promedio por registro (antes vs con CatalogIA).
- Porcentaje de registros que requieren correccion mayor.
- Porcentaje de ejecuciones exitosas por `job`.
- Cumplimiento de campos Dublin Core obligatorios.
- Incidentes operativos por semana.

## 11. Proximo hito recomendado
Cerrar Iteraciones 5 y 6 con evidencia formal (pruebas, checklist y demo guiada) para declarar **MVP usable en piloto** y preparar evaluacion institucional.

## 12. Documentos de soporte
- `docs/docmento_base_oficial_catalogia.md`
- `docs/avances_entregables_plan_trabajo.md`
- `docs/documentacion_codigo_avanzado_actual.md`
- `docs/reporte_estado_instalaciones_locales.md`
- `docs/ai_engine.md`
- `README.md`
