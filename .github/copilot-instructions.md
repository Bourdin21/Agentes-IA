# Copilot Instructions - BlankProject (Orquestador)

Este archivo define el marco general. El detalle operativo y técnico se encuentra modularizado en instrucciones por etapa y por capa dentro de .github/instructions.

## Secuencia operativa obligatoria
Discovery/Relevamiento -> Analisis -> Diseno -> Arquitectura -> Presupuesto -> Implementacion -> Pruebas funcionales -> Documentacion de alcance (cliente) -> Cierre de calibracion estimado vs real

## Objetivo de la reestructuracion
- Separar reglas globales de reglas por capa.
- Facilitar reutilizacion por agentes especializados.
- Reducir ambigüedad al implementar cambios en MVC + EF Core + MySQL.

## Mapa de instrucciones modulares
- .github/instructions/00-operativa-global.instructions.md
- .github/instructions/01-fronteras-por-capa.instructions.md
- .github/instructions/10-blankproject-base.instructions.md
- .github/instructions/20-domain.instructions.md
- .github/instructions/21-application.instructions.md
- .github/instructions/22-infrastructure.instructions.md
- .github/instructions/23-web.instructions.md
- .github/instructions/24-config-paquetes.instructions.md
- .github/instructions/25-frontend-design-system.instructions.md
- .github/instructions/26-checklists.instructions.md
- .github/instructions/27-presupuesto-parametros.instructions.md
- .github/instructions/28-estimacion-avanzada.instructions.md
- .github/instructions/29-trazabilidad-conversacion.instructions.md
- .github/instructions/30-qa-regresiones.instructions.md

## Reglas base que siempre aplican
- No colocar lógica de negocio compleja en Controllers.
- Los Controllers coordinan request/response y delegan en Services.
- La lógica de negocio vive en Services.
- El acceso a datos vive en DbContext, repositorios o infraestructura.
- Toda modificación debe indicar capas afectadas y motivo.
- Si hay migración EF, debe explicitarse.
- Si hay impacto en permisos, estados o validaciones, debe listarse.
- Preservar comportamiento legacy salvo indicación contraria.
- Las pruebas requeridas son funcionales.
- La documentacion requerida es de alcance para el cliente.
- El cierre de calibracion estimado vs real es obligatorio.
- La trazabilidad de la conversacion debe persistirse en /docs/conversaciones con definiciones por agente en archivos .md individuales.

## Bootstrap de proyectos nuevos
- Al iniciar un proyecto nuevo, ademas de copiar la plantilla `/docs/templates/proyecto/` a `/docs/<proyecto>/`, copiar `/docs/templates/proyecto/copilot-instructions.md` al repositorio del sistema bajo `.github/copilot-instructions.md`.
- Personalizar ese archivo con el nombre del proyecto, stack real, paleta y comandos de desarrollo del sistema (secciones marcadas `[Personalizar]` o con placeholders `<...>`).
- Ese archivo es la guia operativa del agente IA dentro del repositorio del sistema y debe quedar consistente con las definiciones de los agentes `3-arquitecto-mvc` y `5-implementador` de ese proyecto.
- Las reglas globales (etapas, fronteras por capa, presupuesto, QA) siguen viviendo aqui en `Agentes-IA/.github/instructions/*` y no se duplican en el repo del sistema.

## Formato mínimo de respuestas técnicas
1. Alcance funcional resumido.
2. Impacto técnico por capa.
3. Riesgos y supuestos.
4. Pruebas funcionales mínimas requeridas.
5. Checklist de salida para merge.
6. Cierre de calibracion estimado vs real.

## Presupuesto
- Los parámetros están en .github/instructions/27-presupuesto-parametros.instructions.md.
- El metodo avanzado de estimacion esta en .github/instructions/28-estimacion-avanzada.instructions.md.

---

## Inventario de proyectos (actualizado 2026-05-20)

