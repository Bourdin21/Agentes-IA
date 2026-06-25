# Analista Funcional — contadores-bma-conversor

Estado: CERRADO — Discovery completado 2026-06-24, mapping completado 2026-06-25

---

## Alcance funcional confirmado

**Sistema:** App web PHP (PhpSpreadsheet) — una sola pantalla.

**Flujo:** Usuario sube Grilla xlsx → sistema convierte → usuario descarga STR xlsx generado.

**Empresa:** SERVICIO TERAPIA RENAL S.A.

---

## Archivo de entrada: Grilla Informe de Liquidación.xlsx

La Grilla es el **único** archivo de entrada. Reemplaza al Cubo (es un superconjunto: incluye datos del empleado + conceptos).

- Formato: tabla larga (tall) — una fila por concepto por empleado
- Cada fila tiene el legajo (no hay filas con legajo vacío como en el Cubo)
- ~108 empleados, ~6292 filas de datos

### Columnas relevantes (0-indexed para PHP toArray)

| Index | Col | Nombre | Uso en STR |
|-------|-----|--------|------------|
| 4 | 5 | Nro. de Legajo | STR col 1 |
| 5 | 6 | Apellido y Nombre | STR col 2 |
| 6 | 7 | CUIL | STR col 4 |
| 8 | 9 | Sector | STR col 7 (parte 1 de Especialidad) |
| 10 | 11 | Lugar de Pago | STR col 3 |
| 15 | 16 | Categoría | STR col 6 |
| 19 | 20 | Código Obra Social | STR col 8 |
| 21 | 22 | Puesto de Trabajo | STR col 7 (parte 2 de Especialidad) |
| 22 | 23 | Código Concepto | lookup conceptos |
| 28 | 29 | Importe Calc | valor del concepto |
| 30 | 31 | Centro de Costos | STR col 5 (CC, entero) |

### Normalización
- Legajo: `str_replace(['.', ' '], '', trim(str(legajo)))` → clave de lookup
- Código Concepto: `int(str_replace('.', '', trim(code)))` → comparar con int fila 2 del template
- Importe Calc: ya viene como float; `parseImporte` maneja también string formato argentino

---

## Destino: STR ENCABEZADO VALIDO.xlsx → Hoja2

- Solo se usa **Hoja2** como estructura/cabecera
- El template **NO provee datos de empleados** — es solo estructura de columnas
- Encabezado: fila 1=empresa, fila 2=códigos int, fila 3=título, fila 4=etiquetas
- Output: fila 5 en adelante, un empleado por fila

### Mapping columnas STR (1-based)

| STR Col | Etiqueta | Fuente |
|---------|----------|--------|
| 1 | Legajo | Grilla index 4 (raw value) |
| 2 | Apellido y Nombre | Grilla index 5 |
| 3 | Lugar de Pago | Grilla index 10 (nombre completo) |
| 4 | CUIL | Grilla index 6 |
| 5 | CC | `int(Grilla index 30)` — Centro de Costos |
| 6 | Categoría | Grilla index 15 |
| 7 | Especialidad | `Grilla[8] . " - " . Grilla[21]` (Sector + Puesto de Trabajo) |
| 8 | OS | Grilla index 19 |
| 9 | Fecha Ingreso | **Omitida** (vacía — no disponible en Grilla, decisión del cliente) |
| 10+ | Conceptos | lookup por código en fila 2 del template; 0 si no existe |

### Reglas de conversión
1. Un empleado por fila (primera aparición del legajo define datos fijos)
2. Si código del template existe en Grilla → valor de Importe Calc
3. Si código NO existe en Grilla → 0
4. Empleados ausentes de la Grilla → no aparecen en el output (no trabajaron ese mes)
5. Empleados nuevos (no estaban en template anterior) → incluidos automáticamente desde la Grilla

---

## Stack implementado
- Backend: PHP 8.3 + PhpSpreadsheet 2.x
- Frontend: HTML/CSS simple (sin framework JS)
- Deploy: Shared hosting Ferozo (LiteSpeed) via FTP + vendor.zip
- Subdominio: conversor.contadoresbma.com.ar
- Document root en servidor: `/public_html/conversor/`

## Issues cerrados
- Issue 4 (datos fijos del empleado cols 1-9): resuelto — vienen de la Grilla
- Fecha Ingreso (col 9): omitida del output por decisión del cliente
