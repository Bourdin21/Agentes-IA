# Documento Funcional — Conversor BMA

**Sistema:** Conversor de Liquidación STR  
**Cliente:** Contadores BMA / SERVICIO TERAPIA RENAL S.A.  
**Proveedor:** OlvidataSoft  
**URL producción:** http://conversor.contadoresbma.com.ar  
**Versión:** 1.0  
**Fecha de entrega:** 25 de junio de 2026  
**Estado:** En producción

---

## 1. Introducción y contexto

### 1.1 Necesidad relevada

Contadores BMA procesa mensualmente la liquidación de sueldos de SERVICIO TERAPIA RENAL S.A.
(~108 empleados). El proceso consistía en exportar manualmente datos de Bejerman Web (Onvio)
y construir a mano el archivo STR que se entrega al cliente, con ~200 columnas de conceptos
de remuneración. Este proceso era propenso a errores, consumía tiempo y requería actualización
manual al incorporar nuevos empleados.

### 1.2 Objetivo del sistema

Automatizar la conversión de la **Grilla Informe de Liquidación** exportado desde Bejerman Web al formato
**STR** requerido por SERVICIO TERAPIA RENAL S.A., eliminando el trabajo manual y asegurando
consistencia en el resultado.

### 1.3 Alcance de la versión 1.0

> **Corregido 2026-07-23** (barrido cross-proyecto de memorias): esta sección y las §2-§3 describian el diseño original de 3 archivos (Informe + Grilla + Cubo), previo a la reescritura completa en PHP 8.3 + PhpSpreadsheet (ver `trazabilidad.md`, entrada 2026-06-25). El sistema efectivamente entregado y en producción usa **un único archivo de entrada**: la Grilla Informe de Liquidación. Corregido para reflejar `Docs/Manual de Usuario.md` (fuente as-built).

- Conversión automática de la **Grilla Informe de Liquidación** (`.xls` / `.xlsx`, formato tabla larga) al archivo STR destino
- Un único archivo de entrada — no hay enriquecimiento opcional con otros reportes de Bejerman
- Interfaz web sin instalación, sin usuario ni contraseña
- Disponible desde cualquier navegador con acceso a internet

---

## 2. Flujo general del sistema

```
[Usuario]
    │
    └── Sube Grilla Informe de Liquidación (.xls/.xlsx)   ← único archivo, obligatorio
                    │
                    ▼
          [Conversor BMA — convert.php]
                    │
                    ▼
          STR-INFORME-{nombre}.xlsx                        ← descarga automática
```

El sistema procesa el archivo en el servidor y devuelve el archivo STR al navegador del usuario
sin almacenar ningún dato.

---

## 3. Archivo de entrada

### 3.1 Grilla Informe de Liquidación (único archivo, obligatorio)

Origen: exportación desde Bejerman Web (Onvio) → módulo Liquidación de Sueldos → informe
**"Grilla Informe de Liquidación"**.
Formato: `.xls` o `.xlsx`.

**No se acepta ningún otro archivo.** El sistema no utiliza el Cubo ni ningún otro reporte de
Bejerman — el diseño original con 3 archivos (Informe jerárquico + Grilla + Cubo) fue reemplazado
por este único archivo durante la reescritura a PHP.

La Grilla tiene formato **tabla larga**: una fila por concepto por empleado (un empleado con 30
conceptos genera 30 filas). El sistema agrupa automáticamente todos los conceptos de cada
empleado en una sola fila del archivo de salida.

**Columnas que utiliza el sistema (de la Grilla):**

| Columna en Grilla | Contenido | Destino en STR |
|---|---|---|
| Nro. de Legajo | Identificador del empleado | Col 1 |
| Apellido y Nombre | Nombre completo | Col 2 |
| Lugar de Pago | Sucursal o lugar de pago | Col 3 |
| CUIL | CUIL del empleado | Col 4 |
| Centro de Costos | CC contable | Col 5 (número entero) |
| Categoría | Categoría del empleado | Col 6 |
| Sector + Puesto de Trabajo | Área/sector + cargo | Col 7 Especialidad (concatenado) |
| Código Obra Social | OS del empleado | Col 8 |
| Código Concepto / Importe Calc | Concepto liquidado + importe | Cols 10+ |

No hay columna Fecha Ingreso disponible en la Grilla — la col 9 (Fecha Ingreso) del STR queda vacía.

