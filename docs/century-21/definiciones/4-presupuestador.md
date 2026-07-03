# Memoria - Presupuestador

## Proyecto: century-21
## Ultima actualizacion: 2026-07-02

## 1. Introducción y contexto

Cliente piloto: Century 21 La Plata. Objetivo: construir una plataforma SaaS multi-agencia (CRM + Chatbot WhatsApp + Agregador de portales inmobiliarios), pensada desde el diseño para revenderse a otras agencias inmobiliarias. Base: `1-analista-funcional.md`, `2-disenador-funcional.md` y `3-arquitecto-mvc.md` (los tres cerrados y vigentes al 2026-07-02).

**Tasa vigente:** USD 35/hora, formula `Costo módulo = M × $16.80` (M/2.5 × 1.20 × $35), según `27-presupuesto-parametros.instructions.md`.
**Política de contingencia:** variable por riesgo (8% / 15% / 25%), aplicada una sola vez por ítem.
**Tokens IA:** USD 100 fijos, ítem individual visible en la tabla cliente (no prorrateado).

## 2. Alcance funcional presupuestado

**Actualizado 2026-07-02 — cambio de modelo de roles:** se elimina el rol Gerente. El sistema pasa a 2 roles: `SuperAdmin` (Olvidata — gestiona Agencias, Grupos, Asesores, Planes, WhatsApp) y `Asesor` (único rol de negocio — peer-to-peer dentro de su grupo, bandeja compartida con self-assign, perfil propio + perfil de grupo). El plan se contrata por **Grupo**, no por Agencia. Ver `2-disenador-funcional.md` y `3-arquitecto-mvc.md` para el detalle. Reestimación completa de este archivo por gatillo de cambio de reglas de negocio y permisos.

**Etapa 1 (MVP operable):** plataforma multi-agencia completa (SuperAdmin gestionando Agencias, Grupos, Asesores, Planes, WhatsApp) + CRM y Chatbot WhatsApp completo (Clientes, Consultas con bandeja compartida, Bot, Alertas, perfiles propio/de grupo). Es lo mínimo para dar de alta la primera agencia/grupo (Century 21 La Plata) y operar.

**Etapa 2 (resto del alcance):** Agregador de portales (scraping global MercadoLibre + Apify ZonaProp/ArgenProp), Catálogo propio CRUD, Búsqueda unificada. Sin cambios por el nuevo modelo de roles.

## 3. Especificaciones técnicas del servicio

| Ítem | Detalle |
|---|---|
| Tecnología | ASP.NET Core MVC .NET 10, EF Core 10, MySQL 8, ASP.NET Core Identity |
| Hosting contratado | SmarterASP.NET, plan **PREMIUM** (~USD 7.95/mes): 20 BD MySQL / 10 GB, conexiones concurrentes "ilimitadas" (a confirmar límite real con soporte), Schedule Tasks/Cron Jobs habilitado |
| Despliegue | IIS compartido (Windows hosting), Hangfire para jobs programados |
| Integraciones externas | Meta WhatsApp Cloud API (por agencia), MercadoLibre REST API (directa), Apify REST API (ZonaProp + ArgenProp) |
| Requisitos de entorno del cliente | Cuenta Meta Business verificada + número WhatsApp Business por cada agencia dada de alta |

## 4. Roles y usuarios del sistema (documentación cliente)

| Rol | Alcance |
|---|---|
| Asesor | Único rol de negocio. Opera dentro de su grupo: bandeja compartida de consultas (self-assign y reasignación entre compañeros, sin jerarquía), perfil propio con estadísticas personales, perfil de grupo con estadísticas del equipo, clientes, catálogo propio, búsqueda del agregador |

> El rol `SuperAdmin` (gestión de agencias, grupos, asesores y planes a nivel plataforma) es de uso interno del proveedor y no se documenta en el material entregado al cliente final. **Ya no existe el rol Gerente** (eliminado 2026-07-02) — la gestión de usuarios que antes hacía el Gerente ahora la hace `SuperAdmin` como parte del servicio (alta de asesores, configuración de WhatsApp), y la operación diaria (reasignar consultas, editar catálogo/clientes) es peer-to-peer entre todos los asesores del grupo.

## 5. PASO 0 — Anclaje histórico

Referencias seleccionadas: **decorhogar** (76h M / 10 módulos, bot WhatsApp + catálogo con fotos, misma era de tasa/formula), **Energy Nutrition** (integraciones batch/webhook, sin cierre real — solo método y rangos), **ShowroomGriffin** (86.57h base / 11 módulos, infra transversal), **labipac** (integración parcial API, cierre real reciente).

## 6. WBS con PERT completo

### Etapa 1 — MVP operable (reestimado 2026-07-02 por cambio de modelo de roles)

| # | Módulo | Tipo | Ref. histórica (base) | O | M | P | PERT | Riesgo | Cont. | Hrs fin. | Hrs fact. | USD |
|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| M1 | Plataforma SuperAdmin (Agencias, Planes, métricas) | ABM intermedio + reporte | decorhogar Usuarios/roles (5.5h) + proxy métricas | 4.5 | **6.5** | 9.5 | 6.67 | Medio | 15% | 7.67 | 3.12 | $109 |
| M2 | Gestión de Grupos y Asesores (SuperAdmin — absorbe alta de asesores + config. WhatsApp, antes en Gerente) | ABM intermedio ×2 + regla de cupo por grupo | decorhogar/ganadería Usuarios (5.5h) + antiguo M8 (1.5h) | 4.5 | **6.5** | 9.5 | 6.67 | Medio | 15% | 7.67 | 3.12 | $109 |
| M3 | Tenancy transversal (query filter por GrupoId, ITenantContext, migraciones, seed roles, **concurrencia optimista RowVersion**) | Infra transversal — sin precedente en el estudio | ShowroomGriffin infra (3h/6 migr.) + complejidad nueva + concurrencia | 3.5 | **5.5** | 8.5 | 5.67 | Alto | 25% | 7.09 | 2.64 | $92 |
| M4 | Clientes y Preferencias (perfil, fechas clave) | ABM intermedio | Dataset genérico ABM intermedio (3.1–5.4h) | 3.5 | **5.0** | 7.5 | 5.17 | Bajo | 8% | 5.58 | 2.40 | $84 |
| M5 | Consultas (bandeja compartida, self-assign, reasignación peer-to-peer) | Workflow con estados + concurrencia | decorhogar CRM Leads (7.7h, 6 estados) | 6.0 | **8.0** | 11.5 | 8.25 | Medio | 15% | 9.49 | 3.84 | $134 |
| M6 | Bot WhatsApp entrante (webhook Meta, flujo de menú, resolución **directa de Grupo** por número) | Integración webhook | decorhogar Bot WhatsApp (M=7h) / EN Sync webhook (8.3h) | 5.0 | **6.5** | 9.5 | 6.75 | Alto | 25% | 8.44 | 3.12 | $109 |
| M7 | Alertas de fechas clave (job diario + plantillas Meta, itera grupos) | Job programado + integración menor | ShowroomGriffin Resumen Semanal (M=2h) | 1.5 | **2.0** | 3.0 | 2.08 | Medio | 15% | 2.39 | 0.96 | $34 |
| M12 | Mi perfil — estadísticas personales del asesor | Reporte simple | Sin precedente exacto — proxy ajuste con widgets (~2h) | 1.5 | **2.0** | 3.0 | 2.08 | Bajo | 8% | 2.25 | 0.96 | $34 |
| M13 | Perfil de grupo — estadísticas agregadas del equipo | Reporte con agregación | ShowroomGriffin Dashboard (M=2h) + agregación multi-usuario | 2.0 | **2.5** | 3.5 | 2.58 | Bajo | 8% | 2.79 | 1.20 | $42 |
| **Subtotal E1** | | | | | **44.5** | | **45.92** | | | **53.37** | **21.36** | **$747** |

