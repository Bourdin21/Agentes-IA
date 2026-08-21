# Memoria - Analista funcional

## Proyecto: eleven-la-plata
## Ultima actualizacion: 2026-08-20

## Definiciones vigentes

### Modulos/features analizados
Barrido de Discovery (2026-08-20) sobre: Alquileres (alta/edición/finalización, contadores por máquina), cambio de máquina dentro de un alquiler/contrato activo, Notificaciones ("avisos"), Incidencias, y verificación cruzada de items pendientes de sesiones anteriores (Contratos con precio en texto libre, curación de Artículos, roles/Identity).

### Reglas funcionales acordadas
- `AlquilerService.CreateAsync` valida los contadores iniciales (`ContadorBNInicial`/`ContadorColorInicial`) contra el `HistoriaContador` de la máquina elegida (contador anterior y siguiente en el tiempo) antes de dar de alta — esta es la regla de integridad vigente para el alta.
- El alquiler queda vinculado a **una sola máquina a la vez** vía `Alquiler.MaquinaId` (escalar, no histórico).

### Criterios de aceptacion vigentes

## Análisis — H1: Cambio de máquina en Alquiler/Contrato sin validar (2026-08-20)
**Aprobado por:** Joaquín (owner del proyecto) — "solucionar bug crítico, el resto depende de definiciones con el usuario". H2 (Avisos) y H3–H7 quedan explícitamente fuera de este ciclo, pendientes de definición.

**Resumen del problema:** `AlquilerService.UpdateAsync` y `ContratoService.UpdateAsync` permiten cambiar `MaquinaId` (y en Alquiler, además `ContadorBNInicial`/`ContadorColorInicial`) sin repetir la validación de consistencia contra `HistoriaContador` que sí aplica `AlquilerService.CreateAsync`. Resultado: se puede guardar un alquiler/contrato con contadores iniciales incompatibles con el historial real de la máquina (ej. menor al último contador registrado), lo que corrompe la base de cálculo de facturación por copia.

**Alcance incluido (este ciclo):**
- Reaplicar en `UpdateAsync` (Alquiler y Contrato) la misma validación de contadores que ya existe en `AlquilerService.CreateAsync` cuando `MaquinaId` cambia respecto al valor guardado.
- Si al cambiar de máquina no existe un `HistoriaContador` que cubra el nuevo `ContadorBNInicial`/`ContadorColorInicial`, crear uno (mismo criterio "Regla de Negocio Legacy" que ya usa `CreateAsync`), para no dejar el contador inicial "flotando" sin respaldo en el historial de la máquina.
- Mensaje de error claro al usuario si los contadores no son consistentes (mismo texto/formato que ya usa Create).

**Alcance excluido (fuera de este ciclo — pasa a "resto, depende de definiciones"):**
- No se crea una pantalla/acción dedicada "Cambiar Máquina" separada del Edit genérico.
- No se agrega un historial estructurado multi-máquina por alquiler (tabla nueva tipo `AlquilerMaquinaHistorial`) — la vista de detalle sigue mostrando el consumo en base a la máquina *actual* del alquiler. Si en el futuro se cambia de máquina, el consumo previo a ese cambio seguirá sin aparecer en el detalle de ese alquiler puntual (mismo comportamiento actual), pero al menos los datos que se guardan van a ser consistentes y no van a corromper la facturación de la máquina.
- No se toca Notifications/Avisos (H2) ni los items H3–H7.

**Reglas funcionales:**
1. Al guardar Edit de un Alquiler donde `MaquinaId` cambió respecto al valor original: validar `ContadorBNInicial`/`ContadorColorInicial` contra el `HistoriaContador` anterior y siguiente de la nueva máquina (idéntico criterio que Create). Si no pasa, rechazar con el mismo mensaje de error que usa Create.
2. Al guardar Edit de un Alquiler donde `MaquinaId` NO cambió: mantener el comportamiento actual (no re-pedir contadores ya validados en el alta, evitar falsos rechazos sobre datos ya consistentes).
3. **Corrección de alcance tras revisar `ContratoService`:** `Contrato` no tiene campos de contador (`ContadorBNInicial`/`ContadorColorInicial`) ni su `CreateAsync` valida nada contra `HistoriaContador` — es una entidad más simple (Fecha/Condición/Monto/Cliente/Máquina). Por lo tanto `ContratoService.UpdateAsync` es consistente con su propio Create: no hay ninguna validación que "falte reaplicar" ahí. **El bug confirmado queda acotado exclusivamente a `AlquilerService.UpdateAsync`.** Se descarta tocar `ContratoService` en este ciclo.

