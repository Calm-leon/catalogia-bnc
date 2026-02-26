# Checklist Final MVP Usable

## Criterios de aceptacion obligatorios
- [ ] `GET /health` responde `200` con `{"status":"ok","db":"ok"}`.
- [ ] Autenticacion valida token y roles:
  - [ ] 401 sin token en endpoints protegidos.
  - [ ] 403 para rol no permitido en pipeline.
- [ ] Flujo catalogador completo funcional:
  - [ ] autenticar (`/login`)
  - [ ] subir imagen (`/upload`)
  - [ ] generar XML (`POST /internal/pipeline/image`)
  - [ ] editar/guardar (`POST /internal/pipeline/image/review`)
  - [ ] consultar historial y detalle (`/select`, `/internal/jobs`, `/internal/jobs/{job_id}`)
- [ ] Trazabilidad por `job_id` visible en jobs/logs/files.
- [ ] Calidad XML evaluada con checklist deterministico (score + checks).

## Evidencia tecnica minima
- [ ] Backend tests en verde (`pytest`).
- [ ] Frontend lint/build en verde.
- [ ] Smoke frontend (upload/xml/select) en verde.
- [ ] Logs backend sin errores no controlados durante demo.

## Script de demo tecnica (10-12 min)
1. `docker compose up -d --build`
2. Validar `http://localhost:8000/health`.
3. Abrir `http://localhost:3000/login` y autenticar catalogador.
4. En `/upload`, cargar imagen y generar XML.
5. En `/xml`, editar campos y guardar revision.
6. En `/select`, abrir detalle del job y mostrar:
   - score/checklist de calidad,
   - archivos asociados,
   - logs asociados.
7. Mostrar query DB de verificacion (opcional):
   - jobs recientes,
   - files por job,
   - logs por job.

## Cierre
- [ ] Documentacion actualizada (`README`, `docs/security_access.md`, `docs/validation_checklist.md`).
- [ ] CI con smoke MVP habilitado y verde.