> Se elimina M8 (Configuración WhatsApp por agencia) como línea independiente — su alcance se absorbió en M2 (ahora la configura SuperAdmin junto con el alta del grupo). Se agregan M12 y M13, pantallas nuevas pedidas explícitamente por el cliente (perfil propio y perfil de grupo).

### Etapa 2 — Agregador y catálogo

| # | Módulo | Tipo | Ref. histórica (base) | O | M | P | PERT | Riesgo | Cont. | Hrs fin. | Hrs fact. | USD |
|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| M9 | Agregador de portales (MercadoLibre directo + Apify ZonaProp/ArgenProp + orquestador + cache global + job + botón forzar) | Integración batch múltiple | EN Catálogo TN+ML batch (16.7h) | 10.0 | **13.0** | 18.0 | 13.33 | Alto | 25% | 16.66 | 6.24 | $218 |
| M10 | Catálogo propio CRUD (cabecera + fotos) | ABM complejo con galería | decorhogar Catálogo+fotos (M=7h) | 5.0 | **7.0** | 9.5 | 7.08 | Medio | 15% | 8.14 | 3.36 | $118 |
| M11 | Búsqueda unificada (filtros multi-fuente, tag de origen, aplicar preferencias) | Reporte/consulta compleja | Sin precedente exacto — proxy reporte complejo (~4h) | 3.0 | **4.5** | 7.0 | 4.67 | Medio | 15% | 5.37 | 2.16 | $76 |
| **Subtotal E2** | | | | | **24.5** | | **25.08** | | | **30.17** | **11.76** | **$412** |

### Totales

| | M | PERT base | Hrs finales | Hrs facturables | USD |
|---|---:|---:|---:|---:|---:|
| Etapa 1 | 44.5h | 45.92h | 53.37h | 21.36h | $747 |
| Etapa 2 | 24.5h | 25.08h | 30.17h | 11.76h | $412 |
| **Total (desarrollo completo, uso interno)** | **69.0h** | **71.00h** | **83.54h** | **33.12h** | **$1.159** |
| Tokens IA (ítem individual) | | | | | $100 |
| **Total interno (Olvidata)** | | | | | **$1.259** |

> Este es el costo de desarrollo **completo** (incluye M1+M2, la plataforma SuperAdmin/gestión de grupos que Century21 no ve ni usa). El monto que se factura a Century 21 La Plata excluye M1+M2 — ver sección 14 y `presupuesto-cliente.md`.

## 7. Autocorrección por ítem (PASO 7)

| # | Ratio (M / ref.) | Decisión | Motivo |
|---|---:|---|---|
| M1 | 1.08 ✅ | Mantener | En banda; suma proxy de métricas al ABM base |
| M2 | 0.93 ✅ | Mantener | 6.5h vs referencia combinada 7h (5.5+1.5) — leve sinergia por construirse en la misma pantalla |
| M3 | 1.06 ✅ | Mantener | Sin precedente exacto — riesgo Alto declarado aparte cubre la incertidumbre; +1h por concurrencia optimista |
| M4 | 1.11 ✅ | Mantener | En banda del dataset genérico |
| M5 | 1.04 ✅ | Mantener | +0.5h vs versión anterior por patrón de bandeja compartida; sigue en banda de decorhogar CRM Leads |
| M6 | 0.93 ✅ | Mantener | −0.5h vs versión anterior — resolución directa de Grupo por número es más simple que la ambigüedad agencia→grupo previa |
| M7 | 1.00 ✅ | Mantener | Coincide con referencia directa |
| M9 | 0.80 ⚠️ justificado | Mantener | Apify absorbe Cloudflare/proxies — menor esfuerzo propio que integrar TN+ML directo (caso EN) |
| M10 | 1.00 ✅ | Mantener | Coincide con referencia directa (mismo driver: galería multi-foto) |
| M11 | 1.13 ✅ | Mantener | Sin precedente exacto, dentro de banda de tolerancia |
| M12 | 1.00 ✅ | Mantener | Pantalla nueva, sin precedente exacto — proxy ajuste con widgets |
| M13 | 1.03 ✅ | Mantener | Pantalla nueva, proxy Dashboard + agregación multi-usuario |

## 8. Sanity check del total (PASO 8)

| Comparable | Módulos | Hrs M | Ratio vs century-21 |
|---|---:|---:|---:|
| decorhogar (bot WhatsApp + catálogo con fotos, sin AFIP) | 10 | 76h | 0.91 ✅ |
| ShowroomGriffin (multi-rol, sin integraciones externas) | 11 | 86.57h | 0.80 — justificado: century-21 no tiene módulo financiero pesado tipo "Ventas" |
| Energy Nutrition (4 integraciones externas) | 18 | 117.3h | avg 5.3h/módulo vs 6.5h/módulo EN — coherente (century-21 tiene 13 módulos ahora, más chicos en promedio) |

