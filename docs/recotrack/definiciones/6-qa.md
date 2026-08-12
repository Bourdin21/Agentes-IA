# Memoria - QA

## Proyecto: recotrack
## Ultima actualizacion: 2026-08-11

## Definiciones vigentes

### Casos de prueba acordados

Sin registros. El rol `qa-mvc` no existia cuando se implementaron las iteraciones 1 y 2 (ver `5-implementador.md`); ninguna de las dos paso por una etapa de pruebas funcionales formal documentada. La unica verificacion registrada en ambos casos es "Build OK".

### Defectos activos

- **DEF-01 (detectado y resuelto 2026-08-11, fuera de pipeline)**: `InvalidCastException: Unable to cast object of type 'System.TimeSpan' to type 'System.TimeOnly'` en `GetMultas`/`GetAccidentes` (produccion), causando 500 y error de DataTables en `tblMultas`/`tblAccidentes`. Causa: mapeo nativo `TimeOnly` de `MySql.EntityFrameworkCore` 10.0.1 contra columnas `TIME` del MySQL de produccion (no reproducible en dev). Fix aplicado: `HasConversion` explicito a `TimeSpan?` (ver `3-arquitecto-mvc.md` A-09). **Estado: corregido en codigo local, pendiente de deploy y verificacion end-to-end en produccion.**
- **DEF-02 (detectado y resuelto 2026-08-11)**: email de notificacion de errores nunca se enviaba por clave de configuracion incorrecta (`Notificaciones:ErrorEmail:Destinatarios` en vez de `Olvidata_ErrorEmail:Destinatarios`). Impacto: cualquier excepcion no manejada en produccion, desde que existe el middleware, no genero alerta. **Estado: corregido en codigo local, pendiente de deploy.**

### Riesgos de liberacion

- El fix de DEF-01 no fue probado contra una base de datos con datos reales de `Hora` poblados fuera de produccion — la verificacion de que el `HasConversion` resuelve el problema se basa en el analisis del stack trace y el patron de causa raiz, no en una repro controlada.
- La migracion `FixHoraTimeOnlyMapping` no fue aplicada aun en produccion.
- `DestinatariosTaller` en `appsettings.Production.json` sigue con placeholder `""` desde la iteracion 2 (jun-2026) — sin confirmar con el cliente.

### Estado go/no-go

- **DEF-01 / DEF-02**: NO-GO hasta deployar y confirmar en produccion (no hay QA post-deploy todavia).
- Resto del sistema (iteraciones 1 y 2): sin evaluacion QA formal — se asume estable por uso continuo en produccion desde 2025-07 sin reportes adicionales conocidos, pero no hay checklist de regresion ejecutado.

## Historial de ajustes
- 2026-08-11: primera entrada de este archivo (rol nunca usado antes en recotrack). Registrados DEF-01 y DEF-02 detectados y resueltos el mismo dia a partir de un reporte del cliente en produccion.
