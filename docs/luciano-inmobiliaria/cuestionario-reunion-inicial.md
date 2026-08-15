# Luciano Inmobiliaria — Checklist para la reunión de relevamiento

Uso interno de Joaquín/OlvidataSoft. El Análisis/Diseño/Arquitectura/Presupuesto ya cerrados en `docs/luciano-inmobiliaria/` se armaron con Joaquín respondiendo en nombre del cliente (hipótesis razonadas, no confirmadas por Luciano todavía). Esta reunión tiene dos objetivos distintos, no confundir uno con otro:

1. **Validar con el cliente real** las 6 decisiones que hoy están asumidas en `1-analista-funcional.md` §0.7 (alguna puede cambiar al hablar con ellos).
2. **Relevar el ERP actual de Luciano** — es el bloque que nadie contestó todavía, y es el que más puede mover la arquitectura (ver Sección 1, la más importante).

Marcar la opción elegida; donde no aplique ninguna, usar "Otro" y anotar a mano.

---

## 1. El ERP actual de Luciano (bloque más importante — nadie lo relevó todavía)

**1.1 — ¿Qué sistema ERP usan hoy para facturar honorarios/alquileres?**
- [ ] A) Sistema propio desarrollado a medida (interno o por un proveedor externo)
- [ ] B) Sistema de gestión inmobiliaria comercial (ej. Tokko, Prometeo, u otro) — nombre: ______________________
- [ ] C) Planillas/Excel + facturación manual en el portal de ARCA (en ese caso, "conectar la API al ERP" no aplica todavía, hay que definir qué se conecta)
- [ ] Otro: ______________________

**1.2 — ¿El ERP puede hacer llamados HTTP salientes (consumir una API REST) hoy, o hay que agregarle esa capacidad?**
- [ ] A) Sí, ya tiene integraciones con otras APIs (cuáles: ______________________)
- [ ] B) No estamos seguros — hay que preguntarle al proveedor/desarrollador del ERP
- [ ] C) No, es un sistema cerrado sin capacidad de integración — **esto cambia la arquitectura del proyecto, avisar antes de seguir**

**1.3 — ¿Quién es el referente técnico del ERP del lado de Luciano (para coordinar la integración)?**
- [ ] A) Alguien interno de Luciano — nombre/contacto: ______________________
- [ ] B) Un proveedor externo — nombre/contacto: ______________________
- [ ] C) No hay uno definido todavía

**1.4 — ¿Cómo facturan hoy (antes de tener esta API)?**
- [ ] A) Manualmente en el portal web de ARCA, comprobante por comprobante
- [ ] B) Con otro sistema/servicio de facturación que ya tienen contratado — cuál: ______________________
- [ ] C) No están facturando electrónicamente todavía

---

## 2. Certificados y puntos de venta en ARCA

**2.1 — ¿Ya tienen certificados de firma digital (`.p12`) vigentes por cada CUIT?**
- [ ] A) Sí, para todos los CUIT que van a usar
- [ ] B) Sí, para algunos — ¿cuáles faltan?: ______________________
- [ ] C) No tienen ninguno todavía — van a necesitar guía para generarlos

**2.2 — ¿Ya tienen puntos de venta habilitados en ARCA para facturación electrónica?**
- [ ] A) Sí, para todos los puntos de venta a usar
- [ ] B) Sí, para algunos — faltan: ______________________
- [ ] C) No, hay que darlos de alta

**2.3 — ¿Cuántos CUIT van a dar de alta en la suscripción, y cuántos puntos de venta por CUIT?**
- CUIT 1: ______ puntos de venta
- CUIT 2: ______ puntos de venta
- (agregar los que falten)

---

## 3. Volumen de facturación (define el control de uso y el tamaño de lote)

**3.1 — ¿Cuántos comprobantes emiten hoy, aproximadamente, por mes y por punto de venta?**
- Punto de venta ______: ______ comprobantes/mes
- (repetir por cada punto de venta)
*Este número es el que se usa como "volumen declarado" para calibrar el bloqueo por uso — ver `1-analista-funcional.md` §0.7-5.*