**Conclusión:** total 69.0h M (13 módulos) coherente con el dataset tras la reestimación por cambio de roles. Sin ajuste adicional.

## 9. Cierre numérico (PASO 9)

- **Paso A (preliminar):** $1.159 desarrollo + $100 tokens IA = **$1.259** (costo interno completo, esfuerzo de construir la plataforma una sola vez)
- **Paso B (ajustado):** sin cambios — autocorrección no generó ajustes. **Total final interno: $1.259**
- **Modelo de facturación al cliente (actualizado 2026-07-02):** se abandona la facturación por proyecto BUILD ($1.041 por etapas). El desarrollo se financia con la suscripción de los propios grupos de asesores (Básico/Pro/Enterprise — ver sección 17 y `presupuesto-cliente.md`), incluyendo el grupo de Century 21 La Plata como uno de esos suscriptores. Ver sección 14 para el detalle de cobertura.

## 10. Pruebas mínimas requeridas

- Aislamiento de tenant: un usuario del Grupo A nunca ve datos del Grupo B (positivo y negativo, para cada entidad tenant-scoped).
- Máquina de estados de Consulta: las 5 transiciones válidas + intentos de transición inválida.
- **Concurrencia en self-assign:** dos asesores del mismo grupo intentan tomar la misma consulta libre al mismo tiempo — solo uno debe lograrlo, el otro recibe error funcional claro.
- **Reasignación peer-to-peer:** cualquier asesor del grupo puede reasignar una consulta a un compañero; un asesor de otro grupo no puede.
- Alta de asesor bloqueada al alcanzar el límite del plan **del grupo**.
- Webhook de WhatsApp: mensaje entrante resuelve el grupo correcto por número de destino.
- Scraping global: job diario y botón "Actualizar ahora" actualizan el mismo cache para todos los grupos.
- Carga de fotos de catálogo propio: tipo/tamaño válido e inválido.

## 11. Checklist de salida

```
[✓] Estimación por módulo funcional (11 módulos, no por capa técnica)
[✓] PERT (O, M, P) por módulo con anclaje histórico (PASO 0)
[✓] Contingencia variable por riesgo aplicada UNA SOLA VEZ
[✓] Autocorrección por ítem (PASO 7) — 1 ratio justificado (M9), resto en banda
[✓] Sanity check del total contra 3 proyectos comparables (PASO 8)
[✓] Cierre por dos pasos (A = B, sin ajuste)
[✓] Tokens IA como ítem individual visible (no prorrateado)
[✓] Tabla simple E1/E2 para cliente
[✓] Plan de mantenimiento por cantidad de tablas
[✓] Condiciones comerciales sin cláusula de validez de oferta
```

## 12. Riesgos y supuestos del presupuesto

| # | Tipo | Descripción | Impacto si se materializa |
|---|---|---|---|
| RP1 | Riesgo | Límite real de conexiones MySQL del hosting compartido no confirmado | Puede requerir upgrade de hosting antes de lo previsto — no afecta el desarrollo de Etapa 1/2, sí el techo comercial del plan Enterprise |
| RP2 | Riesgo | M3 (tenancy transversal) es el primer módulo multi-tenant del estudio, sin cierre real de referencia | Contingencia Alta (25%) ya la cubre; gatillo de reestimación si aparecen requisitos de aislamiento adicionales |
| RP3 | Riesgo | Verificación Meta Business de Century 21 La Plata puede demorar 1-3 semanas | No afecta horas de desarrollo, sí la fecha de arranque de M6/M7 en producción |
| RP4 | Riesgo | Modelo peer-to-peer sin Gerente: gestión compartida de catálogo/clientes sin dueño único es una hipótesis de Diseño, no confirmada explícitamente por el cliente | Si el cliente pide restringir edición al creador original, es cambio de reglas de negocio (gatillo de reestimación) |
| SP1 | Supuesto | Hosting SmarterASP.NET Premium ya contratado por el cliente | — |
| SP2 | Supuesto | Apify (ZonaProp/ArgenProp) y MercadoLibre API sin costo de desarrollo adicional a lo presupuestado en M9 | — |
| SP3 | Supuesto | Asesor pertenece a un único grupo (confirmado en Diseño) | Si cambia, M2 requiere reestimación (+tabla intermedia) |
| SP4 | Supuesto | El plan se contrata por Grupo, no por Agencia (confirmado por el cliente 2026-07-02) | Ya reflejado en M2/M3 y en el modelo de datos |

## 13. Exclusiones (no incluidas en el precio)

- Migración de datos desde sistema anterior de Century 21 La Plata.
- Configuración y costo del servidor/hosting (ya contratado por el cliente).
- Facturación electrónica AFIP/ARCA.
- Aplicación móvil.
- Self-service de alta de agencia y cobro automático (onboarding es manual/asistido en esta fase).
- Bot conversacional con IA/LLM (roadmap futuro documentado en Análisis, fuera de este presupuesto).
- Costo variable de conversaciones WhatsApp ante Meta y de Apify (costos operativos, no de desarrollo — ver sección 14).

## 14. Documento simple — desglose interno completo (uso Olvidata, no es lo que se factura)

| Área funcional | Quién la usa | USD |
|---|---|---:|
| **Etapa 1 — MVP operable** | | |
| Plataforma SuperAdmin (Agencias, Planes, métricas) | Solo Olvidata | $109 |
| Gestión de Grupos y Asesores + config. WhatsApp | Solo Olvidata (SuperAdmin) | $109 |
| Seguridad y control de accesos (infraestructura tenant) | Todos los grupos (valor indirecto) | $92 |
| Clientes y preferencias | Todos los grupos | $84 |
| Consultas — seguimiento comercial (bandeja compartida) | Todos los grupos | $134 |
| Chatbot WhatsApp entrante | Todos los grupos | $109 |
| Alertas automáticas de fechas clave | Todos los grupos | $34 |
| Mi perfil (estadísticas personales) | Todos los grupos | $34 |
| Perfil de grupo (estadísticas del equipo) | Todos los grupos | $42 |
| Tokens IA (desarrollo asistido) | — | $100 |
| **Subtotal Etapa 1 (interno completo)** | | **$847** |
| **Etapa 2 — Agregador y catálogo** | | |
| Agregador de portales (MercadoLibre, ZonaProp, ArgenProp) | Todos los grupos | $218 |
| Catálogo propio de propiedades | Todos los grupos | $118 |
| Búsqueda unificada | Todos los grupos | $76 |
| **Subtotal Etapa 2** | | **$412** |
| **TOTAL INTERNO (desarrollo completo, una sola vez)** | | **$1.259** |

