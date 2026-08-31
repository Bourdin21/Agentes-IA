# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-08-31 - implementador — cierre de auditoria QA (16 hallazgos) + Data Protection persistente
- Etapa: Implementacion directa sobre hallazgos ya auditados por el agente QA (autorizacion explicita del dueño del proyecto: "implementar todos").
- Cambio: los 16 hallazgos implementados, de bloqueante a bajo. Bloqueante: `UsersController.Index` caia con 500 siempre por un `IN` de `HashSet<string>` contra MySQL (MH-001) — se materializa la lista y el filtro por rol pasa a memoria, con `totalCount`/paginacion recalculados despues. Altos: decimales culture-dependientes (LP-003), `Home/Index` y `CalcularDeudaTarjetaAsync` sin filtro de `Pendiente`, confirm de importacion sin re-validar duplicados contra la base, movimiento solo-USD sin cotizacion que se guardaba en $0. Medios/bajos: backdating de `FechaInicio` en cuotas N/M con N>1, 292 lineas de codigo muerto eliminadas del importer (`ImportarResumenAsync` y su cadena, sin caller) + carpeta `Services/Importacion/` (4 archivos de 0 bytes), clave de dedup variable para la fila sintetica de impuestos, exclusion de falsos positivos permanentes del panel de disparidades USD/ARS, `Cuota.FechaInicio` y `Movimiento.DescripcionOriginal` editables, redondeo PAT-003 (ultima cuota absorbe centavos), saldo por cuenta agregado server-side, `[Authorize]` de clase en `HomeController`. Feature nueva: Data Protection con keyring persistente en disco para que los usuarios no se deslogueen en cada deploy/reciclado.
- Motivo: auditoria de calidad del agente QA + pedido de fondo del dueño sobre la invalidacion de sesion.
- Impacto en capas: Application (DTOs, `IResumenTarjetaImporter`), Infrastructure (importer, parser Mastercard, `CotizacionMovimientosService`), Web (5 controllers, ViewModels, 6 vistas, `Program.cs`, model binder nuevo), Infraestructura de deploy (`.pubxml`, `.gitignore`). Domain sin cambios.
- **Sin migracion EF**: ningun cambio de esquema. `Movimiento.DescripcionOriginal` y `Cuota.FechaInicio` ya existian como columnas; lo unico que cambio es que ahora se exponen en los formularios.
- Desviacion de alcance deliberada (LP-003): la auditoria pedia arreglar solo el render de decimales y **no** agregar `InvariantDecimalModelBinder` ni tocar los hidden de `Preview.cshtml`. Se midio que bajo la cultura `es-AR` fijada en `Program.cs` el binder por defecto parsea `"1234.56"` (lo que postea todo `<input type="number">` por spec HTML) como **123456**: la entrada ya corrompia importes x100 en silencio, y el fix acotado habria empeorado el cuadro (campo bien mostrado, corrompido al guardar). Como los sitios de post-back son exactamente 8 y enumerables, se implemento el par completo binder + render.
- Riesgos/supuestos: build Release OK, 0 errores (9 warnings, todos preexistentes). Sin smoke test propio (regla del rol). Residuales nuevos R11 (dedup no cubre dos POST estrictamente concurrentes: requeriria indice unico + migracion, diferido), R12 (el backdating aplica solo a cuotas nuevas; las ya persistidas se corrigen a mano desde `Cuotas/Edit`) y R13 (las reglas `MsDeploySkipRules` del `.pubxml` estan verificadas por precedente de `elevenlaplata` — mismo hosting site4now y mismo SDK — pero no ejecutadas todavia en un deploy real de este proyecto: **confirmar en el proximo deploy que `DataProtection-Keys/` sobrevive**).
- Documentacion actualizada in-place: `2-dominio.md` (editabilidad de `Cuota` como regla de negocio explicita, redondeo PAT-003, pendientes fuera de todos los totales) y `3-aplicacion-infraestructura.md` (clave de dedup sin `Monto`, cuotas N>1 ya no excluidas, carpeta `Services/Importacion/` eliminada).