**3.2 — ¿Cuál es el tamaño típico de un lote cuando facturan varios comprobantes juntos?**
- [ ] A) Menos de 20 comprobantes por lote
- [ ] B) Entre 20 y 50
- [ ] C) Más de 50 — **si es así, avisar antes de cerrar Arquitectura, el diseño actual propone un tope de 50 por lote síncrono (R6, a validar)**

---

## 4. Validar las 6 decisiones ya asumidas (confirmar o corregir con el cliente real)

**4.1 — Certificado: ¿cada inmobiliaria/CUIT lo va a cargar y renovar por su cuenta desde un panel propio?**
- [ ] A) Sí, como está definido — confirma la decisión ya tomada
- [ ] B) Prefieren que Olvidata lo gestione de forma centralizada

**4.2 — Multi-CUIT: ¿todos los CUIT van bajo una sola suscripción de Luciano, cobrada por cantidad de CUIT?**
- [ ] A) Sí, como está definido
- [ ] B) Prefieren suscripciones separadas por CUIT

**4.3 — Lote: ¿les sirve que la respuesta llegue en la misma llamada (síncrono), o necesitan poder mandar lotes grandes y consultar el resultado después?**
- [ ] A) Síncrono está bien (confirma la decisión ya tomada) — validar también con la respuesta de 3.2
- [ ] B) Necesitan asíncrono (lotes grandes)

**4.4 — Autenticación: ¿la API key simple por punto de venta alcanza para su ERP, o necesitan algo más robusto (OAuth2)?**
- [ ] A) API key simple alcanza
- [ ] B) Necesitan OAuth2 — preguntar por qué (suele ser porque el ERP ya tiene un mecanismo estándar propio)

**4.5 — Anti-reventa: ¿están de acuerdo con que la API bloquee la emisión si el volumen se dispara muy por encima de lo declarado?**
- [ ] A) Sí, de acuerdo con el bloqueo duro
- [ ] B) Prefieren que solo se les avise a ellos (sin bloquear) — reabre la pregunta 5 del Análisis original

**4.6 — Modelo comercial: ¿el esquema de suscripción por packs de CUIT (Base/Estándar/Plus, ver `4-presupuestador.md`) les cierra, o esperaban otra lógica de cobro?**
- [ ] A) De acuerdo con packs por cantidad de CUIT
- [ ] B) Prefieren otra base de cobro — cuál: ______________________

---

## 5. Cláusula de uso exclusivo / no reventa (aspecto contractual, no técnico)

**5.1 — ¿Luciano tiene un abogado o asesor legal propio para revisar la cláusula de uso exclusivo, o necesitan que Olvidata proponga un modelo de cláusula?**
- [ ] A) Tienen asesor propio, la revisan ellos
- [ ] B) Necesitan que Olvidata acerque un modelo de cláusula (Joaquín debe conseguir/redactar una, no es parte del desarrollo del sistema)

---

## 6. Usuarios y cronograma

**6.1 — ¿Cuántas personas van a usar el panel de autogestión de certificados?**
- [ ] A) Una sola persona alcanza (Etapa 1, según diseño actual)
- [ ] B) Necesitan varias desde el arranque — ¿cuántas?: ______ (mueve el ítem de Etapa 2 "multi-usuario" a Etapa 1)

**6.2 — ¿Cuándo necesitan estar operativos con la API?**
- [ ] A) Sin fecha límite específica
- [ ] B) Fecha puntual: ______________________ (motivo: ______________________)

**6.3 — ¿Quién de Luciano valida/aprueba cada entrega?**
- [ ] A) Nombre/contacto: ______________________

---

*Al cerrar la reunión: volcar las respuestas en `docs/luciano-inmobiliaria/definiciones/1-analista-funcional.md`. Si 1.2 da "C" (ERP cerrado, sin capacidad de integración), o 3.2/3.1 muestran un volumen muy distinto al asumido, recalcular `3-arquitecto-mvc.md` y `4-presupuestador.md` antes de avanzar — son los dos puntos con mayor impacto en el presupuesto ya armado (USD 1.365 + suscripción).*
