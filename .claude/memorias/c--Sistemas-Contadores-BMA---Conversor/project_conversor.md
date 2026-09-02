---
name: conversor-bma proyecto
description: Stack, repo GitLab, URL producción, decisiones clave de arquitectura e implementación del conversor Grilla→STR
type: project
originSessionId: 38a0ef0f-ff90-48d7-91ef-6284ce35c41d
---
Repo GitLab: https://gitlab.com/olvidata/conversor-bma.git  
URL producción: http://conversor.contadoresbma.com.ar  
Hosting: Ferozo shared hosting, document root `/public_html/conversor/`  
Deploy: `deploy.py` — FTPS + vendor.zip extraído por PHP ZipArchive  

**Why:** App web PHP 8.3 + PhpSpreadsheet 2.x que convierte la Grilla de Bejerman (tall) al formato STR (wide) para SERVICIO TERAPIA RENAL S.A.

**How to apply:** Al retomar el proyecto, el estado es: sistema en producción y funcional. El repo es la fuente de verdad del código.

## Decisiones clave
- Grilla es el único input (reemplaza al Cubo)
- Template `STR ENCABEZADO VALIDO.xlsx` define solo la estructura de columnas (Hoja2), no los datos
- Cols 196-199 del template son del Cubo antiguo → se dejan en 0
- Col 9 (Fecha Ingreso) vacía por decisión del cliente
- Totales calculados por Tipo de Concepto (Grilla index 24): TOTAL PROV, TOTAL CARGAS PROV, Redondeo, Neto a Cobrar
- Logo OlvidataSoft: fuente de verdad en `C:\Sistemas\olvidatasoft-new\public\brand\isotipo-color.svg`

## Archivos principales
- `app/convert.php` — lógica completa
- `app/index.php` — UI
- `app/static/style.css` — estilos
- `deploy.py` — deploy a Ferozo
- `Docs/Manual de Usuario.md` — manual entregado al cliente