> **Ya no se factura por proyecto/etapas.** Este es el costo de construir la plataforma UNA sola vez; se recupera con las suscripciones de los grupos de asesores (Básico/Pro/Enterprise), no con una factura de desarrollo dirigida a Century21. El documento que se entrega a cualquier grupo (incluido el de Century21) es `docs/century-21/presupuesto-cliente.md` — una hoja de precios de suscripción (configuración inicial + plan anual por tier), sin mencionar SuperAdmin ni el esquema multiusuario. Ver sección 17 para el detalle de cuántos grupos hacen falta para cubrir este total.

## 15. Plan de mantenimiento anual recomendado

~17 tablas (8 de negocio + AuditLog/Notification + ~7 de Identity) → **Plan PREMIUM (16-30 tablas) — USD 400/año** (confirmado por el cliente, sin cambios en el monto). Incluye hasta 3 usuarios de soporte, soporte prioritario. Cubre hosting/seguridad/soporte, no cambios funcionales nuevos.

**Ajuste 2026-07-02:** se quitan las "2 rondas de ajuste al año" del alcance del plan de mantenimiento — decisión explícita del cliente: la gestión del sistema (alta de usuarios, grupos, configuración, cualquier cambio operativo) es pura y exclusivamente de Olvidata, no hay nada que el cliente autoadministre y necesite "ajustar" por su cuenta. Cualquier pedido puntual se atiende como soporte estándar dentro del plan, no como un beneficio contado aparte. El precio del plan (USD 400/año) se mantiene sin cambios pese a la reducción de alcance del beneficio — decisión comercial explícita del cliente, no un ajuste de costo.

## 16. Condiciones comerciales

- 50% al inicio / 50% a la entrega de cada etapa.
- Sin cláusula de validez de oferta (regla vigente 2026).
- Moneda: USD (o equivalente ARS al tipo de cambio del día de facturación).

---

## 17. Plan de venta SaaS — Básico / Pro / Enterprise (reventa multi-agencia)

Pedido explícito del cliente: usar este presupuesto como base para armar planes de suscripción de reventa a otras agencias, considerando las limitaciones del hosting contratado.

**Actualización 2026-07-02 — unidad de venta pasa de Agencia a Grupo:** tras eliminar el rol Gerente, el plan (Básico/Pro/Enterprise) se contrata por **Grupo**, no por Agencia. Esto es una buena noticia para el negocio de reventa: una inmobiliaria con varias sucursales ya no es "un cliente, un plan" — es **un plan por sucursal/grupo**, multiplicando los ingresos posibles por cliente franquicia sin cambiar el precio de lista. Los montos de cada plan (USD 49/129/299) no cambian, solo la unidad que los contrata.

### Estructura de costos operativos (no de desarrollo — recurrentes, compartidos entre todas las agencias)
| Costo | USD/mes | Escala con cantidad de agencias |
|---|---:|---|
| Hosting SmarterASP.NET Premium | $7.95 | No escala (cache/BD compartida — ver Análisis/Arquitectura) |
| Apify (ZonaProp + ArgenProp) | ~$10-15 | No escala por agencia (scraping global, una sola vez para toda la plataforma) |
| WhatsApp Cloud API (Meta) | Variable | Escala **por agencia**, cada una paga su propio consumo de conversaciones — no es costo de Olvidata |
| **Costo fijo compartido de Olvidata** | **~$18-23/mes** | Prácticamente constante hasta el techo de capacidad del hosting |

El punto clave de la arquitectura elegida (tenant compartido + cache global) es que el costo marginal de sumar una agencia nueva es bajo: no hay BD nueva, no hay scraping adicional, solo el consumo propio de WhatsApp de esa agencia (que paga la agencia, no Olvidata) y el tiempo de onboarding manual.

### Planes propuestos — revisión v3 2026-07-02, vuelta a curva de precio por volumen (descendente)

**Corrección de rumbo pedida por el cliente:** la v2 (Pro $199, Enterprise $30/asesor plano) había subido el precio por asesor a medida que crecía el plan. El cliente aclaró que la intención real es la opuesta — **el servicio es el mismo en todos los planes, y a mayor cantidad de usuarios el precio por usuario debe bajar** (volumen = descuento, no premium). Se rediseña partiendo de la base explícita del cliente: **Básico = USD 60/mes para 3 asesores**.

| Plan | Límite de asesores | Precio mensual | USD/asesor al tope | Setup inicial |
|---|---|---:|---:|---:|
| **Básico** | Hasta 3 | USD 60/mes | USD 20,00 | USD 150 (único pago) |
| **Pro** | Hasta 10 | USD 150/mes | USD 15,00 | USD 200 (único pago) |
| **Enterprise** | 11+ | USD 150/mes + USD 10/mes por asesor extra sobre 10 (ej. 11 asesores = USD 160/mes; 20 = USD 250/mes) | USD 14,55 en 11, bajando hacia ~USD 10 asintóticamente | USD 300 (único pago) |

**Método:** se modela como precio base + costo marginal decreciente por asesor adicional, no como tarifa plana por asesor — evita el "salto" en el límite entre planes (el primer asesor de Enterprise nunca puede costar menos en total que el último de Pro). Curva de promedio por asesor: **$20,00 → $15,00 → $14,55 y bajando**, siempre descendente, tal como pidió el cliente.

**Comparación contra Tokko Broker** (ver "Investigación de mercado" más abajo): Tokko publica USD 69/mes (Duo, ~2 usuarios), USD 110/mes (Empresa) y USD 147/mes (Empresa superior, probablemente 6-10 usuarios). Con esta v3, Básico (USD 60/mes, 3 asesores) sigue por debajo de la entrada de Tokko (USD 69/mes por solo 2). Pro (USD 150/mes, 10 asesores) queda prácticamente empatado con el techo público de Tokko (USD 147/mes) — pero cubriendo más asesores (10 vs. probablemente 6-10) y con WhatsApp bot + agregador incluidos, que Tokko no confirma al mismo nivel. Mejora respecto a la v2: ya no hay ningún escalón por encima del techo de mercado conocido.

