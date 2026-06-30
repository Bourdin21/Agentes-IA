# Metadata del proyecto

- nombre: contadores-bma-conversor
- fecha_inicio: 2026-06-24
- estado: activo
- owner: bourdinjoaquin@gmail.com
- descripcion: Conversor Excel origen (Bejerman Web/Onvio) → destino (plantilla cliente). Parsea conceptos detallados de recibos de sueldo por empleado de una empresa.
- ruta_definiciones: /docs/contadores-bma-conversor/definiciones
- ruta_repositorio: C:\Sistemas\Contadores BMA - Conversor
- repositorio_git: https://gitlab.com/olvidata/conversor-bma.git
- url_produccion: http://conversor.contadoresbma.com.ar
- estado: ENTREGADO — en producción desde 2026-06-25

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
