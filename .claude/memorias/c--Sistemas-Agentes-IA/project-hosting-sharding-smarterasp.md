---
name: project-hosting-sharding-smarterasp
description: Estrategia de escalado de hosting SmarterASP.NET para los clientes tradicionales de Olvidata (Build/Rent) a medida que crece la cantidad de sistemas
metadata: 
  node_type: memory
  type: project
  originSessionId: 25a80efb-5e2e-4382-9e8c-5262b557989b
  modified: 2026-07-30T18:12:16.936Z
---

Olvidata hospeda los sistemas tradicionales de clientes (no century-21, que es SaaS multi-tenant aparte) consolidados en una o pocas cuentas Premium de SmarterASP.NET (USD 7,95/mes = USD 95,40/año), cada cliente con su propia BD MySQL dentro de la cuenta.

**El techo real no es el que dice el marketing.** SmarterASP anuncia "conexiones concurrentes ilimitadas" en el plan Premium, pero soporte confirmó (verificado en el proyecto century-21, que corre en la misma infraestructura) que el límite real es **10 conexiones simultáneas por usuario MySQL, hasta 5 usuarios MySQL creables por cuenta** → techo teórico ~50, pool seguro recomendado ~8 queries concurrentes. Esto aplica a cualquier cuenta Premium, no es específico de un proyecto.

**Regla de decisión addon vs. cuenta nueva (break-even BD):** una cuenta Premium nueva completa (USD 95,40/año) incluye 20 BD MySQL + un pool de conexiones propio y aislado. El addon de 1 BD MySQL extra cuesta USD 30/año. Break-even = 95,40 / 30 ≈ 3,18. **Si hacen falta más de 3 BD extra sobre el cupo de 20 de una cuenta, conviene abrir una cuenta nueva en vez de seguir comprando addons** — sale más barato y da aislamiento real de conexiones (evita que un cliente pesado degrade a los demás de la misma cuenta).

**Corrección 2026-07-14 (dato real de la cuenta actual, `olvidatasoft-002`): el techo que se toca primero en la práctica es RAM, no BD.** Estado real relevado: RAM 3072/3072 MB (100% usado, repartido en 3 pools de 1024 MB) vs. BD 15/20 (75%, con margen). Es decir, la cuota de RAM se agota antes que la de BD — no se puede crear ningún pool nuevo, de ningún tamaño, aunque sobren slots de BD.

**Los addons de RAM son mucho peor negocio que los de BD — nunca conviene comprarlos:** `RAM04` (+1GB) cuesta USD 240/año → USD 0,234/MB. Una cuenta Premium nueva completa da +3072 MB por USD 95,40/año → USD 0,031/MB — **~7,5x más barato por MB que el addon de RAM**, además de sumar 20 BD y un pool de conexiones propio. A diferencia de BD (donde el addon tiene sentido hasta 3 extra), en RAM no hay punto intermedio: apenas hace falta un pool nuevo, es cuenta nueva directamente.

**Configuración recomendada:**
- Tamaño objetivo por cuenta/shard: ~15-18 clientes activos (no los 20 completos del cupo nativo de BD — deja margen). Pero vigilar RAM en paralelo: la cuenta puede quedarse sin RAM antes de llegar a ese número de clientes si varios necesitan pools propios.
- Antes de gastar en RAM o abrir cuenta nueva, revisar si hay pools redundantes para consolidar gratis: en la cuenta actual hay dos pools ASP.NET 4.x de 32-bit con configuración idéntica (`olvidatasoft-002`, 6 sitios, y `olvidatasoft-002xdn`, 3 sitios) en vez de uno solo. Si no hay una razón técnica para tenerlos separados (ej. aislar un cliente inestable), fusionarlos libera 1024 MB completos (un pool entero) sin costo.
- Clientes nuevos construidos con el stack actual (.NET Core/.NET 10) deberían priorizar sumarse a una cuenta/pool con margen de RAM real, no solo margen de BD — hoy eso apunta a abrir la cuenta #2 antes de seguir sumando sitios al pool `olvidatasoft-002sjn` (.NET Core, ya 6 sitios en 1024 MB).
- Disparador para abrir el próximo shard: NO es un número fijo de clientes, es monitorear timeouts/errores de pool de conexión en logs (mismo método que ya usan en century-21) Y la cuota de RAM disponible (más restrictiva que la de BD en la práctica). Ver el checkpoint técnico análogo en `docs/century-21/definiciones/4-presupuestador.md` sección 17.
- VPS/Dedicated/Managed hosting: no evaluado en detalle (SmarterASP no expone precios de esos tiers en la página pública, requiere cotización directa). Solo tiene sentido si UN cliente puntual muestra carga pesada real (reportes/exports) que no se resuelve con más aislamiento entre cuentas — ahí conviene sacar solo ESE cliente a un plan dedicado, no migrar todo en bloque.

