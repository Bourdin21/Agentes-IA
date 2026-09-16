# Memoria - Arquitecto MVC

## Proyecto: libreria-horizonte
## Ultima actualizacion: 2026-09-15

## Definiciones vigentes

### Research de integraciones (2026-09-15)
**Fixed (fixed.uy)**
- Unica API publica: **API de Facturacion Electronica** (REST JSON, Swagger, sandbox, API Keys desde acceso.fixed.uy/accesoAPI). Documentada para emitir CFE ante DGI ("Ventas"). La pagina declara textual: **"No incluye control de stock"**.
- Es un **plan aparte**: $ 1.480/mes (pesos, segun la pagina; $ 966 con beneficio), hasta 30.000 facturas/mes.
- Planes de la web: 50 comprobantes, Basico Ilimitado ($ 980/mes), **con Control de Stock** ($ 2.140/mes, FIFO), API. Integraciones listadas: solo POS (Fiserv, Getnet, OCA, Scanntech, Totalnet). **Sin integracion con MercadoLibre ni e-commerce.**
- No se pudo leer el Swagger (se renderiza por JavaScript) ni confirmar exportacion de stock a Excel en fuentes publicas.
- **Conclusion: no hay forma de conectarse por API al stock de Fixed.** El stock entra por export manual del panel (a confirmar con el cliente/soporte@fixed.uy). Queda descartada la variante "Fixed por API".

**MercadoLibre (API oficial, misma plataforma para MLU)**
- Autenticacion OAuth 2.0 de vendedor: app creada en Developers con redirect URI; access token 6 h; **refresh token de un solo uso, vence a los 6 meses** (solo vale el ultimo emitido).
- Leer el catalogo completo: `GET /users/{user_id}/items/search` (limit max 100; para mas de 1.000 resultados `search_type=scan` + `scroll_id` hasta recibir null; filtro por status) + multiget `GET /items?ids=...` (**max 20 ids por llamada**).
- Modificar: `PUT /items/{id}` con `available_quantity` y/o `status`. **Stock 0 → la publicacion queda pausada (sub_status out_of_stock) y se reactiva sola al cargar stock > 0**; pausada por falta de stock no se puede activar manualmente. (La doc lista el auto-reactivado para MLB, MLA, MLM, MLC, MPE, MLV — **MLU no figura explicitamente, verificar con la cuenta real**.)
- **User Products** (precio/stock por variante): rollout gradual en Uruguay desde enero 2025; publicaciones simples se migran solas. Stock con multi-origen se actualiza en `PUT /user-products/{id}/stock/type/seller_warehouse`. Hay que leer `user_product_id` de cada item y respetar la estructura nueva si la cuenta esta migrada.
- Limite: **1.500 requests/minuto por vendedor**; 429 / local_rate_limited → reintento con backoff exponencial + jitter.
- Notificaciones disponibles: `orders_v2` (ventas confirmadas) e `items` (cambios en publicaciones).
- Volumen estimado: leer 67.534 items ≈ 676 paginas de scan + ≈ 3.377 multigets ≈ 4.000 llamadas (minutos, espaciado). Modificar N publicaciones = N PUT (30.000 cambios ≈ 20-40 min al limite, horas con margen).
- **Conclusion: se puede sincronizar stock y estado del catalogo por API.** Reemplaza al Excel masivo tambien en el Paso 1 (mas confiable, sin limite de filas por archivo, verificable item por item).

### Resultado del escaneo de reutilizacion
| Componente | Origen | Grado de reuso |
|---|---|---|
| Lectura de Excel por nombre de columna (ClosedXML) + reporte de excepciones | PAT-012 — koi `ImportacionExcelKoiService.cs` | **Literal** (adaptable) |
| Herramienta de consola .NET para proceso unico | PAT-012 — la-platense `tools/ImportarHistorico/Program.cs` | **Literal** (estructura) |
| Preview → confirmar con staging por token | PAT-012 — koi `ImportacionInicialController` | **Literal** (adaptable) |
| Cache de token de API externa con vigencia del servidor | PAT-024 — koi `AyresTokenCache.cs` | **Literal**; se extiende con refresh token rotativo de ML |
| Cola de trabajo en segundo plano con scope propio | PAT-025 (koi) | **Literal** |
| Maquina de estados | PAT-005 | Patron de diseño |
| DataTables server-side + filtro por columna | PAT-008 | **Literal** |
| Data Protection persistente (keyring) | vinosefue/ganaderia/marihogar | **Literal** (obligatorio: guarda el refresh token) |
| Motor de cruce en cascada ISBN → SKU → titulo aproximado → IA | ninguno | **Nuevo** → PAT-036 |
| Cliente MercadoLibre con OAuth de vendedor, scan/multiget y PUT de items | ninguno (century-21 solo busqueda publica) | **Nuevo** |

### Decision de stack
- **Paso 1:** consola .NET 10 (`tools/LimpiezaCatalogo`) en la maquina del estudio + biblioteca `Horizonte.Matching` + `Horizonte.MercadoLibre` (cliente API), ambas reutilizadas literal en el Paso 2.
- **Paso 2:** ASP.NET Core MVC .NET 10 + EF Core + MySQL sobre BlankProject, hosting SmarterASP (asignacion a validar con `olvidata-infra`).
- `olvidata-agentes-multirubro` evaluado como host y descartado por ahora (no esta en produccion).

### Componentes por capa
**Biblioteca `Horizonte.Matching`** (Paso 1 y 2)
- `NormalizadorIsbn`, `NormalizadorTitulo`, `MotorCruce` (cascada, FuzzySharp con umbral), `ClasificadorIA` (residuo por Message Batches, solo propone), `CalculadorDiferencias` (stock Fixed + estado ML + vinculos + "a pedido" → cambios).