**Racional del costo fijo compartido:** con solo 1 grupo en plan Básico ($60/mes) ya se cubre el costo fijo compartido de infraestructura ($18-23/mes) con margen. El setup inicial cubre el tiempo real de onboarding asistido (alta de tenant + acompañamiento de verificación Meta Business, 1-3 semanas de proceso externo).

### Planes propuestos — revisión v4 2026-07-02, captura de margen frente al precio oficial de Tokko

Con el precio real de Tokko Broker confirmado (ver "Cuarta consulta" en Investigación de mercado), quedó demostrado que la v3 dejaba 33-54% de margen sobre la mesa frente al líder del mercado. Se rearman los planes para capturar parte de ese margen, **sin perder la ventaja de precio** ni la lógica de volumen = más barato por asesor que pidió el cliente.

**Método:** costo marginal decreciente por asesor adicional (igual que v3), recalibrado para que Pro y Enterprise queden consistentemente ~25-30% por debajo de Tokko en el mismo tramo de usuarios — Básico se mantiene como gancho de entrada muy agresivo, sin necesidad de acercarlo a Tokko.

| Plan | Límite de asesores | Precio mensual (referencia interna) | USD/asesor/mes al tope | Tramo Tokko equivalente | Diferencia vs Tokko |
|---|---|---:|---:|---|---|
| **Básico** | Hasta 3 | USD 60/mes *(sin cambio)* | USD 20,00 | Inicial (2 usuarios) $90,40/mes | 33,6% más barato, con 1 asesor extra |
| **Pro** | Hasta 10 | USD 185/mes *(antes $150 en v3)* | USD 18,50 | Profesional (10 usuarios) $249,64/mes | 25,9% más barato |
| **Enterprise** | 11+ | USD 185/mes + USD 15/mes por asesor extra sobre 10 *(corregido 2026-07-02 — antes $25/mes, rompía la curva decreciente)* | USD 18,18 en 11, bajando hacia ~USD 16-17 en 15-20 | Corporativo (15 usuarios) $433,45/mes → century-21 a 15 usuarios = $260/mes | 40,0% más barato |

**Construcción del cálculo (marginal decreciente):** Básico = $60 fijo (3 asesores, $20/asesor). Pro = $60 + $18/asesor por los 7 asesores adicionales (4 a 10) = $60 + $126 = **$186/mes** (redondeado a $185). Enterprise = $185 + $15/asesor por cada asesor desde el 11 en adelante — ej. 15 asesores = $185 + 5×$15 = **$260/mes**.

**Corrección 2026-07-02 (error detectado por el cliente):** la versión anterior de Enterprise usaba marginal $25/asesor, que es MAYOR al promedio de Pro ($18,50/asesor) — eso hacía que el USD/asesor de Enterprise **subiera** en vez de bajar a medida que se agregaban asesores (rompía la promesa central de "a mayor volumen, más barato por asesor"). Se corrige el marginal a $15/asesor (menor al promedio de Pro), lo que restaura una curva estrictamente decreciente: **$20,00 → $18,50 → $18,18 (en 11) → bajando progresivamente** con cada asesor adicional.

**Por qué queda ~26-40% por debajo de Tokko y no más:** deja un colchón de precio claro y fácil de argumentar en una venta ("más barato que Tokko, con más funciones incluidas") sin llegar a paridad de precio. Es una decisión de posicionamiento, no un techo técnico — hay margen documentado para subir más si el cliente lo decide más adelante.

**Ajuste 2026-07-02 — se elimina el pago inicial de configuración (setup) y la facturación mensual:** decisión explícita del cliente. Los tres planes se cobran **exclusivamente en modalidad anual**, sin fee de alta separado y sin opción de pago mensual. La puesta en marcha/onboarding queda bundleada dentro del precio del plan. La columna "Precio mensual" de esta tabla es solo referencia de cálculo interno (base para construir el precio anual), no una opción de facturación real.

### Política de cobro — anual exclusivo (decisión 2026-07-02, confirmada por el cliente)

Objetivo explícito: que el costo de desarrollo (USD 1.259, ver sección 9 — actualizado tras la reestimación por cambio de modelo de roles) quede cubierto **de entrada** por los primeros clientes SaaS, no diluido en 20+ meses de recurrente. Confirmado 2026-07-02: la unidad de cobertura son **3 grupos** (no agencias — ver "unidad de venta pasa de Agencia a Grupo" más arriba).

Mecanismo: **facturación exclusivamente anual**, calculada como 10 meses del precio mensual de referencia interna (equivale a 2 meses de descuento vs. cobrar mes a mes, aunque esa opción mensual ya no se ofrece al cliente). Sin fee de setup/configuración inicial.

| Plan | Precio mensual (referencia interna, no ofrecido) | Anual (único modo de facturación) |
|---|---:|---:|
| Básico | $60/mes | **$600/año** |
| Pro | $185/mes | **$1.850/año** |
| Enterprise | $185/mes + $15/mes por asesor extra sobre 10 | **$1.850/año** + $150/año por asesor extra sobre 10 (ej. 11 asesores = $2.000/año, 15 asesores = $2.600/año) |

**No se ofrece facturación mensual** (eliminada 2026-07-02 a pedido del cliente) — la anual es la única modalidad de cobro disponible.

**Cobertura del costo de desarrollo con 3 grupos en Plan Básico (caso pedido por el cliente) — recalculado sin setup:**

| Concepto | Cálculo | USD |
|---|---|---:|
| Prepago anual (3 × $600) | cobrado al firmar | $1.800 |
| Costo de desarrollo a cubrir | (sección 9) | $1.259 |
| **Excedente sobre el costo de desarrollo** | $1.800 − $1.259 | **$541** |

**Atención — cambio relevante al sacar el setup:** con **solo 2 grupos** en Plan Básico ($600 × 2 = $1.200) el costo **ya no queda cubierto** — faltarían $59 (antes, con setup, 2 grupos sí alcanzaban con margen). La meta de "2 o 3 grupos cubren el desarrollo" pasa a depender de tener **3 grupos como mínimo**, no 2. Si el cliente quiere mantener el margen de seguridad con 2 grupos, hay que subir el plan Básico o reintroducir algún cargo inicial.

**Costo de oportunidad del descuento:** el "2x1" anual reduce el recurrente de régimen permanente de $60 a $50/mes equivalente por grupo en Plan Básico — compensado porque el efectivo se cobra todo junto al inicio en vez de diluido en 12 cobros (mejor cashflow, menor riesgo de mora/cancelación a mitad de año).

