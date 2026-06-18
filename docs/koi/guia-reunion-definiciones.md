# Guía de Reunión — Definiciones Pendientes
## Proyecto: KOI — Sistema de Gestión para Inversores
### Fecha: Junio 2026 — ✅ REUNIÓN PROCESADA

> Respuestas incorporadas a `1-analista-funcional.md` §9 (31 decisiones confirmadas · 7 nuevas preguntas derivadas).
> Las preguntas nuevas **P-A01 a P-A07** deben responderse antes de ejecutar la cascada a diseño, arquitectura y presupuesto.
> El presupuesto v3 (USD 1.301) **requiere recálculo** por cambios de alcance.

---

## RESUMEN DE CIERRE

| Bloque | Ítems | Estado |
|---|:---:|---|
| 1 — Comercial | 2 | 🟡 Pendiente firma (precio a recalcular primero) |
| 2 — Hipótesis abiertas | 2 | ✅ Confirmadas · ⚠️ 1 nueva derivada (P-A02) |
| 3 — Máquinas de estado | 5 | ✅ Confirmadas · ⚠️ 2 nuevas derivadas (P-A04, P-A07) |
| 4 — Propiedades y campos | 7 | ✅ Confirmadas · ⚠️ 2 nuevas derivadas (P-A01, P-A03) |
| 5 — Pantallas | 10 | ✅ Confirmadas · ⚠️ 1 nueva derivada (P-A05) |
| 6 — Notificaciones correo | 3 | ✅ Confirmadas |
| 7 — Históricos | 3 | ✅ Confirmadas |
| 8 — Permisos + nueva funcionalidad | 5 | ✅ Confirmadas · ⚠️ 1 nueva derivada (P-A06) |

---

## ⚠️ PREGUNTAS NUEVAS — RESPONDER ANTES DE CASCADA

> Estas 7 preguntas deben cerrarse antes de que Arquitecto y Presupuestador ejecuten la actualización.

| ID | Pregunta | Bloqueante para | Urgencia |
|---|---|---|---|
| **P-A01** | ¿"Cantidad de comensales" se carga manualmente o viene de Ayres (etapa 2)? | M6 Indicadores + Dashboard | 🔴 Alto |
| **P-A02** | ¿Ventas Salón/Delivery REEMPLAZAN a A/B o conviven? ¿Cuál es la nueva base de cálculo de comisiones, IIBB, débitos? | M4 Estado de Resultados — **BLOQUEANTE** | 🔴 Bloqueante |
| **P-A03** | ¿Qué API de dólar y qué cotización (oficial / blue / MEP / CCL)? | M3 TC + nueva integración | 🔴 Alto |
| **P-A04** | Con período no reabreble: si hay error post-cierre, ¿qué mecanismo tiene el Admin? | M10 Liquidaciones | 🟡 Medio |
| **P-A05** | Dashboard "actual": ¿mes Abierto con datos parciales o solo el último Cerrado? | M7 Dashboard | 🟡 Medio |
| **P-A06** | ¿Las notificaciones in-app tienen expiración o se acumulan? | Módulo nuevo Notificaciones | 🟡 Medio |
| **P-A07** | Preview antes de cerrar: ¿el Admin modifica consumos en el preview, o solo confirma? | M10 Liquidaciones + UX | 🟡 Medio |

---

## CAMBIOS NETOS EN ALCANCE (resumen para presupuesto)

| Tipo | Cambio | Módulo | Impacto precio |
|---|---|---|---|
| ➕ | Ajuste manual del monto a repartir + motivo | M10 | Sube |
| ➕ | Integración API dólar para TC automático | M3 nuevo | Sube |
| ➕ | Segunda pantalla Dashboard (Histórico) | M7 expansión | Sube |
| ➕ | Panel de notificaciones in-app con targeting | Módulo nuevo | Sube |
| ➕ | Preview de liquidaciones antes de confirmar cierre | M10 | Sube leve |
| ➕ | Campo `Observaciones` en liquidación del inversor | M10 | Sube leve |
| ➕ | "Cantidad de comensales" si es manual | M6 | Sube leve |
| ➖ | Exportación Excel del estado de resultados | M5 | Baja |
| ➖ | Estado Reabierto del período | M10 | Baja |
| ➖ | Pantalla de configuración SMTP | M15 | Baja |
| ➖ | Contenido del correo simplificado (solo aviso + botón) | M15 | Baja |
| ➖ | Puntos de inversión fijos (sin gestión dinámica) | M9 | Baja |
| 🔄 | Ventas A/B → Salón/Delivery + bases porcentuales a redefinir | M4 | A resolver en P-A02 |