| Proyecto | Estado | Stack | Produccion | Repo local |
|---|---|---|---|---|
| delicias-naturales | cerrado | ASP.NET MVC5 + .NET 4.7.2 + EF6 + MySQL | — | `C:\Sistemas\delicias-naturales` |
| recotrack | cerrado | .NET 10 + EF Core 10 + MySQL | — | `C:\Sistemas\recotrack` |
| eleven-la-plata | cerrado | .NET 10 + EF Core + MySQL | — | — |
| lumitrack | cerrado | .NET 10 + EF Core + MySQL | — | — |
| piapartments | cerrado | .NET 10 + EF Core + MySQL | — | — |
| meta-ads | cerrado | — | — | — |
| ganaderia | abierto (QA pendiente) | .NET 10 + EF Core 10 + MySQL | no | `C:\Sistemas\ganaderia` |
| ShowroomGriffin | activo | .NET 10 + EF Core + MySQL + QuestPDF | si (v1) | `C:\Sistemas\ShowroomGriffin` |
| vinosefue | activo | .NET 10 + EF Core + MySQL | si (olvidatasoft-002-site6) | `C:\Sistemas\vino-y-se-fue` |
| virtualwallet | abierto | .NET 10 + EF Core + MySQL | no (dev) | `C:\Sistemas\virtualwallet` |