---

## 4. Archivo de salida

**Nombre:** `STR-INFORME-{nombre del Informe original}.xlsx`  
**Formato:** Excel (.xlsx), una sola hoja llamada `Hoja2`

### 4.1 Estructura del archivo

| Fila | Contenido |
|---|---|
| 1 | Nombre de empresa (SERVICIO TERAPIA RENAL S.A.) |
| 2 | Códigos numéricos de cada concepto |
| 3 | Título del informe |
| 4 | Etiquetas de columna |
| 5 en adelante | Un empleado por fila |

### 4.2 Columnas fijas (cols 1-9)

Siempre presentes, independientemente de los conceptos del período.

> Corregido 2026-07-23: todas las columnas fijas provienen de la Grilla (único archivo de entrada) — no hay archivo "Informe" separado. Ver §3.1.

| Col | Etiqueta | Fuente |
|---|---|---|
| 1 | Legajo | Grilla — Nro. de Legajo |
| 2 | Apellido y Nombre | Grilla |
| 3 | Lugar de Pago | Grilla |
| 4 | CUIL | Grilla |
| 5 | CC | Grilla — Centro de Costos (número entero) |
| 6 | Categoría | Grilla |
| 7 | Especialidad | Grilla: Sector + " - " + Puesto de Trabajo |
| 8 | OS | Grilla — Código Obra Social |
| 9 | Fecha Ingreso | — *(no disponible en la Grilla, se deja vacío)* |

### 4.3 Columnas de conceptos (cols 10+)

Una columna por cada concepto definido en el template STR ENCABEZADO VALIDO.xlsx.
- Si el empleado tiene ese concepto liquidado en el período → importe numérico
- Si no tiene ese concepto → 0
- Columnas donde **todos** los empleados tienen 0 se eliminan automáticamente del output

### 4.4 Columnas calculadas (sin código de concepto)

El sistema calcula automáticamente estas columnas por etiqueta:

| Etiqueta | Fórmula |
|---|---|
| TOTAL PROV | Provisión Vacaciones + Provisión SAC |
| TOTAL CARGAS PROV | Cargas sobre Provisión Vac. + Cargas sobre Provisión SAC |
| Redondeo | Importe de redondeo del período (Concepto 9999) |
| Neto a Cobrar | Total neto del empleado (haberes − retenciones), calculado desde los conceptos de la Grilla |

> **Corregido 2026-07-23**: se eliminó la columna **Costos** (dependía del Cubo de Liquidación, que ya no existe como archivo de entrada — ver §3). Las filas "Total haberes", "Base Imponible", "Neto" y "Bruto" y "Retenciones" que figuraban acá en la versión anterior de este documento asumían campos de una "fila resumen" del Informe jerárquico original, que tampoco existe en el modelo actual de un único archivo (Grilla, tabla larga). El Manual de Usuario (`Docs/Manual de Usuario.md`, fuente as-built) solo confirma explícitamente las 4 columnas de esta tabla. **Pendiente de QA**: verificar contra el sistema real en producción si esas columnas adicionales (Total haberes, Base Imponible, Neto, Bruto, Retenciones) siguen existiendo en el STR de salida y, si es así, documentar aquí su fórmula real (probablemente agregada por código de concepto sobre las filas de la Grilla, no sobre una fila resumen que ya no existe).

### 4.5 Formato visual del archivo de salida

- Filas 1-4: encabezados con colores corporativos (azul oscuro, azul medio, azul claro)
- Filas de datos: filas pares con fondo azul muy suave (efecto zebra)
- Encabezado fijo (freeze en fila 5): al hacer scroll, el encabezado permanece visible
- Columnas 1-9: ancho automático ajustado al contenido
- Columnas 10+: ancho fijo de 11 unidades

---

## 5. Reglas de negocio

### Empleados incluidos en el output

Solo aparecen los empleados que tienen al menos un concepto en la Grilla del período procesado.
Empleados sin actividad ese mes no se incluyen.

### Empleados nuevos

Si un empleado aparece en la Grilla pero no estaba en períodos anteriores, se incluye
automáticamente. No se requiere ninguna actualización manual del template.

### Orden de los empleados

Los empleados aparecen en el mismo orden en que figuran en la Grilla (primera aparición del legajo).

### Normalización de legajos