**Criterios de aceptación:**
- CA1: Editar un Alquiler cambiando la máquina a una con contador inicial MENOR al último `HistoriaContador` registrado de esa máquina → el sistema rechaza el guardado con mensaje de error, igual que en Create.
- CA2: Editar un Alquiler cambiando la máquina a una con contador inicial consistente → el sistema guarda correctamente y, si corresponde, crea el `HistoriaContador` inicial.
- CA3: Editar un Alquiler sin cambiar la máquina (solo otro campo, ej. Observación) → el guardado funciona igual que hoy, sin nuevas validaciones de por medio.
- CA4: Los alquileres/contratos existentes en producción no se ven afectados retroactivamente por este fix (es una validación hacia adelante, no una corrección de datos históricos).

**Impacto por capa (preliminar):** Negocio (`Eleven.Infrastructure/Services/AlquilerService.cs`, `ContratoService.cs`) — sin cambios de esquema, sin nueva migración EF esperada.

**Riesgos y supuestos:**
- Supuesto: no hay hoy en producción alquileres/contratos con contadores ya inconsistentes que esta validación bloquearía si alguien los vuelve a editar (riesgo bajo, a confirmar en QA con una consulta a la base antes de cerrar).
- Riesgo: si el equipo (técnicos) efectivamente necesita cambiar la máquina de un alquiler seguido, la validación estricta puede generar fricción — pero es la fricción correcta (evita guardar datos que rompen la facturación). Si se vuelve un problema de UX, eso alimenta la definición pendiente de una pantalla "Cambiar Máquina" dedicada (fuera de este ciclo).

### Supuestos y dependencias
- El negocio es de renta de equipos de impresión con facturación basada en contador de copias (B/N y Color) por máquina — la integridad de `HistoriaContador` es crítica para la facturación.
- Notifications/"avisos" está pensado como sistema in-app (entidad + servicio + UI ya existen desde el scaffold base), no como email/WhatsApp.

### Exclusiones confirmadas
- Este barrido es **Discovery únicamente**: no se implementó ningún fix de los detectados abajo. Quedan para pasar por Análisis → Diseño → Arquitectura → Presupuesto (gate cliente) antes de Implementación, según el flujo del orquestador.

## Hallazgos (gaps / bugs funcionales) — 2026-08-20

### 🔴 Crítico

**H1. Cambiar la máquina de un Alquiler activo no valida contadores ni deja rastro histórico.**
- `AlquilerService.UpdateAsync` (`Eleven.Infrastructure/Services/AlquilerService.cs`) reasigna `MaquinaId`, `ContadorBNInicial` y `ContadorColorInicial` sin repetir ninguna de las validaciones que sí tiene `CreateAsync` (consistencia contra `HistoriaContador` anterior/siguiente de la máquina).
- Como `Alquiler.MaquinaId` es un campo escalar (no una relación histórica tipo "máquina X hasta fecha Y, máquina Z desde fecha Y"), cambiar la máquina de un alquiler en curso **reescribe qué máquina fue ese alquiler completo**. `AlquilerService.GetDetailsAsync` arma el historial de consumo filtrando `HistoriaContador` de la máquina **actual** del alquiler — al cambiar la máquina, el consumo registrado durante el período con la máquina anterior deja de aparecer vinculado a ese alquiler.
- Mismo patrón, mismo riesgo, en `ContratoService.UpdateAsync` (`contrato.MaquinaId = dto.MaquinaId;` sin validación).
- **Impacto de negocio:** es un mecanismo plausible de discrepancias de saldo como la reportada por el cliente en la cuenta Efectivo ($612.000) — si en algún momento se cambió la máquina de un alquiler activo desde Editar, la facturación por copia de ese tramo queda huérfana.
- **No existe hoy** una operación dedicada "Cambiar máquina" (con motivo, fecha de corte, cierre de contador de la máquina saliente) — se hace, si se hace, a través del Edit genérico.

