# Manual de usuario — Integración FABA

**Sistema:** LabIPAC  
**Versión:** 1.0  
**Fecha:** Junio 2026

---

## ¿Qué es FABA y para qué se integra?

**FABA** (Federación Bioquímica de la Provincia de Buenos Aires) administra el padrón de afiliados y el catálogo de prácticas de las mutuales y obras sociales que operan en la provincia.

La integración de LabIPAC con FABA permite dos cosas concretas:

1. **Importar el catálogo de prácticas** que cada mutual reconoce y liquida, para saber qué estudios están cubiertos y bajo qué código.
2. **Consultar datos de un paciente** directamente en el padrón de FABA, evitando la carga manual y reduciendo errores de afiliación.

---

## Conceptos clave

| Concepto | Qué es |
|----------|--------|
| **Mutual / Obra social** | En LabIPAC son la misma entidad. Cada mutual tiene su propio catálogo de prácticas y sus propios afiliados. |
| **Analito FABA** | El nombre que FABA le da a un estudio bioquímico dentro del catálogo de una mutual. Incluye un código numérico único por mutual. |
| **Unidad bioquímica local** | El mismo estudio, pero registrado en el catálogo propio del laboratorio (ej: "Glucemia"). |
| **Vínculo analito ↔ UB local** | La conexión manual que establece que el analito FABA de una mutual corresponde a una unidad bioquímica del laboratorio. **Sin este vínculo, el sistema no puede relacionar lo que pide la mutual con lo que hace el laboratorio.** |
| **Afiliado** | El paciente registrado en una mutual. Tiene un número de afiliado, relación con el titular (titular, cónyuge, hijo, etc.) y estado de cobertura. |
| **Web Service FABA (AOL V2)** | La interfaz que FABA expone para consultar afiliados y catálogos. Requiere credenciales (usuario y contraseña) asignadas por FABA. |

---

## Acceder al módulo

En el menú lateral, hacer clic en **Integración FABA**.

> ⚠️ Este módulo requiere perfil **Administrador** o superior.

---

## Paso 1 — Configurar las credenciales FABA

Antes de poder usar cualquier función de la integración, el sistema necesita las credenciales que FABA asigna al laboratorio.

Si las credenciales no están configuradas, la pantalla principal mostrará una advertencia en amarillo indicando que la sincronización no está disponible.

**Para configurarlas:** contactar al responsable técnico del sistema para que ingrese el usuario y contraseña FABA en la configuración del servidor. No se ingresan desde la pantalla web por razones de seguridad.

---

## Paso 2 — Sincronizar el catálogo de mutuales

La pantalla principal de **Integración FABA** muestra la tabla de mutuales que el sistema tiene registradas.

Para actualizar la lista desde FABA:

1. Hacer clic en **Sincronizar mutuales** (arriba a la derecha).
2. Confirmar en el cuadro de diálogo.
3. El sistema descarga el listado de mutuales desde FABA y actualiza la tabla local: agrega las nuevas, actualiza las existentes e inactiva las que FABA ya no devuelve.
4. Al finalizar, se muestra un resumen: *"X nuevas, Y actualizadas, Z inactivadas"*.

La tabla de mutuales muestra:

| Columna | Descripción |
|---------|-------------|
| **Nombre** | Nombre de la mutual según FABA |
| **ID FABA** | Identificador numérico interno de FABA |
| **Cód. Facturante** | Código requerido por FABA para emitir órdenes |
| **OSDE** | Indica si la mutual usa el circuito especial OSDE |
| **Estado** | Activo / Inactivo |
| **Últ. Sync Analitos** | Última vez que se sincronizó el catálogo de prácticas de esa mutual |
| **Acciones** | Acceder al catálogo de analitos de cada mutual |

---

## Paso 3 — Sincronizar los analitos de cada mutual

Cada mutual tiene su propio catálogo de prácticas bioquímicas con nombres y códigos propios. Este catálogo debe importarse de forma **individual por mutual**.

1. En la tabla de mutuales, hacer clic en **Ver analitos** de la mutual deseada.
2. En la pantalla de analitos, hacer clic en **Sincronizar analitos**.
3. El sistema descarga el catálogo de esa mutual desde FABA. Al finalizar, muestra cuántos analitos se insertaron, actualizaron o inactivaron.

> ℹ️ Esto debe hacerse para cada mutual que el laboratorio opere. FABA actualiza periódicamente sus catálogos; se recomienda re-sincronizar cuando FABA notifique cambios en las coberturas.

---

## Paso 4 — Vincular analitos FABA con las unidades del laboratorio ⚠️ Paso crítico

Este es el paso más importante de la configuración. Sin él, el sistema no puede saber que el analito **"001 - Glucemia"** de la Mutual X es lo mismo que la unidad bioquímica **"Glucemia"** del catálogo del laboratorio.

**¿Por qué es por mutual?** Cada mutual puede tener códigos distintos para el mismo estudio. La "Glucemia" en IOMA puede tener el código 001 y en OSDE el código 540. Por eso el vínculo debe hacerse para cada mutual por separado.

### Cómo vincular

En la pantalla de analitos de una mutual:

1. La tabla muestra tres columnas clave: **Cód. FABA**, **Nombre FABA** y **UB Local vinculada**.
2. Los analitos sin vincular muestran el texto *"Sin vincular"* en la última columna.
3. Para vincular: en la columna **Vincular**, seleccionar del desplegable la unidad bioquímica local que corresponde a ese analito.
4. El vínculo se guarda automáticamente al seleccionar.

### Filtros disponibles para facilitar el trabajo

