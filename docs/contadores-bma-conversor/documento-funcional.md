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

Automatizar la conversión del **Informe de Liquidación** exportado desde Bejerman Web al formato
**STR** requerido por SERVICIO TERAPIA RENAL S.A., eliminando el trabajo manual y asegurando
consistencia en el resultado.

### 1.3 Alcance de la versión 1.0

- Conversión automática de Informe de Liquidación (`.xls` / `.xlsx`) al archivo STR destino
- Enriquecimiento opcional con Grilla de Liquidación (Lugar de Pago, Centro de Costos, Obra Social)
- Enriquecimiento opcional con Cubo de Liquidación (columna Costos)
- Interfaz web sin instalación, sin usuario ni contraseña
- Disponible desde cualquier navegador con acceso a internet

---

## 2. Flujo general del sistema

```
[Usuario]
    │
    ├── Sube Informe de Liquidación (.xls)    ← obligatorio
    ├── Sube Grilla de Liquidación (.xls)     ← opcional: Lugar de Pago, CC, OS
    └── Sube Cubo de Liquidación (.xlsx)      ← opcional: columna Costos
                    │
                    ▼
          [Conversor BMA — convert.php]
                    │
                    ▼
          STR-INFORME-{nombre}.xlsx           ← descarga automática
```

El sistema procesa los archivos en el servidor y devuelve el archivo STR al navegador del usuario
sin almacenar ningún dato.

---

## 3. Archivos de entrada

### 3.1 Informe de Liquidación (obligatorio)

Origen: exportación desde Bejerman Web (Onvio) → módulo Liquidación de Sueldos.  
Formato: `.xls` o `.xlsx`.

El Informe tiene formato **jerárquico por empleado**: cada empleado ocupa un bloque de filas
con datos de identificación, fila SIPA, filas de conceptos y una fila de resumen.

**Datos que extrae el sistema:**

| Dato | Origen en el Informe | Destino en STR |
|---|---|---|
| Legajo | Fila empleado, col 3 | Col 1 |
| Apellido y Nombre | Fila empleado, col 7 | Col 2 |
| CUIL | Fila SIPA, col 67 | Col 4 |
| Sector | Fila empleado, col 23 | Parte 1 de col 7 Especialidad |
| Calificación | Fila empleado, col 32 | Parte 2 de col 7 Especialidad |
| Categoría | Fila empleado, col 51 | Col 6 |
| Fecha Ingreso | Fila empleado, col 41 | Col 9 |
| Conceptos (izq. y der.) | Filas de concepto | Cols 10+ |
| Haberes rem. / no rem. | Fila resumen | Total haberes, Bruto |
| Retenciones | Fila resumen | Col Retenciones |
| Neto a cobrar | Fila resumen | Cols Neto a Cobrar, Neto |

### 3.2 Grilla de Liquidación (opcional)

Origen: exportación desde Bejerman Web (Onvio).  
Formato: `.xls` o `.xlsx`.  
Uso: enriquece columnas que no están disponibles en el Informe.

| Dato | Destino en STR |
|---|---|
| Lugar de Pago | Col 3 |
| Centro de Costos | Col 5 (número entero) |
| Código Obra Social | Col 8 |

Si no se sube la Grilla, las columnas 3, 5 y 8 quedan vacías en el STR.

### 3.3 Cubo de Liquidación (opcional)

Origen: exportación desde Bejerman Web (Onvio).  
Formato: `.xls` o `.xlsx`.  
Uso: provee únicamente la columna **Costos** del STR.

Si no se sube el Cubo, la columna Costos queda en 0 para todos los empleados.

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

| Col | Etiqueta | Fuente |
|---|---|---|
| 1 | Legajo | Informe |
| 2 | Apellido y Nombre | Informe |
| 3 | Lugar de Pago | Grilla (o vacío si no se sube) |
| 4 | CUIL | Informe |
| 5 | CC | Grilla (o vacío si no se sube) |
| 6 | Categoría | Informe |
| 7 | Especialidad | Informe: Sector + " - " + Calificación |
| 8 | OS | Grilla (o vacío si no se sube) |
| 9 | Fecha Ingreso | Informe (formato `d/m/A`) |

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
| Redondeo | Concepto 9999 |
| Neto a Cobrar | Neto cobrado según resumen del Informe |
| Total haberes | Haberes remunerativos + no remunerativos |
| Base Imponible | Concepto 399 |
| Neto | Igual a Neto a Cobrar |
| Retenciones | Total de retenciones según resumen del Informe |
| Bruto | Igual a Total haberes |
| Costos | Desde Cubo (o 0 si no se sube) |

### 4.5 Formato visual del archivo de salida

- Filas 1-4: encabezados con colores corporativos (azul oscuro, azul medio, azul claro)
- Filas de datos: filas pares con fondo azul muy suave (efecto zebra)
- Encabezado fijo (freeze en fila 5): al hacer scroll, el encabezado permanece visible
- Columnas 1-9: ancho automático ajustado al contenido
- Columnas 10+: ancho fijo de 11 unidades

---

## 5. Reglas de negocio

### Empleados incluidos en el output

Solo aparecen los empleados que tienen al menos un concepto en el Informe del período procesado.
Empleados sin actividad ese mes no se incluyen.

### Empleados nuevos

Si un empleado aparece en el Informe pero no estaba en períodos anteriores, se incluye
automáticamente. No se requiere ninguna actualización manual del template.

### Orden de los empleados

Los empleados aparecen en el mismo orden en que figuran en el Informe (primera aparición del legajo).

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

Una sola pantalla con tres áreas de carga:

| Área | Estado | Función |
|---|---|---|
| Informe de Liquidación | Requerido | Archivo principal de conversión |
| Grilla de Liquidación | Opcional | Enriquece Lugar de Pago, CC, OS |
| Cubo de Liquidación | Opcional | Enriquece columna Costos |

Cada área acepta arrastrar el archivo o hacer clic para abrir el explorador.

### Flujo de uso

1. Acceder a la URL
2. Subir el Informe de Liquidación (obligatorio) y los opcionales disponibles
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