### Docs por proyecto
- **Agentes-IA** (`docs/<proyecto>/definiciones/*.md`): memoria de cada agente (1-analista-funcional, 2-disenador-funcional, 3-arquitecto-mvc, 4-presupuestador, 5-implementador, 6-qa, 7-documentador).
- **Repo del sistema** (`C:\Sistemas\<proyecto>\docs\`): documentacion tecnica (alcances, scripts SQL, migraciones, manual usuario).

### Items pendientes activos

**vinosefue:**
- Migraciones `AddReversionPedidoYHistorial` + `AddProductosPropiosYStock` pendientes en produccion.
- DEF-003 abierto: boton "Registrar pago" no bloqueado en compra espejo de concesion CerradaManual.

**ShowroomGriffin:**
- V2-V7 (refactor taxonomia Producto/Modelo/Variante) implementados localmente, QA pendiente.
- Scripts SQL V6 generados para produccion — pendiente aplicar.

**ganaderia:**
- 7 etapas completas (build OK), QA funcional pendiente de ejecutar.

---

## Modo de ejecucion de agentes

| # | Agente | Archivo | Modo |
|---|---|---|---|
| 1 | analista-funcional | `1-analista-funcional.md` | Ask |
| 2 | disenador-funcional | `2-disenador-funcional.md` | Ask |
| 3 | arquitecto-mvc | `3-arquitecto-mvc.md` | Ask |
| 4 | presupuestador | `4-presupuestador.md` | Ask |
| 5 | implementador-dotnet | `5-implementador.md` | Agent |
| 6 | qa-mvc | `6-qa.md` | Agent |
| 7 | documentador | `7-documentador.md` | Ask |

- **Ask**: producen contenido textual/decisional sin tocar codigo.
- **Agent**: ejecutan acciones sobre el repo (implementacion y QA funcional).
- **Regla de oro**: no iniciar etapa hasta que la anterior haya cerrado su archivo.

---

## Stack confirmado en todos los proyectos activos

- .NET 10 / EF Core 10.0.2 / ASP.NET Core Identity 10.0.2
- **`MySql.EntityFrameworkCore` v10.0.1** (Oracle) — NO Pomelo (algunas docs internas son incorrectas)
- Serilog.AspNetCore 9.0.0, MailKit 4.14.1, ClosedXML 0.105.0, QuestPDF 2025.12.4

### Estado de .github/copilot-instructions.md por repo

| Repo | Estado |
|---|---|
| blankproject | Completo (canonico) |
| recotrack | Minimo (solo convencion de iconos) |
| ShowroomGriffin | Poblado (2026-05-20) |
| vino-y-se-fue | Creado (2026-05-20) |
| ganaderia | Creado (2026-05-20) |
| virtualwallet | Creado (2026-05-20) |
| delicias-naturales | Ausente (proyecto cerrado, legacy MVC5) |

### Reglas UI mandatorias (no negociables en todos los proyectos)
- **SweetAlert2**: UNICA libreria para alertas, confirmaciones, toasts. Prohibido `alert()`, `confirm()`, toastr.
- **daterangepicker**: UNICO componente para rangos de fechas. Prohibido dos `<input type="date">` separados.
- **DataTables**: TODAS las tablas de listado deben ser DataTables. Prohibidas tablas Bootstrap estaticas para datos.

### Bug conocido del template base
`GlobalExceptionHandler` registrado con `AddExceptionHandler<>` falla en runtime cuando inyecta `IErrorNotifier` (scoped) porque lo registra como singleton. Fix:
```csharp
builder.Services.AddScoped<IExceptionHandler, GlobalExceptionHandler>();
```
Corregido en ganaderia (Etapa 1). Aplicar en todos los proyectos nuevos.

---

## Patrones de implementacion cross-proyecto

### RowVersion / concurrencia optimista
- `RowVersion` como `byte[]` con `IsRowVersion()` en EF Core (`MySql.EntityFrameworkCore` — Oracle, NO Pomelo).
- Aplicado en: `VarianteProducto` (ShowroomGriffin), `ProductoPropio` + `Pedido` (vinosefue).

### Comprobantes / adjuntos fuera de wwwroot
- Path en appsettings: `App:ComprobantesPath`. Descarga via endpoint `[Authorize]`.
- Aplicado en: ganaderia (EgresosController), vinosefue.

### Numerador / correlativo secuencial
- Tabla `ContadorXxx` (Id=1, UltimoNumero) + UPDATE en misma transaccion + UNIQUE index como red de seguridad.
- Aplicado en: ganaderia (`ContadorFactura` → F-NNNNNN), vinosefue (CON-###### concesiones).

### Migraciones no destructivas
- Renombrar tablas: `RENAME TABLE` + `UPDATE` + data migration — NO DROP+CREATE.
- `Down()` no reversible: lanzar `NotSupportedException`.
- Aplicado en: ganaderia (`RenameFacturaToFacturaVenta`).

### Regularizacion de cuotas
- **ErrorDeCarga**: restaurar movimiento original (DeletedAt=null), cuota → Acreditada.
- **CobroPosterior**: restaurar original a Pendiente + crear nuevo movimiento Acreditado con fecha real.
- Aplicado en: ganaderia.

### Reversiones de pedidos (compensaciones contables)
- Compensaciones via `MovimientoCC` prefijadas con `[Reversion]` — no borrar el original.
- Historial de estados en `HistorialEstadoPedido`. `RowVersion` en `Pedido` para concurrencia.
- Aplicado en: vinosefue.

### Deploy a hosting compartido (IIS sin CLI)
- Generar scripts SQL manuales idempotentes. Guardar en `docs/<proyecto>/migraciones/` o `scripts/`.
- Aplicado en: vinosefue, ShowroomGriffin (V6).

### Dual-origen en items de pedido
- `PedidoItem.EsStockPropio` flag + `ProductoPropioId` opcional. Items propios reservan stock FIFO; items de proveedor generan compra.
- Aplicado en: vinosefue.

### Deduplicacion de importaciones
- Persistir `DescripcionOriginal` (linea cruda del archivo fuente) como clave de deduplicacion en re-importacion.
- Aplicado en: virtualwallet (resumenes TC Mastercard/Visa — `ProvinciaMastercardResumenParser`, `ProvinciaVisaResumenParser`).

---

## Calibracion del presupuestador

- Bandas observadas: ABM simple 2-4h, ABM medio 5-7h, ABM complejo 10-15h.
- Normalizar tiempos reales a base sin contingencia: `real / 1.30` para evitar doble contingencia.
- Protocolo de autocorreccion pre-cierre: ratio por item (0.85–1.15 banda neutra); cierre en dos pasos (preliminar → ajustado).

### Cierres historicos
| Proyecto | Estimado | Real | Desvio | Causa |
|---|---|---|---|---|
| ShowroomGriffin (11 modulos) | 101,1 h (PERT) | 25 h | -75,2% | Sobreestimacion M y P; 2,3 h/modulo real |
| ganaderia (7 etapas) | — | — | — | Ver `docs/ganaderia/definiciones/4-presupuestador.md` |

**Accion correctiva ShowroomGriffin**: reducir rangos M y P en PERT para proyectos ABM+workflow MVC similares. Base real ≈ 2,3 h/modulo.