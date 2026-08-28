# Memoria - Analista funcional

## Proyecto: desborder-sin-gluten
## Ultima actualizacion: 2026-08-25

## Definiciones vigentes

### Contexto del lead
DesBorder sin Gluten — dietetica (rubro "Dieteticas y venta de productos") en Ruiz Moreno 397, San Carlos de Bariloche, Rio Negro. Entro por outbound frio con mensaje especifico de rubro (no generico): pitch de control de stock/ventas en tiempo real + cierre de caja automatico, dirigido a dieteticas. Contacto registrado como "Equipo" (sin nombre de persona), telefono 5492944894981, sin email (`-`). Estado CRM: "Derivado manual Completado". Poca presencia online (sin muchas reseñas de Google) — negocio chico, probablemente de barrio/turistico dado que Bariloche es zona turistica.

Cuestionario de calificacion (3 preguntas, respuestas recibidas fuera de orden respecto de las preguntas — mismo patron ya visto en `estudio-contable-maribel-garcia`, este bot de calificacion tiene un problema recurrente de desalineacion pregunta/respuesta):

1. ¿Que es lo mas te complica hoy?: **"Facturo todo a mano"**
2. ¿Con que lo manejas ahora?: **"1"**
3. ¿Cuantas personas lo van a usar?: **"Otro sistema"**
Mensaje adicional (post-cierre del formulario): **"2"**

### Reconstruccion de las respuestas (por contenido, no por posicion)
Igual criterio que estudio-contable-maribel-garcia: las respuestas "1" y "Otro sistema" estan claramente cruzadas respecto de sus preguntas (semanticamente, "Otro sistema" responde a "¿con que lo manejas?" — es una de las opciones textuales de esa pregunta — y "1"/"2" son numeros de persona, no un metodo de gestion). Reconstruccion:
- **Pain point real**: facturacion manual ("Facturo todo a mano") — coincide con la posicion, se toma tal cual.
- **Con que lo manejan hoy**: "Otro sistema" — **usan algun sistema que NO es Excel/papel/cuaderno**, pero ese sistema no cubre (o no resuelve bien) la facturacion, que siguen haciendo a mano. Hipotesis abierta: podria ser un sistema de punto de venta/caja que no emite factura electronica AFIP, o un sistema de otro rubro (contable, gestion basica) sin modulo de venta.
- **Cuantas personas**: "1" y "2" llegaron en momentos distintos (uno en el cuestionario, el otro en el mensaje adicional post-cierre) — se interpreta como **1 o 2 personas**, sin poder confirmar cual es el numero definitivo. Mismo tratamiento de ambiguedad que estudio-contable-maribel-garcia ("1 o 2 personas").

### Research: que "otro sistema" puede estar usando (2026-08-25)
Sin reseñas de Google ni sitio propio visible — no se pudo identificar el sistema exacto. Research de mercado de sistemas tipicos para un comercio chico de este perfil (dietetica, Argentina, 2026):

| Sistema | Tipo | Precio de referencia | Cubre facturacion AFIP real |
|---|---|---:|---|
| Alegra | SaaS facturacion basica | ARS 2.599/mes (≈ USD 21/año) | Si, pero es solo facturacion — sin stock/POS |
| Xubio | SaaS facturacion/contable | Gratis (10 facturas/mes) a ARS 3.500/mes PyME (≈ USD 28/año) | Si, plan pago |
| POS Gestion 4.0 | Sistema de escritorio, alquiler mensual | ARS 16.585 a 18.985/mes (≈ USD 134-154/año) | Si, incluye stock+caja+Factura Electronica |
| Genuino, Control Comercio, Natural Software, Mercadito (GDS) | Sistemas locales para comercio/dietetica chica | Precio no confirmado publicamente | Variable, la mayoria promocionan "Factura Electronica AFIP" incluida |