**Biblioteca `Horizonte.MercadoLibre`** (Paso 1 y 2)
- `MercadoLibreAuth`: intercambio de code, refresh rotativo, persistencia cifrada del ultimo refresh token.
- `MercadoLibreClient`: `ListarItemsVendedor` (scan + scroll_id), `ObtenerItems` (multiget de a 20), `ActualizarStock` (items o user-products segun la cuenta), `Pausar`, `ListarOrdenes`.
- `LimitadorTasa` (token bucket ~1.000 req/min, margen bajo el tope de 1.500) + reintento con backoff exponencial y jitter ante 429.

**Paso 1 — `tools/LimpiezaCatalogo`**
- `ExportFixedReader` (ClosedXML, por nombre de columna).
- `SnapshotCatalogo`: baja las 67.534 publicaciones por API a un archivo local (reanudable).
- `AplicadorCambios`: aplica pausas/ajustes por API con checkpoint (reanudable si se corta) y log por item; modo simulacion obligatorio antes de escribir.
- `GeneradorReporte`: Excel de resultados + resumen al cliente + listado de libros sin publicar.
- Autorizacion del vendedor una sola vez (URL de autorizacion + code pegado en la consola).

**Paso 2 — sistema web**
- Domain: `ConexionMercadoLibre`, `ImportacionFixed`, `ArticuloFixed`, `PublicacionMercadoLibre`, `Vinculo`, `LoteCambios`, `CambioPublicacion`, `VentaMercadoLibre`; enums `EstadoLote`, `TipoCambio`, `EstadoCambio`, `MetodoCruce`, `EstadoVenta`.
- Application: `IImportacionFixedService`, `ILoteCambiosService`, `IVentasMercadoLibreService`, `IVinculosService`; DTOs de preview/lote/venta.
- Infrastructure: `Horizonte.MercadoLibre` + `AplicadorLotesWorker` (PAT-025) + `SincronizadorVentasWorker` (consulta de ordenes cada N minutos; notificaciones `orders_v2` quedan como mejora — sin cierre real de referencia para webhooks) + repositorios EF.
- Web: `InicioController`, `ImportacionController`, `LotesController`, `SinCruzarController`, `VentasController`, `ConexionController` (callback OAuth). Controllers solo coordinan.

### Entidades y configuraciones EF
- `ArticuloFixed` (CodigoFixed unico, Isbn13 indexado, Descripcion, Stock, ImportacionId).
- `PublicacionMercadoLibre` (ItemId unico, UserProductId, Titulo, Sku, Isbn13 indexado, Estado, SubEstado, Cantidad, AProPedido).
- `Vinculo` (PublicacionId unico, ArticuloFixedId, Metodo, Confianza, EsManual).
- `LoteCambios` (Estado, UsuarioId, fechas, RowVersion manual PAT-004) 1-N `CambioPublicacion` (Tipo, antes/despues, Estado, Motivo).
- `VentaMercadoLibre` (OrderId+ItemId unico, Cantidad, Estado, MarcadaPor, MarcadaEn).
- `ConexionMercadoLibre` (UserIdMl, RefreshTokenCifrado, EmitidoEn, VenceEn).
- 8 tablas de negocio.

### Migraciones requeridas
- Paso 1: ninguna.
- Paso 2: migracion inicial `InicialSincronizacion`.

### Modelo de permisos
- Rol `Operador` (libreria) + superusuario interno del estudio (no se documenta al cliente). Sin portal de usuario final (no aplica IDOR).

### Riesgos tecnicos activos
- R-01 **Alto — Fixed sin API de stock (CONFIRMADO):** el stock entra solo por export manual. Si el plan del cliente no exporta stock a Excel, no hay Paso 1 ni Paso 2 → confirmar antes de firmar.
- R-02 **Alto — habilitacion de acceso ML:** app en Developers, autorizacion del vendedor, redirect URI. Refresh token de un solo uso: si dos procesos refrescan a la vez, se pierde la conexion → un unico dueño del refresh (lock) y persistencia inmediata.
- R-03 **Medio — User Products en MLU:** la cuenta puede estar migrada; el stock se actualiza distinto. Detectar por item (`user_product_id`) y usar el endpoint que corresponda.
- R-04 **Medio — auto-reactivacion con stock en MLU no documentada explicitamente:** verificar con 3 publicaciones de prueba antes de la corrida masiva; si no reactiva sola, activar con `status=active` explicito.
- R-05 **Medio — calidad del cruce:** revision + aprobacion + pausar es reversible.
- R-06 **Medio — variantes:** stock por variante fuera de alcance hasta confirmar.
- R-07 **Bajo — rate limit:** limitador + backoff; corridas reanudables.
- R-08 **Bajo — costo IA del residuo:** solo residuo, avisar antes si es grande.
- R-09 **Bajo — vencimiento de conexion:** refresh a los 6 meses sin uso; el panel avisa y pide reconectar.

### Gate para Presupuesto
- Integracion por API con ML confirmada viable; Fixed por API descartado. Gatillos de reestimacion: Fixed no exporta stock, cuenta con variantes, mas de una cuenta ML.

## Historial de ajustes
- 2026-09-15: Arquitectura inicial: consola .NET + biblioteca de cruce compartida (Paso 1), MVC .NET 10 con cliente OAuth de ML y workers (Paso 2); multirubro evaluado y descartado por ahora.
- 2026-09-15: Research de integraciones: Fixed sin API de stock (solo facturacion, plan aparte); ML API viable para leer catalogo y sincronizar stock/estado. Paso 1 pasa de Excel masivo a API; se agrega biblioteca `Horizonte.MercadoLibre` compartida.