### Límite técnico confirmado (actualizado 2026-07-02, ver Arquitectura sección 7.1)
- Límite real del hosting: **10 conexiones simultáneas por usuario MySQL**, con posibilidad de crear **hasta 5 usuarios MySQL** → arquitectura de pools segregados (Web / Hangfire / Staging / 2 de reserva). El pool dedicado a tráfico web queda en 8 conexiones concurrentes (con margen de 2).
- Con EF Core (conexión tomada solo durante la query, no durante toda la sesión del usuario), 8 conexiones concurrentes alcanzan cómodamente para el volumen esperado de los planes Básico y Pro. No es una cifra de "8 usuarios simultáneos", es "8 queries ejecutándose en el mismo milisegundo".
- Checkpoint técnico se mantiene en **~15-20 agencias pagas activas** (o antes si se detectan timeouts de pool en logs) para decidir si conviene activar el 4° usuario MySQL como segundo pool Web (balanceo por `AgenciaId`) o migrar a un hosting con mayor techo — relevante sobre todo para sostener volumen de plan Enterprise.
- El límite de 20 bases de datos del plan Premium no aplica como restricción aquí porque el modelo es de tenant compartido (una sola BD para todas las agencias) — ver decisión de Arquitectura.

### Ejemplo de rentabilidad — 3 grupos en Plan Básico (vista de régimen mensual permanente)

> Nota: esta vista es la rentabilidad de *régimen* (mes a mes, a precio de lista). Para la cobertura del costo de desarrollo *de entrada* con prepago anual, ver la subsección anterior "Política de cobro — prepago anual".

**Modelo de negocio confirmado (2026-07-02):** **Olvidata Soft** opera y factura la plataforma SaaS con infraestructura propia (hosting + Apify a nombre de Olvidata, no de Century 21 La Plata). Century 21 La Plata es el tenant piloto que paga su propio desarrollo por separado (USD 1.041, ver sección 14 y `presupuesto-cliente.md`), no el dueño del producto revendible. Esto habilita vender a otros grupos/agencias (incluso competidoras de Century21) sin conflicto de infraestructura ni de titularidad de datos.

| Concepto | Cálculo | USD |
|---|---|---:|
| Ingreso recurrente mensual (3 × $60) | 3 grupos en Plan Básico | $180 /mes |
| Costo fijo compartido de plataforma (hosting $7.95 + Apify ~$12.5) | no escala por grupo hasta el checkpoint de ~15-20 | −$20.45 /mes |
| **Ganancia recurrente mensual** | $180 − $20.45 | **$159.55 /mes (≈89% margen)** |
| **Ganancia anual (todos los años, sin setup ya no hay salto en el año 1)** | $180×12 − $20.45×12 | **$1.915 /año** |

Costos que **no** se descuentan de esta cuenta porque no son marginales a estos 3 grupos: el WhatsApp Cloud API lo paga cada grupo directamente (no es costo de Olvidata), y las herramientas de desarrollo IA ($495/año) son un costo fijo del negocio completo de Olvidata, no atribuible a este canal en particular.

**Lectura clave para el plan de ventas:** el margen de ~86% es sensiblemente mayor al de los proyectos BUILD actuales (que cargan tiempo de desarrollo por cliente) y al del recurrente de mantenimiento tradicional (donde el hosting hoy corre ~$75/año/cliente, según `plan_ventas_olvidata.md` sección 1, porque cada cliente tiene su propio hosting). En el modelo SaaS, 3 grupos en Plan Básico ya cubren el costo fijo compartido con margen — cada grupo adicional (hasta el checkpoint de conexiones) es casi 100% ganancia incremental menos su propio soporte. Además, con el cambio de unidad de venta (Agencia → Grupo), una franquicia multi-sucursal como Century21 podría representar varios "grupos" pagos en vez de uno solo, si en el futuro decide sumarse como cliente SaaS de su propia red.

### Investigación de mercado — competencia regional (2026-07-02)

Research de CRMs inmobiliarios SaaS en Argentina/LatAm hispanohablante (dólar blue de referencia $1.505 = USD 1, 01/07/2026).

| Producto | Precio aprox. | Multi-agencia | WhatsApp bot | Agregador portales |
|---|---|---|---|---|
| **KiteProp** (AR/Chile) — comparable más cercano | USD ~46-105/mes según usuarios | Sí, jerárquico (org→sucursal→usuario) | Sí ("nativo", no confirmado si es bot automatizado) | Sí, 30+ portales |
| 2clicsApp (AR/UY) | USD ~38-109/mes | Parcial (solo plan tope) | Sí, pero **addon pago aparte** (~USD 28 extra) | No confirmado |
| Tokko Broker (AR/MX/multi-país) | **USD 69/mes (Duo, ~2 usuarios), USD 110/mes (Empresa), USD 147/mes (Empresa superior)** — dato directo obtenido 2026-07-02, ver nota abajo; MX ~USD 26-190/mes | No confirmado (parece multi-usuario, no multi-tenant) | No confirmado | Sí, red propia + Inmuebles24 |
| Wasi, Xintel, ALTOR | **Precio no público** (piden demo) | Variable, no confirmado en detalle | Variable | Variable |
| Bitrix24 (genérico, no vertical) | USD 69/mes (5 usuarios) | No es multi-tenant real | Sí, omnicanal genérico | **No** |
| Follow Up Boss (EE.UU., referencia) | USD 69-1.000/mes | Sí | No | No |

**Rango de mercado verificado:** ~USD 10-15/mes (entrada, 1 usuario) a ~USD 100-190/mes (6-10 usuarios). Varios players esconden precio en planes grandes (señal de que esa franja es negociada caso a caso, no de lista).

**Conclusión:** los precios de century-21 (USD 49/129/299) quedan en la banda **media-alta pero dentro de rango**, no fuera de mercado — Básico es del mismo orden que KiteProp Office (3 usuarios), Pro es competitivo contra 2clicsApp "todo incluido" (que cobra WhatsApp aparte). El hueco de mercado real no es de precio: **ningún competidor verificado combina multi-agencia jerárquica real + agregador de portales + bot de WhatsApp automatizado con alertas de fechas clave** en un solo producto — KiteProp es el que más se acerca, pero sin confirmar si su WhatsApp es bot automatizado o chat asistido. El argumento de venta de century-21 frente al mercado argentino es "todo incluido en un solo producto", no "más barato". Enterprise (USD 299+) no tiene comparable directo con precio público — zona de incertidumbre real de mercado, no solo de este research.

