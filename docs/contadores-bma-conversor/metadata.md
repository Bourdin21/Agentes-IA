# Metadata del proyecto

- nombre: contadores-bma-conversor
- fecha_inicio: 2026-06-24
- estado: ENTREGADO — en producción desde 2026-06-25, activo (con mantenimiento/fixes puntuales, último 2026-08-20)
- owner: bourdinjoaquin@gmail.com
- descripcion: Conversor Excel origen (Bejerman Web/Onvio) → destino (plantilla cliente). Parsea conceptos detallados de recibos de sueldo por empleado de una empresa.
- ruta_definiciones: /docs/contadores-bma-conversor/definiciones
- ruta_repositorio: C:\Sistemas\Contadores BMA - Conversor
- repositorio_git: https://gitlab.com/olvidata/conversor-bma.git
- url_produccion: http://conversor.contadoresbma.com.ar

## Estado de producción verificado

(Movido desde `trazabilidad.md` el 2026-09-15: son estado vigente verificado, no decisiones de log.)

- **Verificación 2026-08-20 — orquestador.** Cliente reenvió los 3 archivos con todas las columnas de Onvio seleccionadas en la exportación (`Docs/*(1).*`). Nueva Grilla incluye columna "Código Obra Social" (index 15) que no existía en el export anterior. Verificado con el fix de `findColByHeader()` (sin cambios de código adicionales): Lugar de Pago, CC y OS se completan correctamente para todos los empleados (ej. OS='SAN', 'ELE'). Confirma que la resolución de columnas por nombre de encabezado es robusta a que el cliente cambie qué columnas incluye en su export de Bejerman/Onvio. Evidencia: `app/convert.php` (sin cambios), verificado contra `Docs/Grilla Informe de Liquidación (1).xlsx`.
- **Deploy 2026-08-20 — orquestador.** Deploy a producción del fix de `findColByHeader()` vía `deploy.py` (FTPS a Ferozo). Subida de `app/` + extracción de `vendor.zip` OK. Smoke test: `http://conversor.contadoresbma.com.ar` responde 200. Cambio no commiteado a git todavía (pendiente decisión del usuario).

## Stack implementado
- Backend: PHP 8.3 + PhpSpreadsheet 2.x
- Frontend: HTML/CSS vanilla (sin framework JS)
- Hosting: Ferozo shared hosting (LiteSpeed), subdominio conversor.contadoresbma.com.ar
- Deploy: deploy.py — FTPS + vendor.zip extraído via PHP ZipArchive

## Documentación técnica
- [mapeo-archivos.md](mapeo-archivos.md) — estructura completa de columnas de cada input/output, columnas labeled, casos edge

## Archivos de referencia Excel (en Docs/, no versionados)
- `STR ENCABEZADO VALIDO.xlsx` — template de estructura de columnas (versionado en app/)
- `Cubo Informe de Liquidación.xlsx` — referencia histórica (reemplazado por Grilla)
- `STR-INFORME 202604.xls` — ejemplo de informe mensual abril 2026

## Archivos de memoria por agente
- analista-funcional: /docs/contadores-bma-conversor/definiciones/1-analista-funcional.md
- disenador-funcional: /docs/contadores-bma-conversor/definiciones/2-disenador-funcional.md
- arquitecto-mvc: /docs/contadores-bma-conversor/definiciones/3-arquitecto-mvc.md
- presupuestador: /docs/contadores-bma-conversor/definiciones/4-presupuestador.md
- implementador: /docs/contadores-bma-conversor/definiciones/5-implementador.md
- qa: /docs/contadores-bma-conversor/definiciones/6-qa.md
- documentador: /docs/contadores-bma-conversor/definiciones/7-documentador.md
