# Ejemplos de uso para Contadores BMA

Los mismos ejemplos del manual de uso, escritos sobre la operación real del estudio.
Complementa a `docs/manual-de-uso.md` del producto, que es genérico. **Este archivo no va al repositorio del producto.**

Contexto relevado: el estudio trabaja con **Bejerman Web/Onvio** y **SOS Contador**; Gastón usa las dos; hay una liquidación mensual de ~108 empleados para SERVICIO TERAPIA RENAL S.A. que se entrega en formato propio; y se concilia el extracto bancario contra el mayor de SOS.

> **Encuadre importante.** Thomson Reuters prohíbe el acceso automatizado a Bejerman/Onvio, así que el sistema trabaja **sobre el archivo que el empleado ya exporta a mano** — la Opción A del análisis. No entra a Bejerman ni a SOS: trabaja con lo que sale de ahí.

---

## El mes de Gastón

**1. Conciliar el extracto contra el mayor**
Sube el resumen del Credicoop y el mayor exportado de SOS a la ficha del cliente, y le pide a *Registración* que los cruce.
→ **Para qué sirve:** le devuelve qué concilia, qué no, y las partidas pendientes con su antigüedad. Hoy eso se hace mirando dos planillas en paralelo.
→ **Límite que conviene saber:** el sistema **lee** las dos tablas y acompaña el criterio, pero **no hace el cruce por código**: los números los produce el modelo, así que se revisan. Eso es lo que falta construir para que sea una garantía y no una ayuda.

**2. Armar el IVA de un cliente**
Con los comprobantes del mes ya cargados, le pide a *Impuestos* la liquidación.
→ **Para qué sirve:** devuelve el cálculo renglón por renglón con el origen de cada número y, arriba, lo que faltó para que sea definitivo.
→ **Instructivo:** «Cómo armamos el IVA acá» se escribe **una vez**, con los pasos del estudio, y el agente lo sigue siempre igual — lo pida Gastón o cualquier otro.

**3. Ingresos Brutos con Convenio Multilateral**
→ **Para qué sirve:** liquida **de a una jurisdicción**, nunca «igual que la anterior», y señala los saldos a favor acumulados, que es plata del cliente parada que nadie mira.

**4. Sueldos de SERVICIO TERAPIA RENAL**
La conversión al formato STR ya está automatizada por el conversor y **sigue siendo un sistema aparte**: eso es código determinístico y está bien que lo sea.
→ **Para qué sirve el agente acá:** el control, no la conversión. *Liquidación de sueldos* señala a todo el que se mueva más de lo esperable contra el mes anterior, con el motivo. Con 108 empleados es el control que no se hace por falta de tiempo.

**5. Dudas de Bejerman y de SOS**
→ **Para qué sirve:** es el caso de menor riesgo de todos y el mejor candidato a arrancar. Hoy se le pregunta a un compañero o se busca en la ayuda del proveedor. Cargando los manuales como **material de referencia** del rubro, el agente responde citando de dónde lo sacó.

---

## Lo que se configura una sola vez

**Reglas de la empresa**, en modo *Siempre*:
- «Nada se presenta ni se paga sin la revisión del responsable.»
- «Ningún número sin respaldo: si falta algo para llegar al total, se informa lo que se puede sostener y se dice qué falta.»
- «Alícuotas, topes y vencimientos, siempre con su vigencia. Si el dato no está cargado, se avisa y se frena.»

→ **Para qué sirve:** se escriben una vez y valen para todas las tareas, de todas las personas, todos los meses. Es la diferencia con pedirle algo a un chat: no dependen de que quien escribe el pedido se acuerde de aclararlas.

**Instructivos**, uno por tarea repetitiva: el IVA, la conciliación, el cierre.
→ **Para qué sirve:** lo que hoy vive en la cabeza de quien lo hace queda escrito, y el agente lo sigue. Es también el mecanismo de «entrenamiento» que pidió el estudio: cada empleado documenta su tarea una vez.

**Una programación semanal** con el panorama de vencimientos de la cartera, los lunes a las 8.
→ **Para qué sirve:** que ningún vencimiento dependa de que alguien se acuerde. El lunes está en `Resultados`.

---

## Qué no hace, dicho de entrada

- **No entra a Bejerman ni a SOS Contador.** Trabaja con los archivos exportados.
- **No presenta ni paga** ante ARCA. No tiene clave fiscal.
- **No reemplaza la revisión** del responsable: lo que devuelve es un borrador de trabajo.
- **No lee imágenes ni PDF escaneados.** Un extracto fotografiado no existe para el agente.
- **No calcula por código todavía.** Los números los produce el modelo y por eso se revisan. Es lo primero que habría que construir para el estudio.
- **Las cifras fiscales no vienen cargadas** a propósito: el agente avisa y frena en vez de inventar una escala de monotributo. Cargarlas es trabajo del estudio, con su fecha de vigencia.