---

## BLOQUE 2 — HIPÓTESIS ABIERTAS ✅

| H | Pregunta | Decisión |
|---|---|---|
| H-01 | ¿Utilidad a repartir admite ajuste manual? | ✅ **Opción B** — Admin ajusta con motivo obligatorio · **sube precio M10** |
| H-02 | ¿Ventas B discriminadas en Dashboard? | ✅ **Opción B** — Solo total. Categorías = **Salón / Delivery** · **P-A02 abierta** |

---

## BLOQUE 3 — MÁQUINAS DE ESTADO ✅

### Período Mensual — máquina redefinida

```
Abierto
   │
   │ [Cerrar período]
   │ Requiere: Ventas (Salón + Delivery) + TC
   ▼
[PREVIEW] ← NUEVO — modal con liquidaciones calculadas
   │         Admin puede ajustar "Monto a repartir" + consumos
   │
   │ [Confirmar]
   │ → Genera Liquidaciones Pendientes
   │ → Envía correo de aviso a inversores activos
   ▼
Cerrado (definitivo — no se puede reabrir)
```

| Pregunta | ✅ Confirmado |
|---|---|
| ¿Rubros obligatorios? | Solo Ventas + TC; gastos pueden ser $0 |
| ¿Reapertura del período? | **Eliminada** — período no se puede reabrir |
| ¿Estado Reabierto? | **Eliminado del alcance** |

> ⚠️ **P-A04** — Error post-cierre: ¿qué mecanismo tiene el Admin?
> ⚠️ **P-A07** — Preview: ¿los consumos son editables en el preview, o solo se muestra y se confirma?

### Liquidación por Inversor — sin cambios estructurales

```
Pendiente ──[Pagar seleccionadas — checkboxes + fecha]──► Pagada
    ▲                                                         │
    └────── [Reabrir con motivo — solo Admin] ────────────────┘
```

| Pregunta | ✅ Confirmado |
|---|---|
| ¿Consumos editables post-cierre mientras Pendiente? | Sí — hasta marcar Pagada |
| ¿Pago masivo? | **Hipótesis C** — checkboxes + "Pagar seleccionadas" + fecha única |
| ¿Resultado negativo? | Liquidación con **$0** — regla `Max(0, utilidad × puntos)` |

---

## BLOQUE 4 — PROPIEDADES ✅

| # | Campo | ✅ Decisión |
|---|---|---|
| 4.1 | Consumos | Monto único mensual — sin detalle de ítems |
| 4.2 | Capital del inversor | Fijo, sin historial |
| 4.3 | TC faltante | **API dólar automático** — Admin puede sobrescribir → **P-A03 abierta** |
| 4.4 | Puntos bonificados | Mostrar total puntos del inversor; recupero con capital $0 = N/A |
| 4.5 | Período por defecto Dashboard | Último período Cerrado disponible |
| 4.6 | Tema por defecto | **Oscuro** |
| 4.7 | Admin en "Mi inversión" | **No** — Admin accede desde Liquidaciones / Reparto General |

> ⚠️ **P-A01** — ¿"Cantidad de comensales" es manual o Ayres (etapa 2)?
> ⚠️ **P-A03** — ¿Qué API de dólar y qué cotización?

---

## BLOQUE 5 — PANTALLAS ✅

| # | Pantalla | ✅ Decisión |
|---|---|---|
| 5.1.a | Rubros automáticos vs. manuales | Lista del Excel confirmada |
| 5.1.b | CMV | Siempre manual |
| 5.2.a | Consumos: cuándo se cargan | Antes del cierre del período (en P-08 con período Abierto) |
| 5.2.b | Grilla liquidaciones | Todos los inversores en una grilla; select múltiple para filtrar |
| 5.2.c | Nota libre en liquidación | ✅ **Sí** — campo `Observaciones` libre |
| 5.3.a | Consumos en historial Mi Inversión | ✅ Sí — columna consumos |
| 5.3.b | Barra de progreso recupero | Hitos 25/50/75/100% + celebración al 100% |
| 5.4 | KPIs Dashboard | **2 pantallas**: (1) mes actual + (2) histórico/evolución |
| 5.5 | Cámaras | iframe + fallback pestaña nueva |

