# Manual de usuario — Prácticas y Producción Mensual

**Sistema:** LabIPAC  
**Versión:** 1.1  
**Fecha:** Junio 2026

---

## ¿Qué es este módulo?

El módulo de **Prácticas** permite armar y gestionar el catálogo de estudios médicos que ofrece el laboratorio. Cada práctica tiene un precio de venta y se compone de una o más **unidades bioquímicas** (los análisis individuales que la integran). El sistema calcula automáticamente cuánto suman los componentes y avisa si el precio de venta es menor que el costo de producción.

---

## Conceptos clave

| Concepto | Qué es |
|----------|--------|
| **Unidad bioquímica** | El análisis individual más pequeño (ej: Glucemia, Hemograma, Colesterol). Tiene su propio precio. |
| **Práctica** | El estudio médico que se le ofrece al paciente. Está compuesta por una o más unidades bioquímicas. Tiene un precio de venta propio. |
| **Sumatoria de componentes** | La suma de los precios de todas las unidades bioquímicas que forman la práctica. Se calcula automáticamente. |
| **RN-01** | Alerta de negocio: se activa cuando el precio de venta de una práctica es menor que la sumatoria de sus componentes. |

---

## Acceder al módulo

En el menú lateral, hacer clic en **Prácticas**.

Se muestra la lista de todas las prácticas, tanto activas como eliminadas.

---

## Listado de prácticas

La tabla muestra:

| Columna | Descripción |
|---------|-------------|
| **#** | Número de identificación interno |
| **Nombre** | Nombre del estudio |
| **Precio actual** | Precio de venta al paciente |
| **Sumatoria componentes** | Suma de precios de las unidades bioquímicas que la componen |
| **Estado** | `Activo` / `Inactivo` / `Eliminado` |
| **Acciones** | Ver detalle, editar, eliminar o reactivar |

> Si la sumatoria de componentes **supera el precio de venta**, aparece un ícono de advertencia ⚠️ en la columna "Sumatoria". Esto indica que el precio está por debajo del costo (alerta RN-01).

Se puede buscar por nombre y ordenar por cualquier columna haciendo clic en el encabezado.

---

## Crear una nueva práctica

1. Hacer clic en el botón **Nueva práctica** (arriba a la derecha).
2. Completar el formulario:

### Datos generales

| Campo | Requerido | Descripción |
|-------|-----------|-------------|
| **Nombre** | Sí | Nombre del estudio. Máximo 150 caracteres. |
| **Precio actual** | Sí | Precio de venta al paciente. Puede ser $0 si todavía no tiene precio definido. |
| **Activo** | — | Tildado por defecto. Destildar para crear la práctica en estado inactivo. |

### Composición — unidades bioquímicas

1. En el campo **Unidades bioquímicas**, hacer clic y buscar o seleccionar las unidades que forman el estudio.
2. Se pueden seleccionar **una o más unidades** usando el buscador integrado.
3. A medida que se seleccionan unidades, el sistema actualiza automáticamente el recuadro azul **"Sumatoria de componentes"**.

### Alerta de precio

Mientras se carga el formulario, si el precio ingresado es menor que la sumatoria de los componentes, aparece el siguiente aviso en naranja:

> ⚠️ **Atención:** el precio de la práctica es menor a la sumatoria de sus componentes.

Esto no impide guardar — es solo un aviso para que el operador revise si el precio es correcto antes de confirmar.

4. Hacer clic en **Guardar**.

---

## Ver el detalle de una práctica

Desde el listado, hacer clic en el ícono 👁 de la práctica deseada.

Se muestra:

- **Información general:** nombre, precio de venta, sumatoria de componentes y estado.
- **Tabla de composición:** todas las unidades bioquímicas que forman la práctica con su precio unitario, cantidad y subtotal.
- **Total sumatoria** al pie de la tabla.

Si alguna unidad bioquímica fue desactivada, se muestra con la etiqueta gris `Inactiva` junto a su nombre.

Si el precio de venta es menor a la sumatoria, se muestra la advertencia ⚠️ **"Precio menor a sumatoria"** en la ficha.

---

## Editar una práctica