**H2. "Avisos" (Notifications) — infraestructura completa pero nunca se dispara.**
- Existen `Notification` (entidad), `NotificationService`, `NotificationsController` y el ícono/dropdown en el sidebar — pero **ningún servicio de negocio llama a `INotificationService`** (ni Alquileres, ni Contratos, ni Incidencias, ni Pedidos, ni Insumos Críticos).
- Confirmado en producción: la tabla `Notifications` tiene **0 filas históricamente** — nunca se generó un aviso, ni uno solo, desde que existe la funcionalidad.
- El cliente no recibe ningún aviso proactivo de nada (contrato por vencer, stock crítico bajo, incidencia sin resolver, pedido a proveedor pendiente de recepción, etc.) pese a que la base ya está lista para engancharse.

### 🟡 Pendiente de sesiones anteriores (sin resolver, verificar estado con el cliente)

**H3.** 3 Contratos del sistema viejo (Id 77, 78, 79) con precio en texto libre ("precio por copia de $13", etc.) — el cliente iba a cargarlos a mano en NEW. No hay forma de verificar desde el sistema si ya se hizo; recomendable preguntar.

**H4.** Lista de repuestos (`revision_repuestos_pendientes.xlsx`, entregada) con 37 códigos sin match y 11 grupos ambiguos — sin confirmación de que el cliente ya la revisó y devolvió decisiones.

**H5.** 6 cuentas de tipo test (`admin@admin.com`, `chino@chino.com`, etc.) siguen con rol `Administrador` en producción — decisión previa del cliente fue dejarlas, pero sigue siendo superficie de riesgo si esas contraseñas son débiles/conocidas.

### 🔵 Informativo — confirmar si es esperado o no

**H6.** 255 de 310 alquileres activos (sin `FechaDevolucion`) llevan más de 2 años abiertos. Puede ser normal para este modelo de negocio (alquileres de largo plazo), pero si alguno debería estar finalizado y no lo está, también corta la cadena de contadores. Vale una pasada del cliente para confirmar cuáles siguen vigentes de verdad.

**H7.** Solo 3 `Incidencias` registradas históricamente en producción — uso muy bajo del módulo. Confirmar si el flujo real del técnico pasa directo por Pedidos Técnico (sin pasar por Incidencias) o si hay fricción de UX que hace que no se cargue.

## Alcance inicial (Discovery) — incluido / no incluido
**Incluido en este barrido:** Alquileres (alta/edición/finalización/contadores), cambio de máquina en alquiler y contrato, Notificaciones, Incidencias, verificación de pendientes previos.
**No incluido (fuera de este barrido, no revisado en profundidad):** Pedidos Proveedor/Técnico más allá del fix de tabla ya aplicado, Máquinas/Repuestos más allá de lo ya trabajado, Reportes/Informes, exportaciones Excel/PDF.

## Preguntas abiertas para el cliente
1. ¿Alguna vez se cambió la máquina de un alquiler/contrato ya activo usando "Editar"? Si sí, en qué casos — ayuda a acotar el impacto real de H1 en los datos históricos.
2. ¿Qué avisos concretos quiere recibir (H2)? Ej.: contrato por vencer, stock crítico bajo, incidencia sin resolver, pedido a proveedor pendiente — para poder alcanzar/presupuestar bien.
3. Estado real de H3 (3 contratos) y H4 (repuestos pendientes) — ¿ya resueltos por su cuenta o siguen pendientes?
4. De los 255 alquileres sin fecha de devolución hace 2+ años (H6): ¿siguen vigentes o falta finalizarlos en el sistema?

## Condición de paso a Análisis
Bloqueado hasta que el cliente confirme cuáles de H1–H7 quiere llevar adelante y responda las preguntas abiertas 1–4. H1 y H2 son los únicos que ameritan pasar a Análisis por su cuenta sin depender de más info (son gaps confirmados en el código, no dudas de dato); H3–H7 dependen de la respuesta del cliente.

## Historial de ajustes
- 2026-08-20: Barrido de Discovery inicial (primera vez que este proyecto pasa por el flujo formal de agentes pese a estar registrado como "cerrado" en el índice — se corrige el estado).
