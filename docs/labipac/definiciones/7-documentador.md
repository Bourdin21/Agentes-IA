# Memoria - Documentador

## Proyecto: labipac
## Ultima actualizacion: 2026-07-23 — resumen de sprint M10+M11+M12 (Produccion Mensual por Centro de Salud)

## Definiciones vigentes

### Documentacion al cliente
- `docs/labipac/resumen-sprint-2026-07-23.md` — resumen de sprint entregado tras implementacion + verificacion liviana, cubre M10 (ABM Centro de Salud), M11 (CentroSaludId en Produccion Mensual + RN-24) y M12 (Centro de Salud en PDF). Basado en `5-implementador.md` sesion 4. Nota: no hubo QA formal exhaustivo tipo sesion 2 (se hizo verificacion directa del orquestador por corte de un subagent, ver `trazabilidad.md` 2026-07-23) — se documenta igual porque no se encontraron defectos, pero queda abierto si el cliente pide QA mas profundo antes de considerar el sprint 100% cerrado.
- `docs/labipac/presupuesto-cliente.md` — presupuesto de las 3 mejoras (Unidad/Precio por Unidad, carga masiva, fix PDF), aprobado.
- `docs/labipac/resumen-sprint-2026-07-08.md` — resumen de sprint entregado al cierre de QA, cubre M7 (Precio por Unidad), M8 (carga masiva + alta rapida) y M9 (fix PDF). Basado en `5-implementador.md` sesion 3 y `6-qa.md` (QA sin defectos bloqueantes).

### Manuales y alcance
- Pendiente: actualizar `docs/labipac/manuales/manual-practicas.md` para reflejar que el precio de un Perfil ya no se edita a mano (se deriva de Unidad x Precio por Unidad) y que la composicion dejo de ser obligatoria. No se actualizo en este cierre por no haber sido solicitado explicitamente.

### Cierre documental
Resumen de sprint entregado. Pendiente que el cliente ejecute las 8 pruebas manuales de UI listadas por QA y confirme antes del cierre de calibracion final.

## Historial de ajustes
- 2026-07-08: Se redacto el resumen de sprint para las 3 mejoras (Precio por Unidad, carga masiva + alta rapida, fix PDF), reflejando solo lo implementado y validado por QA (sin defectos bloqueantes). Se documento como pendiente la actualizacion del manual de Practicas/Perfiles para reflejar el nuevo modelo de precios.
