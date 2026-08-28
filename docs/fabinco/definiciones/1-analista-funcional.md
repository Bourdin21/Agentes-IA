# Memoria - Analista funcional

## Proyecto: fabinco
## Ultima actualizacion: 2026-08-26

## Definiciones vigentes

### Contexto del lead
FABINCO - Soluciones en vestimenta laboral — Venezuela 2157, Balvanera, CABA. Rubro "Indumentaria o calzado", pero con un perfil marcadamente distinto de los leads de indumentaria minorista del historial (ej. ShowroomGriffin): es un **fabricante y distribuidor B2B con 50 años de trayectoria**, no un local de venta al publico. Sitio propio (`fabinco.com.ar`, research 2026-08-26): vende indumentaria de trabajo y EPP (calzado de seguridad, uniformes industriales, ropa de alta visibilidad) a empresas de 9 sectores (comercio, quimica, petroleo, construccion, salud, gastronomia, metalurgia, alimentos, limpieza), con cumplimiento IRAM/ISO. Maneja multiples lineas de marca (ATT, Grafa70, calzado Funcional), ofrece **servicios propios de corte y confeccion** (produccion, no solo reventa), envios a todo el pais, venta por sistema de presupuesto (no e-commerce estandar). Una sola sede fisica.

Entro por outbound frio con mensaje especifico de indumentaria (stock por talle/color, cuotas, devoluciones). Cuestionario de calificacion (3 preguntas + mensaje adicional, respuestas limpias y coherentes, sin problema de desorden):

1. ¿Que es lo mas te complica hoy?: **"Stock talle/color"**
2. ¿Con que lo manejas ahora?: **"Otro sistema"** (ya tienen algun sistema, no identificado — a diferencia de una dietetica chica, una empresa de 50 años probablemente tiene un ERP o sistema de gestion ya instalado, no una planilla).
3. ¿Cuantas personas lo van a usar?: **"3"**
Mensaje adicional (post-cierre): **"Ok."** (sin informacion adicional).

### Lectura del dolor real
El pain point declarado ("Stock talle/color") calza casi exacto con el precedente mas fuerte del historial del estudio: **ShowroomGriffin** — sistema real, entregado, en produccion, para indumentaria/calzado con variantes Color/Talle, Compras a proveedores, Ventas con pago multi-medio (PAT-003), Devoluciones y Cambios (wizard de 3 tipos), Aumento masivo de precios, Dashboard. El mensaje outbound que recibio FABINCO menciona explicitamente "cuotas" y "devoluciones y cambios" — funcionalidad que ShowroomGriffin YA tiene construida y en produccion.

**Diferencia clave de escala respecto de ShowroomGriffin y de los leads recientes (dietéticas):** FABINCO es una empresa B2B de 50 años con produccion propia y venta por presupuesto a empresas, no un comercio minorista de barrio. Esto abre dos preguntas de alcance que NO estaban en ShowroomGriffin ni en las dietéticas, a sondear explicitamente en la demo (no asumidas en el presupuesto base):
- **Gestion de presupuestos/cotizaciones a clientes empresariales** (B2B, no venta de mostrador) — podria ser un modulo relevante no cubierto por el patron ShowroomGriffin (pensado para venta minorista).
- **Trazabilidad de produccion propia** (corte y confeccion) — si fabrican parte de su catalogo, podria haber una necesidad de seguimiento de orden de produccion distinta de "Compras a proveedor" (que asume todo el stock se compra hecho).

### Modulos/features analizados (alcance base, anclado en ShowroomGriffin)
- Productos y variantes (Color/Talle) — PAT reutilizable directo de ShowroomGriffin.
- Stock por variante con alertas.
- Compras a proveedores (con o sin workflow de estados, a definir segun complejidad real de FABINCO).
- Ventas con cobro multi-medio (PAT-003) y posible financiamiento en cuotas (mencionado en el pitch outbound).
- Devoluciones y cambios (wizard, patron ya construido en ShowroomGriffin).
- Usuarios y roles (3 personas declaradas).
- Dashboard.