### 2026-07-23 - orquestador (barrido cross-proyecto) — mergeada feature reintegros Mastercard/Visa desde la memoria local del proyecto
- Etapa: 2-3-5 (diseño + arquitectura + implementacion, mergeadas juntas)
- Cambio: se detecto que `C:\Sistemas\virtualwallet\docs\virtualwallet\definiciones\{2-disenador-funcional,3-arquitecto-mvc,5-implementador}.md` (memoria local del proyecto, dated hasta 2026-07-07) tenian una cadena completa de 4 etapas sobre el importador de resumenes de tarjeta que nunca se habia mergeado a este repo central: (1) reintegros M2/M5/M7 (persistir como Ingreso+EsPagoTarjeta=true, dedupe por cupon en linea cruda), (2) ajustes funcionales (cuenta TC por filtro de texto, fecha desde el PDF, USD como fuente de verdad), (3) reescritura completa del parser Visa contra un PDF real (el parser original no matcheaba el formato real del banco), (4) importes ARS/USD en dos columnas + filtros nuevos de Movimientos + KPIs de proyeccion en dashboards. Todo mergeado como bloque unico en `definiciones/5-implementador.md`.
- Motivo: pedido explicito del usuario de auditar cada carpeta de proyecto individual en busca de especificaciones que debieran vivir en la memoria centralizada de Agentes-IA, y mergearlas.
- Impacto en capas: Application (DTOs), Infrastructure (parsers Mastercard/Visa, importer), Web (controller, ViewModels, vistas). Domain sin cambios en ninguna de las 4 partes.
- Riesgos/supuestos: sin migracion EF en ninguna de las 4 partes. **Pendiente de visto bueno de stakeholder**: R5 — reintegros modelados como `Ingreso+EsPagoTarjeta=true` podrian no ser contemplados por reportes historicos que asuman que "Ingreso" nunca lleva ese flag. QA manual end-to-end con PDFs reales (incluyendo un Visa con consumos en USD) tambien pendiente.

### 2026-05-11 - implementador
- Etapa: Implementacion — Dolar historico
- Cambio: nueva seccion "Dolar Historico": `ICotizacionService`, `CotizacionService`, `DolarController`, `DolarHistoricoViewModel`, vista `Dolar/Historico.cshtml`. `MovimientosController` actualizado para integrar cotizacion en Create/Edit. Menu actualizado.
- Motivo: permitir ver la cotizacion del dolar a la fecha de cada movimiento y convertir importes en pesos a dolares.
- Impacto en capas: Application (interface), Infrastructure (service), Presentacion (controller + vistas).
- Riesgos/supuestos: sin migracion EF. `CotizacionService` consulta API externa con fallback. Build OK.

### 2026-05-05 - implementador
- Etapa: Implementacion — Mejoras importacion resumen + defectos D-04/D-09/D-10 + mejoras dashboard M-04/M-05/M-06/M-07
- Cambio: cierre defectos QA (D-04 flag EsPagoTarjeta en formulario manual, D-09 rename CuotasActualizadas->CuotasReutilizadas, D-10 persistencia filtros dashboard en Session). Mejoras dashboard: M-04 badge Pendiente Top 10, M-05 columnas Restantes/MontoPendiente en Cuotas Activas, M-06 columna SaldoArrastrado Deuda Tarjeta, M-07 alerta crecimiento categoria >=30%. Migracion `ConstrainDescripcionOriginalLength`. Parsers actualizados. `Program.cs` actualizado.
- Motivo: calidad post-QA y nuevas funcionalidades del dashboard solicitadas por el cliente.
- Impacto en capas: todas.
- Riesgos/supuestos: build OK. Script idempotente `ConstrainDescripcionOriginalLength.sql` pendiente en produccion.
