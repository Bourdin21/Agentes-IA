# Memoria del Implementador .NET

## Metodo de medicion
- [Medir antes de heredar](feedback-medir-antes-de-heredar.md) — todo numero de un brief o reporte previo se re-mide; en La Platense fallo 3 veces
- [Conteos exactos, no estimados](feedback-conteos-exactos-no-estimados.md) — `TABLE_ROWS` es estimado y ya mintio; `CHECKSUM TABLE` no sirve si se agregan columnas
- [Exit code, no tamano de archivo](feedback-exit-code-de-herramienta.md) — un dump con exit != 0 no se usa aunque pese lo esperado

## La Platense
- [Estado de produccion y deploy](project-la-platense-estado-prod-y-deploy.md) — prod en 8/18 migraciones; las 10 pendientes ya ensayadas y OK
- [Acceso a produccion](reference-acceso-produccion-la-platense.md) — la base se lee directo por `mysql.exe`; la password de FTP/Web Deploy no autentica