Fuentes: KiteProp (kiteprop.com/ar/planes), 2clicsApp (2clics.app/precios), Tokko Broker (tokkobroker.com), Wasi (wasi.co), Xintel (xintel.com.ar), ALTOR (altor.ar), Bitrix24 (bitrix24.es/prices), Follow Up Boss (followupboss.com/pricing), comparativas de comparasoftware.com.ar y redtuinmobiliaria.com. Detalle completo de research y advertencias de calidad de dato en `trazabilidad.md` (entrada 2026-07-02).

**Segunda pasada de research (cross-check independiente, 2026-07-02):** una segunda corrida de investigación confirmó la conclusión general (century-21 en banda media-alta, no outlier) pero corrige/agrega dos puntos:
- **Xintel sí tiene automatización real de WhatsApp** ("Chat Multiagente" con respuesta de bienvenida, derivación automática y recordatorios) — la primera pasada lo había marcado como "no confirmado". Xintel esconde precio ("armá un plan a medida") y es percibido por terceros como tecnológicamente desactualizado — oportunidad de posicionamiento para century-21 como alternativa moderna con precio transparente.
- **Cuidado con las fuentes de KiteProp:** buena parte de las afirmaciones de KiteProp sobre sí mismo (multisucursal jerárquica, WhatsApp nativo, 30+ portales) vienen de contenido autopromocional del propio KiteProp comparándose contra su competencia (se autoevalúa 9,4/10) — recomendado verificar de forma independiente (ej. demo real) antes de asumirlo como el rival más fuerte en funcionalidad.
- Nuevo competidor detectado: **Solution Malls** (+20 años en el mercado, +80 clientes LatAm), pero orientado a holdings/ERP grandes más que a agencias chicas — precio no público.
- Ambas pasadas coinciden en que Tokko Broker Argentina bloquea el acceso público a precios (HTTP 403 en la página oficial), y que Wasi/Xintel esconden precio en los planes grandes.

**Tercera consulta (2026-07-02) — precio de Tokko Broker obtenido vía fuente de terceros (SUPERADA por el dato directo de más abajo):** el sitio oficial de Tokko sigue bloqueando el acceso directo por WebFetch (HTTP 403), pero `comparasoftware.com.ar/tokko-broker` publicaba precios propios sensiblemente más bajos que los reales — **dato descartado**, ver corrección inmediatamente abajo.

**Cuarta consulta (2026-07-02) — precio OFICIAL de Tokko Broker Argentina, aportado directamente por el cliente desde el sitio real (tokkobroker.com/es-ar/planes, con sesión que sí accede — el bloqueo 403 es solo para tráfico automatizado):**

Dólar blue de referencia: **$1.515 ARS = USD 1** (cotización del día, aportada por el cliente).

| Plan Tokko | Usuarios | ARS/mes (con impuestos) | USD/mes (con impuestos) | ARS/mes (sin impuestos nacionales) | USD/mes (sin impuestos) |
|---|---:|---:|---:|---:|---:|
| Inicial | 2 | $136.956 | **$90,40** | $113.187 | $74,71 |
| *(plan intermedio, nombre no capturado en el copy-paste)* | 4 | $237.835 | **$156,99** | $196.558 | $129,74 |
| Profesional | 10 | $378.201 | **$249,64** | $312.563 | $206,31 |
| Corporativo | 15 | $656.678 | **$433,45** | $542.709 | $358,22 |

Este dato **reemplaza completamente** las dos referencias anteriores de Tokko (la de México y la de comparasoftware.com.ar), que resultaron muy por debajo del precio real. Es la fuente más confiable que tenemos de Tokko porque viene directo del sitio oficial, no de un intermediario.

**Comparación directa contra century-21 v3 (mismos tramos de usuarios, precio con impuestos — lo que paga el cliente final):**

| Usuarios | Tokko (con impuestos) | century-21 v3 | Diferencia |
|---:|---:|---:|---|
| 2-3 | $90,40/mes (Inicial, 2 usuarios) | $60/mes (Básico, hasta 3 usuarios) | century-21 **33% más barato**, con un asesor más de capacidad |
| 10 | $249,64/mes (Profesional) | $150/mes (Pro) | century-21 **40% más barato**, misma capacidad |
| 15 | $433,45/mes (Corporativo) | $200/mes (Enterprise: $150 + 5×$10) | century-21 **54% más barato**, misma capacidad |

**Lectura clave:** con el dato real de Tokko, la brecha es mucho más grande de lo que mostraba la fuente de terceros — century-21 no está "dentro de rango", está **muy por debajo del jugador más establecido del mercado argentino en los tres tramos comparables**. Esto abre espacio real para subir precios sin dejar de ser claramente más barato que Tokko: por ejemplo, duplicar el Pro actual (a ~$300/mes) todavía dejaría a century-21 un 20% por debajo del Profesional de Tokko. **No se aplica ningún cambio de precio en este momento** — se deja registrado como espacio de negociación disponible, a definir si el cliente quiere capturar más de ese margen.

### Reevaluación de posición competitiva tras pasar a modelo de suscripción anual (2026-07-02)

El research original comparó contra el precio mensual de lista ($49/129/299). Con el pasaje a `presupuesto-cliente.md` como hoja de precios de suscripción (configuración inicial + plan anual con 2 meses de descuento), el equivalente mensual bajó ~17% sin tocar el precio de lista:

| Plan century-21 | Mensual lista | Equivalente anual | Comparable de mercado más cercano | Rango de mercado | Posición |
|---|---:|---:|---|---:|---|
| Básico (≤3 asesores) | $49/mes | **$40,83/mes** | KiteProp Single/Office (1-3 usuarios), 2clicsApp Esencial (2 usuarios) | $38-80/mes | En rango, mitad-baja con precio anual |
| Pro (≤10 asesores) | $129/mes | **$107,50/mes** | 2clicsApp Profesional (6 usuarios + WhatsApp aparte ≈$137 todo incluido), Tokko Broker MX Enterprise (6-10 usuarios, ~$190/mes) | $109-190/mes | Por debajo del techo, con más usuarios incluidos y WhatsApp ya incluido (la competencia lo cobra aparte o no lo tiene) |
| Enterprise (11+ asesores) | $299+/mes | **$249,17+/mes** | Sin comparable regional con precio público (Wasi/Xintel/Tokko AR ocultan precio). Única referencia pública: Follow Up Boss (EE.UU.) $499-1.000/mes | Sin dato regional | Zona de incertidumbre de mercado se mantiene, pero muy por debajo de la única referencia pública disponible |

