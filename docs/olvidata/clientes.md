# Clientes y su plan
> **Archivo generado — no editarlo a mano.** Lo regenera `python scripts/olvidata_datos.py clientes` leyendo el CRM productivo.
> Snapshot del 2026-10-15. Lo que el CRM no sabe se edita en `datos-manuales.yml`.

| Cliente | Sistema | Frente | Plan | Recurrente anual USD | Año 1 gratis | Alta | Próxima renovación |
|---|---|---|---|---:|---|---|---|
| Contadores BMA | Conversor | Build | Starter | 0 | no | 2026-06-26 | 2027-06-26 |
| Contadores BMA | Front web | Landing | Starter | 0 | no | 2026-02-23 | 2027-02-23 |
| Delicias Naturales | — | Build | Premium | 200 | no | 2026-03-01 | 2027-03-01 |
| Diercas SA | — | Landing | Premium | 400 | sí | 2026-08-17 | 2027-08-17 |
| Eleven La Plata | Eleven | Build | Premium | 280 | no | 2026-03-01 | 2027-03-01 |
| ESCABA | — | Build | Starter | 160 | no | 2026-07-02 | 2026-10-02 |
| Estancia Santa Rosa | — | Build | Premium | 300 | sí | 2026-05-08 | 2027-05-08 |
| Ferretería la Platense | — | Build | Starter | 500 | sí | 2026-08-10 | 2027-08-10 |
| KOI | KOI Dumplings | Build | Premium | 400 | sí | 2026-06-24 | 2027-06-24 |
| LABIPAC | Instituto Privado de Análisis Clínicos | Build | Starter | 0 | no | 2026-06-15 | 2027-06-15 |
| Lumitrack | — | Build | Pro | 250 | no | 2026-06-18 | 2027-06-18 |
| Lumitrack | Recotrack | Build | Pro | 250 | no | 2026-01-26 | 2027-01-26 |
| Marí Hogar | — | Build | Premium | 400 | sí | 2026-07-28 | 2027-07-28 |
| PiApartments | — | Build | Pro | 180 | no | 2026-03-01 | 2027-03-01 |
| ShowroomGriffin | Griffin Showroom | Build | Starter | 300 | no | 2026-04-15 | 2027-04-15 |
| Vinoysefue | — | Build | Starter | 200 | no | 2026-03-16 | 2027-03-16 |

### Bajas

El CRM marca el cliente como inactivo pero **no guarda la fecha de la baja**, así que la última columna sigue siendo la renovación que tenía agendada, no el día en que se fue. Por eso la serie mensual de `metricas.md` lo cuenta como vivo hasta hoy y su total no coincide con el de este archivo.

| Cliente | Sistema | Frente | Plan | Recurrente anual USD | Año 1 gratis | Alta | Renovación que tenía agendada |
|---|---|---|---|---:|---|---|---|
| Belclau | — | Build | Starter | 180 | no | 2026-03-01 | 2027-03-01 |

## Lo que suma

| Concepto | Valor |
|---|---:|
| Clientes activos | 16 |
| Recurrente anual **contratado** | USD 3.820 |
| Recurrente anual **cobrable hoy** (sin los de año 1 gratis) | USD 1.820 |
| Recurrente mensual cobrable | USD 152 |
| Ticket anual real promedio (solo los que pagan recurrente) | USD 294 |
| Ticket anual de planificación que usa el plan financiero | USD 426 |
| Upsells registrados (acumulado histórico) | USD 7.818 en 35 operaciones |

**Contraste con el supuesto del plan:** el ticket real promedio de los clientes que pagan recurrente es USD 294 contra los USD 426 que usa el plan financiero (-31%). Con 16 clientes activos, el recurrente contratado da USD 318/mes.

**Clientes activos con recurrente en 0** (o no tienen plan de mantenimiento, o está sin cargar en el CRM — conviene decidir cuál de las dos): Contadores BMA, LABIPAC.

## Renovaciones

**Vencidas** (la fecha ya pasó y el cliente sigue activo — o se renovó sin actualizar el CRM, o hay que cobrarla):

- **ESCABA** — vencía el 2026-10-02, USD 160/año (13 días).

## Upsells por cliente

| Cliente | Tipo | USD | Fecha |
|---|---|---:|---|
| Belclau | Dominio | 17 | 2026-03-11 |
| Belclau | Trabajo adicional | 149 | 2026-04-20 |
| Contadores BMA | Pago único | 199 | 2026-06-30 |
| Delicias Naturales | Trabajo adicional | 67 | 2026-02-11 |
| Delicias Naturales | Trabajo adicional | 200 | 2026-03-30 |
| Delicias Naturales | Trabajo adicional | 75 | 2026-05-20 |
| Delicias Naturales | Trabajo adicional | 76 | 2026-05-29 |
| Delicias Naturales | Trabajo adicional | 33 | 2026-06-29 |
| Delicias Naturales | Trabajo adicional | 101 | 2026-07-23 |
| Diercas SA | Implementación (cuota 2/2) | 201 | 2026-08-12 |
| Diercas SA | Implementación (cuota 1/2) | 201 | 2026-08-12 |
| ESCABA | Trabajo adicional | 179 | 2026-01-05 |
| ESCABA | Trabajo adicional | 188 | 2026-02-03 |
| Eleven La Plata | Trabajo adicional | 144 | 2026-04-07 |
| Eleven La Plata | Trabajo adicional | 130 | 2026-07-24 |
| Estancia Santa Rosa | Trabajo adicional | 200 | 2026-05-08 |
| Estancia Santa Rosa | Trabajo adicional | 556 | 2026-07-03 |
| Estancia Santa Rosa | Trabajo adicional | 202 | 2026-07-03 |
| Ferretería la Platense | Implementación (cuota 1/3) | 500 | 2026-08-15 |
| Ferretería la Platense | Implementación (cuota 2/3) | 510 | 2026-10-04 |
| Ferretería la Platense | Implementación (cuota 3/3) | 510 | 2026-11-04 |
| KOI | Trabajo adicional | 604 | 2026-06-24 |
| LABIPAC | Pago único | 200 | 2026-07-10 |
| Lumitrack | Trabajo adicional | 143 | 2026-01-05 |
| Lumitrack | Trabajo adicional | 203 | 2026-01-26 |
| Lumitrack | Trabajo adicional | 103 | 2026-06-09 |
| Marí Hogar | Trabajo adicional | 194 | 2026-07-31 |
| Marí Hogar | Trabajo adicional | 718 | 2026-08-01 |
| PiApartments | Trabajo adicional | 168 | 2026-04-07 |
| ShowroomGriffin | Trabajo adicional | 264 | 2026-04-15 |
| ShowroomGriffin | Trabajo adicional | 235 | 2026-05-12 |
| Vinoysefue | Trabajo adicional | 201 | 2026-04-24 |
| Vinoysefue | Trabajo adicional | 118 | 2026-04-28 |
| Vinoysefue | Trabajo adicional | 180 | 2026-06-10 |
| Vinoysefue | Trabajo adicional | 50 | 2026-07-10 |