**Lectura:** si el "otro sistema" que declararon es del tipo POS de escritorio (Genuino/Control Comercio/POS Gestion/Natural Software/Mercadito — los mas promocionados especificamente para dieteticas), es raro que no tenga facturacion — la contradiccion con "facturo todo a mano" sugiere que: (a) el sistema que tienen es solo para otra cosa (ej. llevar stock en una planilla dentro de un sistema contable, o un sistema de cobranza sin AFIP), o (b) tienen el sistema pero no lo usan para facturar por costo/complejidad de habilitarlo, y siguen con factura manual en talonario. Ninguna hipotesis confirmada — pregunta abierta para la demo. **Referencia de precio de mercado para dimensionar mantenimiento**: sistemas locales comparables (POS Gestion 4.0) rondan USD 130-155/año; SaaS de solo-facturacion rondan USD 20-30/año. Conversion a USD con tipo de cambio promedio ARS 1.480 (mismo criterio que `27-presupuesto-parametros.instructions.md`).

### Modulos/features analizados
- Facturacion electronica AFIP/ARCA (el pain point nombrado explicitamente — nucleo de ambas propuestas).
- Catalogo de productos (dietetica: granel y empaquetados, con %IVA por producto).
- Control de stock (para la Propuesta A integral).
- Ventas con cobro (efectivo/tarjeta/transferencia — PAT-003) integradas a la facturacion.
- Cierre de caja automatico (mencionado explicitamente en el pitch outbound original — expectativa ya generada en el lead).
- Compras a proveedor simples (para reponer stock, Propuesta A).
- Usuarios con roles (Administracion, Vendedor).

### Reglas funcionales acordadas (hipotesis, a confirmar)
- Ambas propuestas emiten comprobantes AFIP reales (Factura B/C segun condicion fiscal del cliente final — a confirmar condicion de IVA de DesBorder: Monotributo vs Responsable Inscripto, define si emite C o A/B).
- Propuesta B (solo facturacion) no lleva stock — el catalogo de productos/conceptos existe solo para facturar rapido (nombre, precio, %IVA), no para controlar existencias.
- Propuesta A (integral) descuenta stock automaticamente al facturar una venta.

### Criterios de aceptacion vigentes
- Se puede emitir una Factura electronica real (CAE) desde el sistema, para un cliente/consumidor final, con el IVA correcto.
- (Solo Propuesta A) Un producto vendido descuenta su stock automaticamente.
- (Solo Propuesta A) El cierre de caja del dia muestra el total facturado por medio de pago.

### Supuestos y dependencias
- **[SUPUESTO — pregunta abierta activa para la demo]** Que sistema usan hoy exactamente y por que no cubre la facturacion — impacta si hace falta migrar algun dato o si el nuevo sistema arranca de cero.
- **[SUPUESTO]** Condicion fiscal de DesBorder ante AFIP/ARCA (Monotributo o Responsable Inscripto) — define el tipo de comprobante (C vs A/B) y el circuito exacto de IVA. Se asume Monotributo o RI chico (comercio de barrio), a confirmar.
- **[SUPUESTO]** "1 o 2 personas" van a usar el sistema (ver reconstruccion arriba) — impacta el plan de mantenimiento.
- **[SUPUESTO]** DesBorder ya tiene o puede tramitar un certificado digital .p12 ante AFIP/ARCA para habilitar Web Services — requisito indispensable para facturar electronicamente desde un sistema propio (no es un tramite que el estudio pueda resolver por el cliente, ver "Lo que necesitamos de tu parte" en el documento cliente).
- Sin discovery por llamada/reunion todavia — igual que otros leads de calificacion outbound reciente, con el agravante de que este cuestionario en particular tiene un patron confirmado de respuestas desalineadas (ver estudio-contable-maribel-garcia).

### Exclusiones confirmadas
- Migracion de datos del "otro sistema" actual (exclusion fija del estudio, y ademas no identificado con certeza).
- Aplicacion movil nativa (exclusion fija — se accede via navegador, funciona bien en celular).
- Integracion con hardware fiscal (impresora fiscal) — un lector de codigo de barras USB funciona como teclado y no requiere desarrollo, pero una impresora fiscal dedicada esta fuera de alcance salvo pedido explicito.
- Multi-sucursal (no hay indicio de mas de una sede).

## Historial de ajustes
- 2026-08-25: primera version, a partir del cuestionario de calificacion outbound con respuestas fuera de orden (reconstruidas por contenido). Pendiente de confirmacion con el lead antes de iniciar implementacion — preguntas abiertas: que sistema usan hoy, condicion fiscal ante AFIP, y numero exacto de usuarios.