1. Desde el listado, hacer clic en el ícono ✏️.
2. Se pueden modificar el nombre, el precio y la composición (agregar o quitar unidades).
3. Si la práctica tiene componentes inactivos, se muestra un aviso en naranja indicando cuáles son. Se conservan en la práctica pero no aparecen disponibles para nuevas selecciones.
4. La sumatoria y la alerta de precio se recalculan en tiempo real al hacer cambios.
5. Hacer clic en **Guardar cambios**.

---

## Eliminar una práctica

1. Desde el listado, hacer clic en el ícono 🗑️.
2. Se pide confirmación con el nombre de la práctica.
3. Al confirmar, la práctica queda marcada como **Eliminada** y deja de mostrarse como disponible. **No se borra físicamente** — puede reactivarse.

---

## Reactivar una práctica eliminada

Las prácticas eliminadas siguen apareciendo en el listado con el estado `Eliminado` y un botón **Reactivar**.

1. Hacer clic en **Reactivar** sobre la práctica deseada.
2. Confirmar en el cuadro de diálogo.
3. La práctica vuelve al estado activo con todos sus datos intactos.

---

## Preguntas frecuentes

**¿Puedo tener dos prácticas con el mismo nombre?**  
Sí, el sistema no bloquea nombres repetidos, pero se recomienda usar nombres únicos para evitar confusión.

**¿Qué pasa si cambio el precio de una unidad bioquímica?**  
El cambio se refleja automáticamente en la sumatoria de todas las prácticas que la contienen. El precio de venta de la práctica **no cambia** — hay que editarlo manualmente si es necesario.

**¿Puedo guardar una práctica con precio $0?**  
Sí. Es útil cuando la práctica está en construcción o el precio aún no está definido.

**¿La alerta ⚠️ me impide guardar?**  
No. Es solo informativa. El sistema permite guardar aunque el precio sea menor a la sumatoria.

**¿Qué es una unidad inactiva?**  
Es una unidad bioquímica que fue desactivada en el catálogo. Las prácticas que ya la contenían la conservan, pero no puede agregarse a prácticas nuevas.

---

---

# Módulo Producción Mensual

## ¿Qué es este módulo?

La **Producción Mensual** registra todos los estudios realizados en un mes determinado. Funciona como un cuaderno de carga donde el operador va anotando qué estudios (prácticas o unidades sueltas) se realizaron, en qué cantidad y a qué precio, para obtener el total facturado estimado del período.

---

## Conceptos clave

| Concepto | Qué es |
|----------|--------|
| **Período** | Un mes y año específico (ej: "Junio 2026"). Cada período es independiente. |
| **Línea** | Un renglón del período: un estudio realizado con su tipo, nombre, precio y cantidad. |
| **Snapshot de precio** | El precio se copia en el momento de agregar la línea. Si después se modifica el precio de la práctica, la línea no cambia. |
| **Período actual** | El período cuyo mes y año coincide con la fecha de hoy. Muestra la etiqueta verde 🟢 **Período actual**. |
| **Período histórico** | Cualquier período de un mes o año anterior. Muestra la etiqueta naranja 🟠 **Período histórico**. Los cambios en períodos históricos modifican datos pasados. |
| **Total estimado** | Suma de todos los subtotales (precio × cantidad) de las líneas del período. |

---

## Acceder al módulo

En el menú lateral, hacer clic en **Producción Mensual**.

Se muestra la lista de todos los períodos registrados, ordenados del más reciente al más antiguo.

---

## Listado de períodos

La tabla muestra:

| Columna | Descripción |
|---------|-------------|
| **Período** | Mes y año (ej: Junio 2026) |
| **Líneas** | Cantidad de ítems cargados en ese período |
| **Total estimado** | Suma de todos los subtotales del período |
| **Notas** | Observaciones opcionales (se truncan si son largas) |
| **Creado** | Fecha en que se creó el período |
| **Acciones** | Ver / cargar líneas, eliminar |

---

## Crear un nuevo período

1. Hacer clic en **Nuevo período** (arriba a la derecha).
2. Completar:

| Campo | Requerido | Descripción |
|-------|-----------|-------------|
| **Mes** | Sí | Seleccionar de la lista (Enero a Diciembre). Por defecto muestra el mes actual. |
| **Año** | Sí | Número de año (ej: 2026). Por defecto muestra el año actual. |
| **Notas** | No | Observaciones libres. Máximo 500 caracteres. |