| Filtro | Opciones |
|--------|----------|
| **Buscar** | Por nombre o código del analito FABA |
| **Estado** | Activos / Inactivos / Todos |
| **Vínculo** | Vinculados / Sin vincular / Todos |

> 💡 Se recomienda usar el filtro **"Sin vincular"** para identificar rápidamente los analitos que aún necesitan ser mapeados.

### Estado del vínculo

| Indicador | Significado |
|-----------|-------------|
| Badge azul con nombre | El analito está vinculado a una UB local |
| *"Sin vincular"* en gris | El analito FABA no tiene correspondencia local asignada |
| Badge gris "Inactivo" | FABA ya no incluye ese analito en el catálogo de la mutual |

---

## Consultar un afiliado en FABA

Esta función permite buscar los datos de un paciente directamente en el padrón de FABA, sin carga manual.

### Acceder

Desde el menú de **Integración FABA**, hacer clic en **Consultar afiliado**.

### Tipos de búsqueda

| Opción | Cuándo usarla |
|--------|---------------|
| **Por Documento** | Cuando el paciente trae su DNI. Permite buscar por DNI, Pasaporte o CUIL. |
| **Por Legajo** | Cuando el paciente tiene el número de afiliado de la mutual. |

### Cómo realizar la consulta

1. Seleccionar la **mutual** a la que pertenece el paciente.
2. Elegir el tipo de búsqueda (Documento o Legajo).
3. Ingresar el número correspondiente.
4. Hacer clic en **Consultar**.

### Resultado

Si el afiliado es encontrado en FABA, el sistema muestra:

| Dato | Descripción |
|------|-------------|
| **Apellido y Nombre** | Nombre completo según el padrón FABA |
| **Documento** | Tipo y número |
| **Número de afiliado** | Código completo de afiliación en esa mutual |
| **Relación** | Vínculo del afiliado con el titular del plan (ver tabla abajo) |
| **Fecha de nacimiento** | Según FABA |
| **Sexo** | Masculino / Femenino / No especificado |
| **Estado** | Estado de la cobertura en FABA |

Si el afiliado **no es encontrado**, el sistema muestra un mensaje de advertencia con el detalle devuelto por FABA.

### Relación del afiliado con el titular

| Relación | Quién es |
|----------|----------|
| **Titular** | El afiliado principal del plan |
| **Cónyuge** | Esposo/a o conviviente del titular |
| **Hijo/a** | Hijo o hija a cargo del titular |
| **Otro familiar** | Otro familiar dependiente del titular |

---

## Crear un paciente a partir de la consulta FABA

Una vez encontrado el afiliado, el sistema ofrece el botón **Crear paciente con estos datos**.

Al hacer clic, se abre el formulario de nuevo paciente con los siguientes campos **pre-completados automáticamente** con los datos de FABA:

- Nombre y apellido
- Tipo y número de documento
- Fecha de nacimiento
- Sexo
- Número de afiliado
- Mutual a la que pertenece

El operador solo debe verificar los datos, completar lo que falte (por ejemplo, el teléfono o dirección), y guardar.

> ✅ Esto reduce errores de tipeo y asegura que el número de afiliado y la mutual queden correctamente asociados al paciente desde el inicio.

---

## Actualizar datos de un paciente ya registrado desde FABA

Si un paciente ya existe en el sistema y se necesita actualizar sus datos de afiliación:

1. Ir a **Pacientes** y abrir el paciente deseado en modo edición.
2. En el formulario de edición, utilizar la opción de **consulta FABA** para buscar nuevamente al afiliado.
3. Los datos devueltos por FABA actualizan automáticamente los campos correspondientes en el formulario.
4. Hacer clic en **Guardar** para confirmar los cambios.

> ⚠️ Los datos del paciente no se actualizan solos. El paso de **Guardar** es obligatorio para que los cambios queden registrados en el sistema.

---

## Resumen del flujo completo de configuración

```
1. Configurar credenciales FABA (una sola vez, por el técnico)
		↓
2. Sincronizar mutuales desde el panel FABA
		↓
3. Para cada mutual que opere el laboratorio:
   → Sincronizar analitos de esa mutual
   → Vincular cada analito FABA con la unidad bioquímica local correspondiente
		↓
4. El sistema ya puede relacionar prácticas de FABA con el catálogo del laboratorio
		↓
5. Al registrar pacientes: consultar afiliado en FABA y crear/actualizar con datos pre-completados
```

---

## Preguntas frecuentes

**¿Cuándo hay que re-sincronizar mutuales o analitos?**  
Cuando FABA notifique cambios en coberturas o cuando aparezcan analitos nuevos en las liquidaciones. No hay sincronización automática; siempre se activa manualmente.

**¿Qué pasa si un analito FABA no tiene vínculo local?**  
El sistema registra el analito pero no puede asociarlo a ningún estudio del laboratorio. Para que la práctica quede correctamente clasificada en los registros del laboratorio, el vínculo debe completarse.

**¿Un mismo estudio puede tener distintos códigos en distintas mutuales?**  
Sí. El código FABA es propio de cada mutual. Por eso el vínculo se configura por separado para cada una.

**¿Qué pasa si FABA no encuentra al afiliado?**  
El sistema muestra el mensaje que devuelve FABA (ej: "afiliado no encontrado", "cobertura suspendida"). En ese caso el paciente puede cargarse manualmente sin datos de FABA.

**¿Las credenciales FABA tienen vencimiento?**  
Sí, según las políticas de FABA. Si la sincronización empieza a fallar con errores de autenticación, contactar a FABA para renovar el acceso.

**¿La consulta FABA consume costos o tiene límite de uso?**  
Depende del contrato del laboratorio con FABA. Consultar directamente con FABA ([faba.org.ar](https://www.faba.org.ar)).
