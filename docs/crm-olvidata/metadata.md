# Metadata del proyecto

- nombre: crm-olvidata
- fecha_inicio: 2026-07-14
- estado: **en producción desde 2026-07-21** en `https://portal.olvidata.com.ar/` (SSL Let's Encrypt manual, vence 2026-10-19 — no renueva sola). "Campañas de contacto frío configurables" implementada y con QA GO 2026-07-21 (CU-13/14/15, HU-12 a HU-16). Datos de producción poblados por migración completa desde dev (1189 filas). Ver `definiciones/5-implementador.md`, `6-qa.md` y `trazabilidad.md` (entradas de deploy/SSL/migración de datos).
- URL producción: https://portal.olvidata.com.ar/
- Hosting: site4now.net (win8232.site4now.net), sitio IIS `olvidatasoft-002-site12`, MySQL en `MYSQL5044.site4now.net`
- owner: Joaquín Bourdin (OlvidataSoft)
- descripcion: CRM interno de OlvidataSoft para centralizar contactos, leads y clientes hoy dispersos en archivos (JSON/Excel/txt) de BotPublicitario, sobre stack .NET del estudio.
- ruta_definiciones: /docs/crm-olvidata/definiciones
- ruta_repositorio: `C:\Sistemas\olvidatasoft-crm` — namespace/solución `OlvidataCRM`, creado como copia de `C:\Sistemas\KoiDumplings` (base .NET 10 real del estudio) y saneado de toda la lógica de negocio de KOI (ver entrada de trazabilidad 2026-07-14 "Limpieza técnica base").

## Archivos de memoria por agente
- analista-funcional: /docs/<proyecto>/definiciones/1-analista-funcional.md
- disenador-funcional: /docs/<proyecto>/definiciones/2-disenador-funcional.md
- arquitecto-mvc: /docs/<proyecto>/definiciones/3-arquitecto-mvc.md
- presupuestador: /docs/<proyecto>/definiciones/4-presupuestador.md
- implementador: /docs/<proyecto>/definiciones/5-implementador.md
- qa: /docs/<proyecto>/definiciones/6-qa.md
- documentador: /docs/<proyecto>/definiciones/7-documentador.md
