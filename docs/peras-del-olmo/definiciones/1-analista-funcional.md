# Memoria - Analista funcional

## Proyecto: peras-del-olmo
## Ultima actualizacion: 2026-08-27

## Definiciones vigentes

### Contexto del lead
Peras del Olmo — Calle 49 Nº 717, Galeria La Cumbre Loc. 27, Centro, La Plata. Rubro "Indumentaria o calzado". Entro por outbound frio con el mismo mensaje usado con FABINCO (stock por talle/color, cuotas, devoluciones) — esta vez con **confirmacion explicita de interes** ("Si, contame mas") antes de pasar al cuestionario, señal de enganche mas fuerte que otros leads recientes.

Research (WebSearch, sin sitio propio mas alla de un Linktree que no cargo — 2026-08-27): marca de diseño argentino con **local unico** pero **fuerte presencia en redes**, operando 3 lineas de producto bajo el mismo local/marca:
- Tienda principal de ropa (Instagram @perasdelolmotienda, ~27K seguidores).
- Linea de ropa para niños "Peques" (@perasdelolmopeques, ~21K seguidores).
- Jugueteria/recursos educativos (@perasdelolmojugueteria, ~18K seguidores).

Se promociona como "trabajo autogestivo" — negocio chico-mediano de diseño independiente, no una cadena ni un franquiciado, pero con volumen de ventas relevante dado el alcance en redes.

Cuestionario de calificacion (respuestas parcialmente numericas, con el mismo patron de ambiguedad ya visto en otros leads de este bot):

1. ¿Que es lo mas te complica hoy?: **"Stock talle/color"** — identico pain point a FABINCO.
2. ¿Con que lo manejas ahora?: **"2"** — respuesta numerica en vez de texto (a diferencia de FABINCO que respondio "Otro sistema" en texto). **Hipotesis de reconstruccion**: si el bot le presento las 4 opciones numeradas en el orden en que aparecen en la pregunta (1=Excel, 2=papel, 3=cuaderno, 4=otro sistema), "2" corresponderia a **papel** — no confirmado, es la lectura mas probable dado el orden literal de la pregunta, pero se declara como hipotesis, no como hecho.
3. ¿Cuantas personas lo van a usar?: **"4"** — sin ambiguedad, la cifra mas alta declarada entre los leads de indumentaria/dieteticas de esta tanda (FABINCO declaro 3).

### Lectura del dolor real
Mismo pain point exacto que FABINCO (stock por talle/color) — mismo pitch outbound, mismo precedente de dominio aplicable: **ShowroomGriffin** (codigo real en produccion, indumentaria con variantes Color/Talle, cuotas, devoluciones). A diferencia de FABINCO (B2B, 50 años, produccion propia), Peras del Olmo es **venta directa al consumidor** desde un local fisico unico, con catalogo diversificado en 3 lineas (ropa adultos, ropa niños, jugueteria) — mas parecido en perfil comercial a ShowroomGriffin mismo (venta minorista de mostrador) que a FABINCO.

### Modulos/features analizados (alcance base, anclado en ShowroomGriffin)
- Productos y variantes (Color/Talle) — aplicable de lleno a las 2 lineas de ropa (adultos y niños).
- **Nota de diseño importante**: la linea de jugueteria/educativos probablemente NO necesita variante de Talle (un juguete no tiene talle) y puede que tampoco de Color de la misma forma — el sistema debe soportar productos CON variantes (ropa) y productos SIN variantes o con variantes simples (juguetes), no forzar el mismo esquema de Color+Talle a las 3 lineas. Confirmar en la demo.
- Stock por variante/producto simple, con alertas.
- Compras a proveedores.
- Ventas con cobro multi-medio y cuotas (PAT-003).
- Devoluciones y cambios (wizard, patron ya construido en ShowroomGriffin).
- Usuarios y roles — 4 personas declaradas (mas que cualquier otro lead reciente de esta escala).
- Categorias para separar las 3 lineas de producto (Ropa Adultos / Ropa Niños / Jugueteria) dentro del mismo catalogo.
- Dashboard.

### Reglas funcionales acordadas (hipotesis, a confirmar)
- Catalogo unico con categorias que distinguen las 3 lineas, no 3 sistemas separados.
- Variantes Color/Talle solo aplican a las categorias de ropa; jugueteria/educativos se modela como producto simple (sin variante) o con variante simplificada (a definir en diseño segun lo que confirme el cliente).
- Sin facturacion electronica AFIP en el alcance base (no mencionada como pain point) — a confirmar si ya la resuelven de alguna forma.

### Criterios de aceptacion vigentes
Identicos en estructura a ShowroomGriffin/FABINCO (variante+stock+venta multi-pago+devolucion) — ver esos proyectos para el detalle, con el agregado de que el alta de producto debe permitir marcar si la categoria usa variantes o no.

### Supuestos y dependencias
- **[SUPUESTO — hipotesis de reconstruccion]** "Con que lo manejas: 2" se interpreta como **papel**, por orden literal de las opciones de la pregunta — no confirmado, mismo tipo de ambiguedad ya documentado en otros leads de este bot de calificacion (ver estudio-contable-maribel-garcia, desborder-sin-gluten).
- **[SUPUESTO]** Las 3 lineas de producto (ropa adultos, ropa niños, jugueteria) conviven en el mismo local y se gestionan con el mismo equipo de 4 personas — no confirmado si hay reparto de roles por linea de producto.
- **[SUPUESTO]** No hay necesidad de facturacion electronica AFIP en el alcance base (no mencionado, y es un local de venta directa — a diferencia de FABINCO, es mas probable que ya resuelvan esto con un sistema simple o no lo necesiten formalmente si operan como monotributista con factura C manual). A confirmar en demo antes de excluirlo definitivamente.
- Sin discovery por llamada/reunion todavia — confirmacion de interes explicita ("Si, contame mas") es una señal positiva fuerte, pero el cuestionario en si mantiene el patron de respuestas ambiguas de este bot.

### Exclusiones confirmadas (provisorias)
- Migracion de datos de cualquier sistema/planilla actual (exclusion fija del estudio).
- Aplicacion movil nativa (exclusion fija del estudio).
- Multi-sucursal (un solo local confirmado por la direccion).
- Integracion con redes sociales/Instagram para venta directa (no mencionado, fuera de alcance salvo pedido explicito).

## Historial de ajustes
- 2026-08-27: primera version, a partir del cuestionario de calificacion outbound (con confirmacion explicita de interes) + research de redes sociales (Linktree no accesible directamente, reconstruido via busqueda: 3 cuentas de Instagram con 27K/21K/18K seguidores). Mismo precedente de dominio que FABINCO (ShowroomGriffin), pero perfil de venta directa al consumidor, no B2B — pendiente de confirmacion con el lead antes de iniciar implementacion.