El sistema elimina automáticamente puntos y espacios de los legajos para que el lookup funcione
independientemente del formato exportado por Bejerman.  
Ejemplo: `3.116` → `3116`.

### Normalización de importes

El sistema reconoce importes en formato argentino (coma decimal, punto de miles).  
Ejemplo: `1.234,56` → `1234.56`.

### Columnas vacías eliminadas

Las columnas de conceptos (a partir de col 10) donde todos los empleados tienen 0 se eliminan
del output. Esto reduce el tamaño del archivo y facilita su lectura.

### Caso de empleados en licencia vacacional

Un empleado que toma licencia vacacional ese mes puede no tener los conceptos TOTAL PROV
(Provisión Vacaciones + Provisión SAC) ni Base Imponible (Ganancias). Esto es comportamiento
correcto: las provisiones se consumen al liquidar las vacaciones. Las columnas mostrarán 0 para
ese empleado en ese período.

---

## 6. Interfaz de usuario

### Acceso

Sin usuario ni contraseña. Disponible desde cualquier navegador moderno.

URL: `http://conversor.contadoresbma.com.ar`

### Pantalla principal

> Corregido 2026-07-23: una sola área de carga (no tres) — ver §3.

Una sola pantalla con un área de carga (arrastrar y soltar, o clic para abrir el explorador):

| Área | Estado | Función |
|---|---|---|
| Grilla Informe de Liquidación | Requerido (único archivo) | Archivo principal y único de conversión |

### Flujo de uso

1. Acceder a la URL
2. Subir la Grilla Informe de Liquidación (único archivo, obligatorio)
3. Hacer clic en **"Convertir y Descargar"**
4. Esperar entre 5 y 20 segundos (procesamiento con spinner visible)
5. El navegador descarga automáticamente el archivo STR generado

### Mensajes de error

| Situación | Mensaje |
|---|---|
| No se seleccionó archivo | "No se recibió el archivo." |
| Formato incorrecto | "El archivo debe ser .xlsx o .xls" |
| Archivo corrupto / inválido | "Error al procesar el archivo" |
| Template no encontrado en servidor | "Template STR no encontrado en el servidor. Contactar al administrador." |

---

## 7. Especificaciones técnicas

| Componente | Detalle |
|---|---|
| Lenguaje backend | PHP 8.3 |
| Librería Excel | PhpSpreadsheet 2.x |
| Frontend | HTML5 + CSS3 (sin framework JS) |
| Servidor | Ferozo Shared Hosting (LiteSpeed) — mismo servidor que www.contadoresbma.com.ar |
| URL | conversor.contadoresbma.com.ar |
| Almacenamiento | Sin base de datos. Los archivos no se almacenan en el servidor. |
| Repositorio | https://gitlab.com/olvidata/conversor-bma.git |
| Deploy | Script Python (FTPS + vendor.zip extraído por PHP ZipArchive) |

---

## 8. Exclusiones del alcance

- Almacenamiento de archivos procesados en el servidor
- Historial de conversiones
- Autenticación de usuarios
- Envío automático del STR al cliente final
- Integración directa con Bejerman Web/Onvio (API)
- Aplicación móvil
- Modificación del template STR ENCABEZADO VALIDO.xlsx desde la interfaz

---

## 9. Presupuesto

### Desarrollo (versión 1.0)

| Área funcional | USD |
|---|---|
| Motor de conversión (Informe → STR) | 67 |
| Interfaz web (carga + descarga) | 17 |
| Configuración web, dominio y deploy | 50 |
| Documentación | — *(sin cargo)* |
| Tokens IA (infraestructura de desarrollo) | 100 |
| Subtotal | 234 |
| Descuento por referido (15%) | −35 |
| **Total** | **USD 199** |

El hosting no genera costo adicional: el sistema corre sobre el servidor existente de
www.contadoresbma.com.ar. Los cambios funcionales futuros se presupuestan por separado.

### Condiciones comerciales

- 50% al inicio del desarrollo / 50% a la entrega
- Sin cláusula de vencimiento de la oferta

---

## 10. Soporte

**OlvidataSoft**  
Email: olvidatasoft@gmail.com  
WhatsApp: +54 9 221 440-2340  
Web: https://olvidata.com.ar

---

*Documento generado el 29 de junio de 2026*  
*Versión del sistema: 1.0 — en producción desde 2026-06-25*