3. Hacer clic en **Crear período**. El sistema redirige directamente al detalle del período para comenzar a cargar líneas.

---

## Cargar estudios en un período (Detalle)

Desde el listado, hacer clic en **Ver / Cargar** sobre el período deseado.

Se muestra la pantalla de detalle con:

- **Encabezado:** nombre del período y etiqueta de estado (actual o histórico).
- **Tabla de líneas:** todos los ítems cargados hasta el momento.
- **Panel resumen** (a la derecha): total de líneas y total estimado del período.

### Agregar una línea

1. Hacer clic en el botón **Agregar ítem**.
2. En la ventana emergente, completar:

**Tipo de ítem** — elegir una opción:
- **Práctica:** un estudio compuesto (ej: Perfil lipídico, Hemograma completo).
- **Unidad bioquímica:** un análisis individual suelto (ej: Glucemia, Colesterol).

**Selección del ítem:**
- Según el tipo elegido, aparece el selector correspondiente con búsqueda integrada.
- Al seleccionar el ítem, el sistema **completa automáticamente el precio vigente** del catálogo.

**Precio unitario:**
- Se completa automáticamente con el precio del catálogo.
- Puede modificarse manualmente si el precio cobrado fue distinto al del catálogo.

**Cantidad:**
- Por defecto es 1. Puede ingresarse cualquier valor entre 1 y 9.999.

3. Hacer clic en **Agregar**.

> El precio y el nombre del ítem se guardan como una **copia fija (snapshot)** en el momento de agregar. Cambios posteriores en el catálogo no afectan las líneas ya cargadas.

---

## Editar una línea

1. En la tabla del período, hacer clic en el ícono ✏️ de la línea a modificar.
2. Se abre una ventana emergente con el nombre del ítem (no editable) y los campos:
   - **Cantidad:** modificar la cantidad realizada.
   - **Precio unitario:** corregir el precio si es necesario.
3. Hacer clic en **Guardar**.

---

## Eliminar una línea

1. En la tabla del período, hacer clic en el ícono 🗑️ de la línea.
2. Confirmar en el cuadro de diálogo.
3. La línea se elimina y el total estimado se recalcula.

---

## Eliminar un período completo

1. Desde el listado, hacer clic en el ícono 🗑️ del período.
2. El sistema advierte que **se perderán todas sus líneas**.
3. Confirmar para eliminar el período y todo su contenido.

> Esta acción no tiene rollback. Si se necesita preservar los datos, no eliminar el período.

---

## Panel de resumen

En la pantalla de detalle, el panel derecho siempre muestra:

- **Total de líneas:** cantidad de ítems cargados.
- **Total estimado:** suma total del período en pesos.
- Si es un período histórico, una advertencia recordando que los cambios modifican datos pasados.
- Las notas del período (si tiene).

---

## Período actual vs. período histórico

| | Período actual | Período histórico |
|---|---|---|
| **Etiqueta** | 🟢 Período actual | 🟠 Período histórico |
| **Cuándo aparece** | El mes/año coincide con hoy | Cualquier mes/año anterior |
| **Se puede editar** | Sí, es el uso normal | Sí, pero con advertencia |
| **Recomendación** | Cargar los estudios del día | Solo corregir errores pasados |

---

## Preguntas frecuentes

**¿Puedo tener más de un período para el mismo mes?**  
No. El sistema no lo bloquea explícitamente, pero se recomienda tener un único período por mes para que los totales sean coherentes.

**Si cambio el precio de una práctica, ¿se actualiza en los períodos ya cargados?**  
No. El precio queda fijo en el momento de la carga (snapshot). Los períodos anteriores no se ven afectados.

**¿Puedo cargar una práctica que fue eliminada del catálogo?**  
No. Solo aparecen en el selector las prácticas y unidades activas al momento de agregar.

**¿El total estimado incluye impuestos?**  
No. Es la suma directa de precio × cantidad. Cualquier cálculo impositivo debe hacerse externamente.

**¿Puedo cargar la misma práctica más de una vez en el mismo período?**  
Sí. Cada vez que se agrega un ítem se crea una línea nueva, independientemente de si ese ítem ya fue cargado antes.