**Plan 2026-07-14 — NUNCA EJECUTADO (corrección 2026-07-30):** se había planeado fusionar `olvidatasoft-002` + `olvidatasoft-002xdn` (ambos ASP.NET 4.x 32-bit) en un único pool, liberando 1024 MB a 67% de uso. **El relevamiento real del 2026-07-30 confirma que la fusión nunca se aplicó (o se revirtió)**: el panel sigue mostrando 3 pools separados, cada uno en 1024 MB, **RAM de vuelta a 3072/3072 (100%, sin margen)**. Ver el detalle completo y la distribución real de sitios por pool en [[infraestructura-completa-olvidata]] — esa memoria tiene el estado vigente, esta sección queda como historial de la recomendación original (que sigue siendo válida, solo que pendiente de ejecutar).
- Tras ejecutar la fusión (todavía pendiente), monitorear 2-4 semanas: si el pool combinado (9 sitios) no muestra reciclados por memoria, se puede evaluar bajarlo por debajo de 1024 MB (mínimo 256) para liberar aún más margen — no bajarlo sin datos reales de uso.
- Las BD de MySQL no tienen concepto de "pool": cada BD es independiente y SmarterASP la reparte sola entre sus servidores backend (mysql5038, mysql8003, etc.) — no hay nada que redistribuir ahí, solo la cuota de cantidad (15/20 hoy) importa.
- **La cuota de disco de BD (7500/10000 MB, 75%) es una falsa alarma — no confundir con la de RAM.** Cada BD reserva 500 MB fijos por defecto (15×500=7500, coincide exacto con lo que muestra el panel), pero el uso real sumando el % individual de cada BD es de solo ~290 MB (~3% de los 10.000 MB de la cuenta). La cuota que realmente se agota es la de cantidad de BD (20), no la de espacio — no hace falta ninguna acción sobre el disco.

**Umbral concreto para avisar "contratar cuenta nueva" (con la distribución de arriba ya aplicada):**
- Señal BD: techo práctico 23 BD (20 nativas + 3 addons económicos). Avisar cuando la cuenta llegue a **~20-21 BD activas** (hoy 15) — no esperar a las 23, para no gestionarlo bajo presión.
- Señal RAM: la reserva liberada (1024 MB) alcanza para exactamente 1 pool más. Una vez que ese pool de reserva también se cree y llegue a su máximo sin quedar más margen, ahí sí — cuenta nueva sin alternativa (ya confirmado que los addons de RAM no convienen).
- Con el ritmo del plan (16→25 clientes 2026→2027), el umbral de BD es el que se cruza primero, probablemente durante 2027.

**Proyección de costo vs. el plan a 5 años** (`plan_ventas_olvidata.md`): con ~17 clientes/shard, el costo de hosting total pasa de USD 95,40/año (2026, 16 clientes, 1 shard) a ~USD 382/año (2030, 58 clientes, 4 shards) — contra un recurrente proyectado de USD 24.708/año en 2030. No es un problema de costo, es puramente operativo.

**Why:** evita gastar en addons más allá del punto donde una cuenta nueva ya es más barata Y más segura, y evita migrar de golpe a tiers más caros (VPS/dedicated) sin evidencia real de que el shared hosting se haya quedado corto.

**⚠️ CORRECCIÓN 2026-07-30 — el precio de USD 95,40/año usado en TODA esta memoria es el precio de lista, no el real.** Joaquín confirmó la factura real de abril 2026: **USD 120/año** por el plan Premium (+ USD 24/año de backup diario aparte). Esto corre el break-even de BD de 3 a **4** (120/30=4,0) y el ratio del addon de RAM de 7,5x a **6,0x** peor por MB — las conclusiones cualitativas no cambian (addon de RAM nunca conviene, BD hasta cierto punto sí), solo los números exactos. Además, SmarterASP ofrece **13% off a 2 años / 30% off a 3 años** de compromiso — contratar cuentas nuevas a 3 años bajaría el costo efectivo a USD 84/año c/u. Detalle completo de esta corrección y de la comparación de precio/MB contra los demás tiers de SmarterASP (Semi Basic/Advance/Premium/Ultimate) en [[infraestructura-completa-olvidata]] — esa es ahora la fuente de precios vigente, no recalcular desde el 95,40 de acá.

**How to apply:** cuando se hable de escalar infraestructura, agregar clientes nuevos a una cuenta que ya tiene varios sistemas, o evaluar costos de hosting en el plan financiero, usar la regla de break-even de BD (ahora 4, no 3, ver corrección arriba) y el tamaño objetivo de shard (~15-18) en vez de recalcular desde cero. Ver también [[project-agentes-ia]] para el contexto del stack .NET/MySQL usado en todos los proyectos, y [[infraestructura-completa-olvidata]] para el inventario completo (sitios, SSL, dominios, servidor DonWeb aparte, precio real y descuentos multi-año) relevado el 2026-07-30 — esta memoria se enfoca solo en la regla de escalado de la cuenta SmarterASP, la otra tiene el detalle completo y los precios corregidos.
