# Implementador PHP — contadores-bma-conversor

Estado: CERRADO — Implementación completada 2026-06-25

---

## Stack

- PHP 8.3 + PhpSpreadsheet 2.x
- Frontend: HTML/CSS vanilla (sin framework JS)
- Hosting: Ferozo shared hosting (LiteSpeed), subdominio `conversor.contadoresbma.com.ar`
- Deploy: `deploy.py` — FTPS + vendor.zip extraído via PHP ZipArchive

## Archivos implementados

| Archivo | Descripción |
|---|---|
| `app/convert.php` | Lógica principal: parseo Grilla, pivot tall→wide, totales, escritura STR |
| `app/index.php` | UI: drag-and-drop, spinner, descarga automática, footer OlvidataSoft |
| `app/static/style.css` | Estilos: card, drop-zone, botón, footer ov-* |
| `app/static/isotipo.svg` | Isotipo OlvidataSoft (fuente: olvidatasoft-new/public/brand/) |
| `app/STR ENCABEZADO VALIDO.xlsx` | Template de estructura de columnas STR |
| `app/.htaccess` | Configuración LiteSpeed/Apache |
| `deploy.py` | Script de deploy FTPS a Ferozo |

## Lógica de convert.php

### Parsing (Grilla tall→wide)
- Itera filas de la Grilla (una fila por concepto por empleado)
- Primera aparición del legajo define los datos fijos (cols 1-8)
- Acumula conceptos por código en `$employees[$legajo]['concepts']`
- Acumula totales por tipo en `$employees[$legajo]['agg']`:
  - `neto` = sum(importe) donde tipo ≠ 'Contribución Patronal'
  - `redondeo` = sum(importe) donde tipo = 'Redondeo'

### Columnas STR calculadas (sin código de concepto)
- `TOTAL PROV` → concepts[6033] + concepts[6100]
- `TOTAL CARGAS PROV` → concepts[6034] + concepts[6101]
- `Redondeo` → agg['redondeo']
- `Neto a Cobrar` → agg['neto']
- Detección por etiqueta de fila 4 del template (no por número de columna)

### Columnas descartadas
- Col 9 (Fecha Ingreso): vacía, no disponible en Grilla — decisión del cliente
- Cols 196-199 del template (Neto/Retenciones/Bruto/Costos del Cubo): obsoletas, quedan en 0

## Decisiones tomadas

- **Grilla como único input**: reemplaza al Cubo. Contiene datos del empleado + conceptos.
- **Template solo define estructura**: no provee datos de empleados, solo columnas (Hoja2).
- **Nuevos empleados**: se incluyen automáticamente desde la Grilla sin intervención manual.
- **Empleados sin actividad**: no aparecen en el output.
- **Legajo normalizado**: se eliminan puntos y espacios para el lookup.
