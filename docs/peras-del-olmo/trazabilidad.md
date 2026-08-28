# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-08-27 - orquestador (Discovery + Analisis + Diseno + Arquitectura + Presupuesto — pasada consolidada)
- Etapa: Discovery, Analisis, Diseno, Arquitectura, Presupuesto.
- Cambio: creado el proyecto `peras-del-olmo` (Galeria La Cumbre, La Plata) a partir de la calificacion outbound — mismo pitch que FABINCO (stock talle/color), con confirmacion explicita de interes del lead ("Si, contame mas"). Respuesta a "con que lo manejas" llego como "2" (numerico) en vez de texto — reconstruido como hipotesis "papel" por orden literal de las opciones de la pregunta, declarado explicitamente como no confirmado. Research de redes sociales (Linktree no accesible, reconstruido via busqueda): marca de diseño independiente con local unico pero fuerte presencia online (3 cuentas de Instagram, 27K/21K/18K seguidores) y 3 lineas de producto (ropa adultos, ropa niños "Peques", jugueteria educativa) bajo el mismo local.
- Escaneado `docs/*/definiciones/`: mismo precedente de dominio que FABINCO (**ShowroomGriffin**, codigo real en produccion), pero perfil de venta directa al consumidor (no B2B) — mas cercano al ShowroomGriffin original. A diferencia de FABINCO, **no se consulto a `olvidata-ceo`** porque el perfil de cliente (retail chico-mediano, venta directa) es exactamente el caso que la politica de descuento por expansion agresiva esta pensada para acelerar — se aplico el Tier 1 (30%) **por calculo objetivo, sin necesidad de override** (R=81.8%). Tampoco se agrego año de mantenimiento gratis por defecto (esa promocion es solo para manejo de objecion de precio real, no aplicada aca todavia).
- Identificada una extension de diseño real no presente en ShowroomGriffin ni FABINCO: `Categoria.UsaVariantes`, para soportar que 2 de las 3 lineas de producto (ropa) usen Color/Talle y la tercera (jugueteria) no.
- Total del proyecto: **USD 878** desarrollo + mantenimiento **PREMIUM+1 usuario USD 625/año** (alternativa SCALE USD 850/año mencionada por señal de crecimiento en redes).
- Motivo: pedido implicito del cliente (pego los datos del lead sin instruccion explicita adicional, mismo patron de esta sesion donde pegar un lead nuevo implica pedir el pipeline completo).
- Impacto en capas: ninguno de codigo — documento de propuesta. Sin repo creado todavia.
- Riesgos/supuestos: hipotesis de reconstruccion de "con que lo manejas" (declarada, no confirmada). Volumen real de catalogo desconocido (3 lineas de producto + fuerte presencia en redes podria implicar mas SKUs de lo tipico). Reparto de roles entre las 4 personas no confirmado. **Gate cliente pendiente**: propuesta lista para revision de Joaquin antes de enviarse al lead real.

### 2026-08-27 - presupuestador (nueva regla de estudio: usuarios sin cargo hasta 10)
- Etapa: Presupuesto (ajuste de mantenimiento, sin cambio de alcance ni de desarrollo).
- Cambio: a pedido explicito de Joaquin ("no cobrar usuario extra hasta superar los 10 usuarios"), se actualizo `27-presupuesto-parametros.instructions.md` con la regla de estudio: los planes (STARTER/PRO/PREMIUM) ya no cobran usuario adicional al superar su tope "incluido" — el cargo por usuario adicional solo aplica desde el usuario 11 en cualquier plan. Recalculado el mantenimiento de este proyecto: de PREMIUM+1 usuario (USD 625/año) a **PREMIUM sin cargo extra (USD 500/año)**, ya que 4 usuarios < 10. `presupuesto-cliente.md` actualizado.
- Motivo: pedido explicito del cliente, aplicado como regla de estudio (no solo para este proyecto).
- Impacto en capas: ninguno de codigo.
- Riesgos/supuestos: proyectos ya cotizados con el criterio anterior (`cma-centro-medico`, `audifonos-bariloche` — este ultimo YA ENVIADO) no se tocaron retroactivamente, ver nota en `27-presupuesto-parametros.instructions.md`.

### 2026-08-27 - presupuestador (reestructurado en MVP + Full con AFIP, corregido error de mantenimiento)
- Etapa: Presupuesto (reestructuracion de alcance en dos propuestas de implementacion, mas correccion de un error propio).
- Cambio: a pedido explicito de Joaquin ("armar dos propuestas de implementacion, una que sea un mvp y otra full, con facturacion afip"), se reestructuro el presupuesto unico anterior (11 items, USD 878) en dos propuestas completas: **MVP** (Usuarios, Categorias+Clientes, Productos+Variantes, Stock, Ventas con cobro+cuotas, Puesta en marcha — USD 543) y **Full** (todo el MVP + Compras, Devoluciones, Aumento masivo, Reportes, Dashboard, y **Facturacion electronica AFIP/ARCA nueva via PAT-006** — USD 958). De paso, se corrigio un error propio: el mantenimiento de la version anterior se habia clasificado como PREMIUM razonando desde la cantidad de usuarios en vez de tablas — recontado, ambas propuestas caen dentro de PRO (6-15 tablas: MVP 9, Full 15) → **PRO USD 400/año en ambas**, no PREMIUM.
- Motivo: pedido explicito del cliente.
- Impacto en capas: ninguno de codigo — documento de propuesta.
- Riesgos/supuestos: mismos que la version anterior (hipotesis de reconstruccion "papel", volumen real de catalogo, reparto de roles). Nuevo: facturacion AFIP no fue mencionada como pain point por el lead — se agrega a la Opcion Full a pedido explicito de Joaquin, no porque el cliente la haya pedido; si en la demo dice que no la necesita, la Opcion Full pierde ese item y se reestima.

## Historial de ajustes
- 2026-08-27: primera version.
- 2026-08-27: mantenimiento recalculado bajo la nueva regla de usuarios (sin cargo hasta 10) — baja de USD 625/año a USD 500/año.
- 2026-08-27: reestructurado en Propuesta MVP (USD 543) y Propuesta Full con facturacion AFIP (USD 958), ambas con mantenimiento PRO USD 400/año (corregido de PREMIUM, error de clasificacion propio).
