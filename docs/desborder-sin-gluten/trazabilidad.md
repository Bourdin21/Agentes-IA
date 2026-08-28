# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-08-25 - orquestador (Discovery + Analisis + Diseno + Arquitectura + Presupuesto — pasada consolidada)
- Etapa: Discovery, Analisis, Diseno, Arquitectura, Presupuesto (corridas en una sola pasada por velocidad comercial, mismo criterio que audifonos-bariloche/estudio-contable-maribel-garcia/cma-centro-medico).
- Cambio: creado el proyecto `desborder-sin-gluten` (dietetica, San Carlos de Bariloche) a partir de la conversacion de calificacion outbound (3 respuestas + 1 mensaje adicional post-cierre, con el mismo problema de respuestas fuera de orden ya visto en estudio-contable-maribel-garcia). Reconstruido el pain point real (facturacion manual) y declarada la ambiguedad de "1 o 2 personas". Hecho research de mercado (WebSearch) sobre sistemas tipicos que un comercio de este perfil podria estar usando (Alegra, Xubio, POS Gestion 4.0, Genuino, Control Comercio, Natural Software, Mercadito) para dimensionar la comparacion de precio anual — sin poder confirmar cual usa DesBorder exactamente (sin reseñas de Google, negocio chico). Escaneado `docs/patrones/catalogo.yml` y `docs/*/definiciones/`: **mayor reutilizacion de codigo real confirmada del historial hasta ahora** — PAT-006 (AFIP/ARCA, marihogar, produccion real con CAE) y PAT-003 (MetodoPago, ShowroomGriffin) directamente aplicables; ademas se identifico `delicias-naturales` (cerrado 2025) como precedente de dominio casi identico (comercio de "naturales", 19 modulos, con su propia integracion AFIP en .NET Framework). Actualizado PAT-006 en el catalogo: confirmado proyecto_origen (antes "pendiente confirmar"), agregadas rutas reales de `marihogar` y `delicias-naturales`.
- Armadas DOS propuestas explicitamente NO independientes: Propuesta B (solo facturacion, USD 462) es el subconjunto exacto de items de Propuesta A (sistema integral, USD 847) que resuelve el dolor mas urgente — mismo M en los items compartidos (Usuarios, Catalogo/Productos, AFIP). Documentado el argumento de crecimiento ("software factory", B es la Etapa 1 literal de A, sin migracion destructiva) tanto en `2-disenador-funcional.md`/`3-arquitecto-mvc.md` (verificacion tecnica de que es aditivo, no rewrite) como en `presupuesto-cliente.md` (seccion dedicada). Propuesta B cae en Tier V0 de volumen (sin descuento); Propuesta A cae en Tier V1 (5% descuento) — mismo tier que cma-centro-medico. Mantenimiento: Propuesta B STARTER USD 300-425/año segun 1 o 2 usuarios; Propuesta A PRO USD 400/año sin upsell (cubre hasta 2 usuarios).
- Motivo: pedido explicito del cliente (research de sistema/precio de mercado + dos propuestas + argumento de crecimiento + respuesta escrita + presupuesto en .md).
- Impacto en capas: ninguno de codigo — solo documentacion de propuesta. Sin repo creado todavia.
- Riesgos/supuestos: discovery con respuestas fuera de orden (mismo patron de bug del bot de calificacion que estudio-contable-maribel-garcia — vale la pena reportarlo como mejora del bot en algun momento, no se toca en este proyecto). Condicion fiscal de DesBorder ante AFIP (Monotributo/RI) no confirmada — bloqueante para configurar el circuito real, se resuelve en la demo. **Gate cliente pendiente**: propuesta lista para revision de Joaquin antes de enviarse al lead real.