### Modulos/features candidatos — solo si se confirma en la demo (NO incluidos en el presupuesto base)
- Gestion de presupuestos/cotizaciones B2B (distinto de una venta de mostrador — probablemente sin cobro inmediato, con seguimiento de aprobacion del cliente empresarial).
- Trazabilidad de produccion propia (corte y confeccion) — orden de produccion, consumo de materia prima, tiempos.
- Facturacion electronica AFIP (no mencionada por el lead, pero dado que ya factura a empresas hace 50 años, casi seguro ya tiene resuelto este punto con su "otro sistema" — a confirmar, NO asumir que hace falta como en las dietéticas).

### Reglas funcionales acordadas (hipotesis, a confirmar)
- Se asume, hasta la demo, que el alcance es el nucleo de ShowroomGriffin (variantes + stock + compras + ventas + devoluciones), SIN presupuestos B2B ni trazabilidad de produccion — esos dos quedan como preguntas abiertas explicitas, no como alcance tácito.

### Criterios de aceptacion vigentes
Anclados en el precedente de ShowroomGriffin (ver `docs/ShowroomGriffin/definiciones/1-analista-funcional.md` si existe, o `4-presupuestador.md` para el detalle de modulos ya construidos) — se detallan en `2-disenador-funcional.md`.

### Supuestos y dependencias
- **[SUPUESTO — pregunta abierta central para la demo]** Que es el "otro sistema" que ya usan y por que no les resuelve el stock por variante — a diferencia de las dietéticas (donde "otro sistema" era ambiguo sobre si cubria algo), aca es mas probable que sea un ERP/sistema de gestion real ya en uso (empresa de 50 años), lo que puede implicar necesidad de migracion de datos (exclusion fija salvo acuerdo aparte) o coexistencia parcial.
- **[SUPUESTO]** No se asume necesidad de facturacion electronica AFIP en el alcance base — a diferencia de las dietéticas, FABINCO ya factura a empresas hace decadas, es altamente probable que ya tenga esto resuelto en su "otro sistema". Confirmar en la demo antes de incluirlo o excluirlo del presupuesto.
- **[SUPUESTO]** "3 personas" declaradas — sin ambiguedad de origen (a diferencia de otros leads recientes), pero no se sabe si son 3 en total en la empresa o 3 que usarian especificamente este sistema (podria ser un subconjunto del personal si la empresa tiene mas gente en otras areas, dado que factura B2B a 9 sectores).
- **Pendiente de definicion estrategica**: se consulto a `olvidata-ceo` (2026-08-26) sobre si corresponde el mismo descuento de expansion agresiva usado con las dietéticas (Tier 1, 30% + año 1 gratis) o si el perfil de esta empresa (B2B, 50 años, produccion propia) amerita cotizar mas cerca de precio de lista — resultado a incorporar en `4-presupuestador.md` antes de cerrar numeros.

### Exclusiones confirmadas (provisorias, a re-confirmar en demo)
- Migracion de datos del "otro sistema" actual (exclusion fija del estudio, salvo acuerdo aparte — mas relevante aca que en las dietéticas dado que es mas probable que tengan datos reales cargados en un sistema real).
- Aplicacion movil nativa (exclusion fija del estudio).
- Multi-sucursal (una sola sede fisica confirmada por el sitio web).
- Gestion de presupuestos B2B y trazabilidad de produccion propia — fuera del alcance BASE hasta que se confirme en la demo (ver arriba); si se confirman, son alcance adicional a re-presupuestar, no incluido en los numeros de este documento.

## Historial de ajustes
- 2026-08-26: primera version, a partir del cuestionario de calificacion outbound (respuestas limpias) + research del sitio web de FABINCO. Identificado como el precedente de dominio MAS fuerte del historial (ShowroomGriffin, codigo real en produccion) pero con una escala de negocio distinta (B2B, 50 años, produccion propia) que amerita consulta estrategica antes de fijar precio — delegado a `olvidata-ceo`, resultado pendiente de incorporar.