### Dashboard: estructura de las 2 pantallas

**P-02a — Mes actual**
```
[ Ventas total + torta Salón/Delivery ]   [ Resultado vs mes anterior (barras) ]
[ Rentabilidad % ]                        [ Utilidad por punto ]
[ USD: Ventas | Resultado ]               [ Ticket / Cubierto / Comensales* ]
[ Tabla liquidaciones del mes: inversores + estado Pendiente/Pagada ]
```
*Comensales sujeto a P-A01.

**P-02b — Histórico / Evolución**
```
[ Barras+línea: Ventas vs Gastos vs Resultado multi-año ]
[ Línea: Rentabilidad % histórica ]
[ Línea: Resultado en USD histórico ]
[ Línea: Utilidad por punto histórica ]
[ Tabla resumen anual mes a mes ]
```

> ⚠️ **P-A05** — Dashboard "actual": ¿muestra mes Abierto o solo el último Cerrado?

---

## BLOQUE 6 — NOTIFICACIONES POR CORREO ✅

| # | Punto | ✅ Decisión |
|---|---|---|
| 6.1 | Configuración SMTP | Configura el proveedor desde el código; sin pantalla en la UI |
| 6.2 | Contenido del correo | **Solo aviso** de que la liquidación está disponible + botón al sistema |
| 6.3 | Reenvío al re-cerrar | Pide confirmación antes de reenviar |

> ✅ M15 simplificado: sin renderizado de plantilla con datos del mes. Solo email de aviso + link.

---

## BLOQUE 7 — CARGA INICIAL DE HISTÓRICOS ✅

| # | Punto | ✅ Decisión |
|---|---|---|
| 7.1 | Excel fuente | **Ambos disponibles** para entregar ✅ |
| 7.2 | Validación | SuperAdmin (proveedor) valida internamente |
| 7.3 | Meses 2026 parciales | Se migran hasta el último mes con datos en el Excel |

> ✅ Riesgo M14 reducido: Excel confirmados disponibles. Riesgo de demora por espera de insumos = eliminado.

---

## BLOQUE 8 — PERMISOS + NUEVA FUNCIONALIDAD ✅

### Tabla de permisos definitiva

| Acción | Admin | Inversor |
|---|:---:|:---:|
| Ver Dashboard (mes actual + histórico) | ✅ | ✅ |
| Cargar estado de resultados | ✅ | ❌ |
| Cerrar período | ✅ | ❌ |
| Reabrir período global | ❌ eliminado | ❌ |
| Ver estado de resultados anual | ✅ | ✅ |
| Exportar Excel | ❌ eliminado | ❌ |
| Configurar rubros, parámetros, TC | ✅ | ❌ |
| Gestionar puntos (ABM reducido) | ✅ | ❌ |
| Ver reparto general histórico | ✅ | ❌ |
| Ver "Mi inversión" | ✅ (todos) | ✅ (propia) |
| Generar y editar liquidaciones | ✅ | ❌ |
| Marcar como pagada / reabrir individual | ✅ | ❌ |
| Gestionar usuarios | ✅ | ❌ |
| Configurar cámaras | ✅ | ❌ |
| Ver cámaras | ✅ | ✅ |
| Ver historial envíos correo + reenviar | ✅ | ❌ |
| **Crear notificaciones in-app** | ✅ | ❌ |
| **Ver notificaciones in-app** | ✅ | ✅ |

### Nueva funcionalidad: Panel de Notificaciones In-App

- Admin crea notificaciones con destinatarios: todos o selección múltiple de inversores.
- Visible en el navbar de todos los roles (usa `INotificationService` de BlankProject).
- Admin puede crear, los inversores solo leen y marcan como leídas.

> ⚠️ **P-A06** — ¿Las notificaciones tienen expiración automática o se acumulan?

---

*Guía actualizada con respuestas de reunión — KOI / OlvidataSoft — Junio 2026*