### 2026-08-25 - presupuestador (override de expansion agresiva Tier 1 — precio de referido)
- Etapa: Presupuesto (cambio de precio, sin cambio de alcance).
- Cambio: a pedido explicito de Joaquin ("calcular con la estrategia de expansion masiva dejando el precio a un valor de referido"), se aplico el descuento de expansion agresiva Tier 1 (30%) en ambas propuestas, pisando el calculo objetivo de R (que daba Tier 3/0% en las dos por el mismo motivo documentado en `4-presupuestador.md`: el modulo de AFIP, unico item de reutilizacion real estricta, es chico en horas relativas al resto). Mismo mecanismo de override ya usado en audifonos-bariloche (2026-08-19). Mantenimiento anual SIN cambios (la politica excluye explicitamente mantenimiento del descuento). Nuevos totales: **Propuesta B: USD 462 → USD 351** (desarrollo). **Propuesta A: USD 847 → USD 670** (desarrollo). `presupuesto-cliente.md` actualizado con la linea "Descuento por eficiencia de desarrollo" en ambas opciones.
- Motivo: pedido explicito del cliente, para maximizar probabilidad de cierre de un lead frio de ticket bajo.
- Impacto en capas: ninguno de codigo — documento de propuesta.
- Riesgos/supuestos: mismo supuesto que audifonos-bariloche — el override no se justifica recalculando R artificialmente, es una decision de negocio declarada explicitamente. Gatillo del tablero de ciclos economicos verificado: sigue en verde/amarillo (checkpoint octubre 2027, no llego).

### 2026-08-26 - orquestador (numeros finales cerrados por Joaquin, mensaje enviado al cliente)
- Etapa: Presupuesto (cierre final de numeros) + envio.
- Cambio: Joaquin redacto el mensaje final de WhatsApp con los precios definitivos — Propuesta B USD 350 (redondeado desde USD 351, descuento ajustado de -111 a -112) y Propuesta A USD 670 (sin cambios). Actualizado `4-presupuestador.md` y `presupuesto-cliente.md` con el numero final de B. Mensaje simplifica el mantenimiento a "mantenimiento anual" sin monto especifico en el chat (el detalle completo — STARTER 300-425/PRO 400 segun opcion — sigue en el documento `.md` adjunto).
- Motivo: pedido explicito del cliente, cerrar en un numero redondo para el mensaje final.
- Impacto en capas: ninguno de codigo.
- Riesgos/supuestos: mismos que la entrada anterior. Estos son los precios definitivos ya comunicados al lead — cualquier ajuste posterior requiere avisar explicitamente el cambio, no silencioso.

### 2026-08-26 - orquestador (numeros finales corregidos por Joaquin, segunda ronda)
- Etapa: Presupuesto (segundo ajuste de numeros finales, sin cambio de alcance).
- Cambio: Joaquin corrigio los numeros finales dos veces en la misma sesion — Propuesta B de USD 350 a **USD 400**, y Propuesta A de USD 670 a **USD 650**. Ambos son numeros comerciales fijados directamente (no recalculados por la formula de tiers) — mismo criterio que Ganaderia/Luciano Inmobiliaria ("numeros finales fijados por Joaquin"). Descuentos efectivos resultantes: B ~16.8% sobre subtotal distribuido, A ~32.9% (ligeramente por encima del 30% formal). `4-presupuestador.md` y `presupuesto-cliente.md` actualizados con ambos numeros y la tabla de mantenimiento con año 1 gratis.
- Motivo: pedido explicito del cliente.
- Impacto en capas: ninguno de codigo.
- Riesgos/supuestos: los numeros finales de este proyecto quedaron fijados por decision comercial directa en 3 rondas sucesivas (351→350→400 para B; 670→650 para A) — dejar claro en cualquier reenvio futuro cual es la version vigente (esta, la mas reciente) para no confundir con versiones anteriores ya descartadas.

## Historial de ajustes
- 2026-08-25: primera version.
- 2026-08-25: aplicado override Tier 1 (30%) de expansion agresiva — totales de desarrollo bajan a USD 351 (B) y USD 670 (A).
- 2026-08-26: numero final de Propuesta B ajustado a USD 350 (redondeo), mensaje enviado al cliente.
- 2026-08-26: numeros finales corregidos por Joaquin — Propuesta B a USD 400, Propuesta A a USD 650. Agregado primer año de mantenimiento gratis en ambas opciones.
