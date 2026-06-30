# Mapeo de Archivos — contadores-bma-conversor

Última actualización: 2026-06-26  
Estado: producción activa

---

## Flujo general

```
Informe de Liquidación (.xls/.xlsx)   ← input obligatorio (Bejerman Web)
Grilla (.xls/.xlsx)                   ← input opcional (enriquece cols 3, 5, 8)
Cubo (.xls/.xlsx)                     ← input opcional (enriquece col "Costos")
        ↓
    convert.php
        ↓
STR-INFORME-{nombre}.xlsx             ← output (PhpSpreadsheet)
```

---

## 1. Informe de Liquidación (input principal)

Formato jerárquico por empleado. El sistema usa `$ws->toArray(null, false, false, false)` de PhpSpreadsheet → array 0-indexed por fila y columna.

### Estructura de bloques por empleado

Cada empleado ocupa un bloque de filas con este patrón:

```
[Fila empleado]    col2=legajo(numeric), col6=nombre, col22=sector,
                   col31=calificacion, col40=ingreso_date, col50=categoria,
                   col64=lugar_trabajo
[Fila SIPA]        col2='SIPA', col66=CUIL (formato '20-12345678-9')
[Filas concepto]   col2=cod_izq, col4=desc_izq, col34=imp_izq
                   col44=cod_der, col48=desc_der, col69=imp_der
[Fila resumen]     col2='Haberes remunerativos:', col10=hab_rem,
                   col35=hab_norem, col56=retenciones, col74=neto
[Filas vacías]     separador entre empleados
```

Al final del archivo hay una fila de totales generales adicional (`col2='Haberes remunerativos:'` con valores muy grandes) — se ignora automáticamente porque `$currentLegajo = null` al terminar el último empleado.

### Columnas de la fila empleado (0-indexed)

| Index | Dato | Destino STR |
|-------|------|-------------|
| 2 | Legajo (numeric) | col 1 `int($c2)` |
| 6 | Apellido y Nombre | col 2 |
| 22 | Sector | parte 1 de col 7 Especialidad |
| 31 | Calificación | parte 2 de col 7 Especialidad |
| 40 | Fecha Ingreso (serial Excel) | col 9 → `XlsDate::excelToDateTimeObject` → `d/m/Y` |
| 50 | Categoría | col 6 |
| 64 | Lugar de Trabajo | no usado en STR (existe en informe pero CC y OS vienen de Grilla) |

**Especialidad** = `sector . " - " . calificacion` (o solo el que tenga valor si uno está vacío).

### Columnas de la fila SIPA (0-indexed)

| Index | Dato | Destino STR |
|-------|------|-------------|
| 66 | CUIL completo (ej: `'20-12345678-9'`) | col 4 |

### Columnas de filas de concepto (0-indexed)

| Index | Dato | Uso |
|-------|------|-----|
| 2 | Código concepto izquierdo | `normCode()` → buscar en template |
| 34 | Importe izquierdo | valor del concepto izquierdo |
| 44 | Código concepto derecho | `normCode()` → buscar en template |
| 69 | Importe derecho | valor del concepto derecho (solo si no es vacío) |

Cada fila de concepto puede tener hasta **dos conceptos**: izquierdo (cols 2+34) y derecho (cols 44+69). El derecho solo se registra si `col44 ≠ vacío AND col69 ≠ vacío`.

**Concepto especial 9999**: si aparece como código, su importe se guarda además en `$agg['redondeo']`.

### Columnas de la fila resumen (0-indexed)

| Index | Dato | Uso en STR |
|-------|------|------------|
| 10 | Haberes remunerativos | `$agg['hab_rem']` → columnas `Total haberes`, `Bruto` |
| 35 | Haberes no remunerativos | `$agg['hab_norem']` → sumado a `hab_rem` en `Total haberes` |
| 56 | Retenciones totales | `$agg['retenciones']` → columna `Retenciones` |
| 74 | Neto a cobrar | `$agg['neto']` → columnas `Neto a Cobrar`, `Neto` |

### Detección de filas

| Condición | Tipo de fila |
|-----------|-------------|
| `col2` es numérico AND `col6` no vacío | Fila de empleado (inicio de bloque) |
| `col2 == 'SIPA'` | Fila de detalle (extrae CUIL) |
| `col2` empieza con `'Haberes remunerativos'` | Fila de resumen (cierra bloque del empleado) |
| `col2` no vacío (otro caso) | Fila de concepto |
| `col2` vacío | Ignorada |

---

## 2. Grilla (input opcional)

Complementa Lugar de Pago, CC y Obra Social que no están en el Informe.

Formato: tabla larga (tall), una fila por concepto por empleado. Header en fila 1 (se saltea con `$i = 1`).

### Columnas relevantes (0-indexed)

| Index | Dato | Destino STR |
|-------|------|-------------|
| 4 | Nro. de Legajo | clave de lookup |
| 10 | Lugar de Pago | col 3 (solo primera ocurrencia) |
| 19 | Código Obra Social | col 8 (solo primera ocurrencia) |
| 30 | Centro de Costos | col 5 → `int(CC)` (solo primera ocurrencia) |

Solo enriquece empleados ya detectados en el Informe (`isset($employees[$legajo])`).

---

## 3. Cubo (input opcional)

Complementa únicamente la columna "Costos" del STR.

### Columnas relevantes (0-indexed)

| Index | Dato | Destino STR |
|-------|------|-------------|
| 2 | Legajo | clave de lookup |
| 11 | Costos | columna labeled `'Costos'` |

---

## 4. Template STR ENCABEZADO VALIDO.xlsx → Hoja2