**Respuesta corta (vigente hasta la revisión de precios de más abajo): sí, seguimos dentro del margen competitivo — y mejoró.** El plan anual movió a century-21 de "banda media-alta" (conclusión del research original) a "banda media, con ventaja de valor": mismo precio de lista, pero el cliente que paga el año completo queda en la mitad o por debajo del rango verificado, y en Pro directamente por debajo del techo de mercado con más funcionalidad incluida (WhatsApp + agregador de portales, que la competencia cobra aparte o no ofrece). Enterprise sigue siendo la única zona sin validar contra mercado regional.

### Reevaluación v2 — tras la corrección de la curva de precio por asesor (2026-07-02)

Con Pro subido a $199/mes y Enterprise rediseñado a $30/asesor/mes plano (ver "Planes propuestos" más arriba), la posición cambia:

| Plan century-21 | Mensual lista (nuevo) | Equivalente anual | Comparable de mercado | Posición |
|---|---:|---:|---|---|
| Básico (≤3) | $49/mes | $40,83/mes | Tokko Duo $69/mes (2 usuarios) | **Más barato que Tokko** teniendo 1 asesor más de capacidad — se mantiene como gancho de entrada |
| Pro (≤10) | $199/mes | $165,83/mes | Tokko Empresa superior $147/mes (probable 6-10 usuarios) | **Por encima del techo de Tokko** — decisión consciente, apostando a que el bundle completo justifica el sobreprecio |
| Enterprise (11+) | $30/asesor/mes | $25/asesor/mes (anual) | Sin comparable regional público | Sigue sin validar — ahora es una tarifa por asesor simple de defender en una negociación 1 a 1 |

**Conclusión revisada (v2, superada por v3 más abajo):** century-21 deja de estar "dentro de rango en toda la grilla" y pasa a una estrategia de **precio ancla barato en Básico + precio premium en Pro/Enterprise**, apostando la diferenciación de producto (todo-en-uno) para sostener el sobreprecio en los planes de equipos más grandes. Esto resultó ser una lectura incorrecta de lo que pidió el cliente — ver corrección v3.

### Reevaluación v3 — vuelta a volumen = más barato (2026-07-02, versión vigente)

El cliente aclaró que la intención real era la opuesta a la v2: mismo servicio en todos los planes, precio por asesor **decreciente** con el volumen, partiendo de Básico = USD 60/mes para 3 asesores. Con los precios v3 (Básico $60, Pro $150, Enterprise $150+$10/asesor extra):

| Plan century-21 (v3) | Mensual lista | USD/asesor al tope | Comparable Tokko Broker | Posición |
|---|---:|---:|---|---|
| Básico (≤3) | $60/mes | $20,00 | Duo $69/mes (2 usuarios) | Más barato que Tokko con 1 asesor más de capacidad |
| Pro (≤10) | $150/mes | $15,00 | Empresa superior $147/mes (6-10 usuarios, probable) | Prácticamente empatado con el techo de Tokko, pero cubriendo más asesores y con WhatsApp+agregador incluidos |
| Enterprise (11+) | $150 + $10/asesor extra | $14,55 en 11, bajando | Sin comparable regional público | Sigue sin validar, pero ahora la lógica de precio (volumen = descuento) es más fácil de justificar en una negociación que un premium plano |

**Conclusión v3:** con la v3, century-21 quedaba dentro o por debajo del rango de mercado en los tres escalones frente al dato de terceros — pero ese dato resultó estar muy por debajo del precio real de Tokko (ver "Cuarta consulta"). Superada por v4.

**Conclusión v4 (vigente, corregida 2026-07-02):** con el precio oficial de Tokko confirmado, se rearmaron los planes (ver "Planes propuestos — revisión v4" más arriba) para capturar parte del margen documentado sin perder la ventaja de precio ni la curva decreciente por asesor: Básico 33,6% más barato que Tokko Inicial, Pro 25,9% más barato que Tokko Profesional, Enterprise 40,0% más barato que Tokko Corporativo (a 15 asesores). Facturación exclusivamente anual, sin fee de configuración inicial. Es la versión recomendada para ofrecer.

### Pendiente de validar con el cliente antes de cerrar precios
- Confirmar si el diferencial "bot de WhatsApp automatizado" (vs. chat asistido) de KiteProp es real — si lo es, deja de ser un diferencial exclusivo de century-21 y hay que reforzar otro ángulo de venta (alertas de fechas clave, o precio).
- Plan Enterprise sin comparable de mercado verificado — validar apetito de precio directamente con agencias grandes antes de publicarlo como precio de lista.
- Definir si el costo de WhatsApp (Meta) se factura aparte a cada agencia o se incluye prorrateado en el plan.

## Historial de ajustes
- 2026-06-25: Archivo creado en bootstrap del proyecto.
- 2026-07-02: Presupuesto inicial completo. 11 módulos, 64.0h M, $1.076 desarrollo + $100 tokens IA = $1.176 total. Etapa 1 $764 / Etapa 2 $412. Mantenimiento Plan PREMIUM $400/año. Agregado plan de venta SaaS Básico/Pro/Enterprise a pedido del cliente, con análisis de costos operativos compartidos y checkpoint técnico de hosting en ~15-20 agencias. Estado: BORRADOR — pendiente aprobación del cliente (gate hacia Implementación).
- 2026-07-02 (cambio de modelo de roles): Reestimación completa por eliminación del rol Gerente (gatillo: cambio de reglas de negocio y permisos). 13 módulos (se quita M8 standalone, se agregan M12 Mi perfil y M13 Perfil de grupo). Total interno 69.0h M / $1.259 (incluye Tokens IA). Total facturado a Century21: $1.041 (excluye M1+M2, gestión de plataforma que solo usa Olvidata). Plan de venta SaaS actualizado: unidad de contratación pasa de Agencia a Grupo, mejora la economía de reventa a franquicias multi-sucursal. Documento cliente actualizado en paralelo (`presupuesto-cliente.md`).