Solo provee **estructura de columnas**, no datos de empleados.

### Filas del template

| Fila | Contenido |
|------|-----------|
| 1 | Nombre de empresa / agrupador |
| 2 | **Códigos de concepto** (int) por columna — usados para el lookup |
| 3 | Título descriptivo |
| 4 | **Etiquetas legibles** por columna — usadas para columnas sin código |

### Columnas fijas STR (cols 1-9, siempre presentes)

| Col STR | Etiqueta | Fuente |
|---------|----------|--------|
| 1 | Legajo | Informe col2 → `int($c2)` |
| 2 | Apellido y Nombre | Informe col6 |
| 3 | Lugar de Pago | Grilla col10 (o null si no se sube Grilla) |
| 4 | CUIL | Informe fila SIPA col66 |
| 5 | CC | Grilla col30 → `int(CC)` |
| 6 | Categoría | Informe col50 |
| 7 | Especialidad | `Informe[22] . " - " . Informe[31]` |
| 8 | OS | Grilla col19 |
| 9 | Fecha Ingreso | Informe col40 → fecha `d/m/Y` |

### Columnas de conceptos STR (cols 10+)

Para cada columna con código entero en la fila 2 del template:
```
$rowData[$col] = $concepts[$colCodes[$col]] ?? 0
```
Si el empleado no tiene ese concepto → 0.

### Columnas labeled STR (cols sin código en fila 2, identificadas por etiqueta en fila 4)

| Etiqueta fila 4 | Fórmula |
|-----------------|---------|
| `'TOTAL PROV'` | `($concepts[6033] ?? 0) + ($concepts[6100] ?? 0)` |
| `'TOTAL CARGAS PROV'` | `($concepts[6034] ?? 0) + ($concepts[6101] ?? 0)` |
| `'Redondeo'` | `$agg['redondeo']` (concepto 9999) |
| `'Neto a Cobrar'` | `$agg['neto']` |
| `'Total haberes'` | `$agg['hab_rem'] + $agg['hab_norem']` |
| `'Base Imponible'` | `$concepts[399] ?? 0` |
| `'Rem 2'` | `$concepts[2910] ?? 0` |
| `'Detraccion'` | `$concepts[2972] ?? 0` |
| `'Rem 10'` | `$concepts[2981] ?? 0` |
| `'Gerente'` | `$concepts[100] ?? 0` |
| `'Neto'` | `$agg['neto']` |
| `'Retenciones'` | `$agg['retenciones']` |
| `'Bruto'` | `$agg['hab_rem'] + $agg['hab_norem']` |
| `'Costos'` | `$cuboData[$legajo]['costos'] ?? 0` |
| cualquier otro | `0` |

### Post-procesamiento: eliminación de columnas todo-cero

Después de construir todas las filas, se eliminan del output las columnas 10+ donde **todos** los empleados tienen 0. Las columnas 1-9 siempre se mantienen.

---

## 5. Normalización de datos

```php
normLegajo($v): string   // trim + quita '.' y ' ' → ej: '3.116' → '3116'
normCode($v): int        // trim + quita '.' → int → ej: '0101' → 101
parseImporte($v): float  // maneja float directo o string '1.234,56' → 1234.56
```

---

## 6. Casos edge documentados (junio 2026)

### Barquet, Orlando (legajo 672209) — empleado en licencia vacacional

Este empleado tiene una estructura de conceptos diferente al resto cuando toma licencia:

| Columna STR | Empleados normales | Barquet en vacaciones | Observación |
|-------------|-------------------|----------------------|-------------|
| `Base Imponible` | `concepts[399]` ≠ 0 | `concepts[399]` = **ausente** | No tiene base Ganancias ese mes |
| `TOTAL PROV` | `concepts[6033] + concepts[6100]` ≠ 0 | ambos **ausentes** | La provisión se consume al liquidar vacaciones |

Conceptos que **reemplazan** a 6033/6100 cuando el empleado toma vacaciones:
- Concepto 205 (Vacaciones pagadas) — importe positivo
- Concepto 305 (Descuento vacaciones) — importe negativo compensatorio
- Conceptos 6034 y 6101 (Cargas sobre provisiones) — siguen presentes

Conceptos comunes a todos los empleados (verificado sobre 108 empleados, junio 2026):

| Concepto | Descripción | Todos | Valor típico |
|----------|-------------|-------|-------------|
| 398 | Base total (rem + no rem) | 108/108 | = hab_rem + hab_norem |
| 7291 | Base remunerativa | 108/108 | = hab_rem |
| 7300 | Base total | 108/108 | = 398 |
| 399 | Base Imponible (Ganancias) | 107/108 | = hab_rem (salvo Barquet) |
| 6033 | Provisión Vacaciones | 107/108 | ausente en mes de licencia |
| 6100 | Provisión SAC | 107/108 | ausente en mes de licencia |

> **Nota para modificaciones futuras**: si se reporta `Base Imponible = 0` en el output para algún empleado, verificar si ese empleado tiene concepto 399. Si no lo tiene, probablemente esté en período de licencia vacacional o exento de Ganancias — es comportamiento correcto.

---

## 7. Estructura del output

- Una hoja: `Hoja2`
- Filas 1-4: cabeceras del template (copiadas tal cual)
- Fila 5+: un empleado por fila, en el orden en que aparecen en el Informe
- Columnas: solo las que tienen al menos un valor ≠ 0 en col 10+ (las 1-9 siempre)
- Estilos aplicados: colores alternos por fila, freeze en A5, auto-width cols 1-9, width fija 11 en cols 10+
