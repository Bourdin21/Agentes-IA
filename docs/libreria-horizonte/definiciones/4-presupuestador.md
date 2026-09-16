# Memoria - Presupuestador

## Proyecto: libreria-horizonte
## Ultima actualizacion: 2026-09-15

## Definiciones vigentes

### Encuadre comercial
- Mismo alcance cotizable de dos formas; Joaquin elige:
  - **Opcion A — Build (recomendada):** Etapa 1 limpieza + Etapa 2 sistema de sincronizacion, formula Build, mantenimiento por tablas con año 1 gratis.
  - **Opcion B — AI Agents:** Paso 1 como servicio unico (formula Build) + Paso 2 como AI Agents Intermedio (catalogo promo hasta 2026-12-31).
- Integraciones confirmadas por research (ver `3-arquitecto-mvc.md`): **MercadoLibre por API: si** (incluida en ambas etapas). **Fixed por API: no existe para stock** → variante "Fixed por API / AI Agents Avanzado" eliminada.
- Paso 0.5 (perfil): `olvidata-ceo` consultado → sin descuento agresivo. Igual no dispara tier (ver R y volumen abajo).

### WBS y PERT — Etapa 1: Limpieza del catalogo (conectada por API a ML)
| Item | Tipo | Referencia (Paso 0) | O | M | P | PERT | Riesgo | Cont. | Horas finales | USD lista (M x 10.50) |
|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|
| 1.1 Lectura y normalizacion del export de Fixed | Parser Excel | Parser Excel propietario 4-6 h | 3 | 4 | 6 | 4.17 | Medio | 15% | 4.79 | 42.00 |
| 1.2 Motor de cruce en cascada | Logica compleja | Logica compleja 5-8 h | 6 | 8 | 12 | 8.33 | Alto | 25% | 10.42 | 84.00 |
| 1.3 Revision asistida del residuo (IA + planilla) | Logica compleja | Sin referencia | 2.6 | 4 | 7 | 4.27 | Alto | 25% | 5.33 | 42.00 |
| 1.4 Reporte + listado de libros sin publicar | Reporte | Nuevo reporte 1-2 h | 1.3 | 2 | 3.6 | 2.15 | Medio | 15% | 2.47 | 21.00 |
| 1.5 Aplicacion de pausas/ajustes por API (simulacion, checkpoint, verificacion) | Integracion (escritura) | Sin referencia directa | 2 | 3 | 5 | 3.17 | Alto | 25% | 3.96 | 31.50 |
| 1.6 Habilitacion de datos de Fixed (export, iteraciones) | Riesgo de acceso | Leccion KOI/Ayres | 1.3 | 2 | 3.6 | 2.15 | Alto | 25% | 2.69 | 21.00 |
| 1.7 Conexion OAuth ML + lectura del catalogo completo (scan + multiget, User Products) | Integracion REST | REST documentada 3-5 h (KOI/Ayres, PAT-024) | 3 | 4 | 6 | 4.17 | Alto | 25% | 5.21 | 42.00 |
| 1.8 Habilitacion de acceso ML (app + autorizacion del vendedor) | Riesgo de acceso | Leccion KOI/Ayres | 1 | 1.5 | 2.7 | 1.62 | Alto | 25% | 2.02 | 15.75 |
| **Total Etapa 1** | | | | **28.5** | | **30.03** | | | **36.89** | **299.25** |

### Autocorreccion por item (Etapa 1)
| Item | Referencia | Ratio M/mediana | Decision | Motivo |
|---|---|---:|---|---|
| 1.1 | Parser Excel (5) | 0.80 | Mantener | Export plano; lectura por columna reutiliza PAT-012 |
| 1.2 | Logica compleja (6.5) | 1.23 | Justificado | 67.534 filas, ISBN no garantizado, ajuste de umbral con datos reales |
| 1.3 | — | — | Rango | Residuo de tamaño desconocido |
| 1.4 | Nuevo reporte (1.5) | 1.33 | Justificado | Reporte al cliente + listado sin publicar (ya no genera archivos de edicion masiva) |
| 1.5 | — | — | Mantener | Escritura sobre publicaciones reales: modo simulacion, reanudable, muestreo |
| 1.6 / 1.8 | — | — | Mantener | Items de acceso separados por regla de integraciones |
| 1.7 | REST documentada (4) | 1.00 | Mantener | Scan + multiget + deteccion de User Products; token cache reutiliza PAT-024 |

### Etapa 2: Sistema de sincronizacion diaria (M para ambas opciones)
| Item | M | Referencia |
|---|---:|---|
| 2.1 Conexion ML desde la web (callback OAuth, refresh con lock, aviso de vencimiento) — reusa `Horizonte.MercadoLibre` | 1 | Reuso literal de 1.7 |
| 2.2 Importacion diaria del export de Fixed con preview (PAT-012) | 2 | Reuso |
| 2.3 Diferencias (reusa motor de Etapa 1) | 1.5 | Reuso literal |
| 2.4 Lote aprobable + aplicacion en segundo plano (PAT-005/025, reusa aplicador de 1.5) | 3 | Workflow 4-6, bajado por reuso |
| 2.5 Ventas de ML → pendientes a descontar en Fixed | 2 | ABM simple-intermedio |
| 2.6 Bandeja sin cruzar / vinculo manual / "a pedido" | 2 | ABM simple |
| 2.7 Panel, historial, usuarios (BlankProject) | 2 | Reuso baseline |
| 2.8 Deploy inicial hosting | 3 | Deploy inicial hosting compartido 2-3 |
| **Total Etapa 2** | **16.5** | USD lista 173.25 |

### Sanity check del total
- M total 45 h (Etapa 1 28.5 + Etapa 2 16.5). Comparable: Ganaderia (8 modulos, 20 h reales) — alcance menor en pantallas pero con 2 integraciones de datos; contadores-bma-conversor (parser + proceso, M 11 h) para la Etapa 1. Dentro de rango para 2 etapas con integracion.
- Horas facturables internas: 45 / 4.0 x 1.20 = 13.5 h.

### Opcion A — Build (recomendada)
| Etapa | Area (cliente) | Items | M | USD lista | USD al cliente (x1.25) |
|---|---|---|---:|---:|---:|
| 1 | Conexion con MercadoLibre y lectura del catalogo | 1.7, 1.8 | 5.5 | 57.75 | **72** |
| 1 | Cruce, limpieza y reporte del catalogo | 1.1-1.6 | 23 | 241.50 | **302** |
| 2 | Actualizacion diaria desde Fixed y aplicacion en ML | 2.1-2.4 | 7.5 | 78.75 | **98** |
| 2 | Ventas de MercadoLibre para descontar en Fixed | 2.5 | 2 | 21.00 | **26** |
| 2 | Libros sin cruzar y vinculos manuales | 2.6 | 2 | 21.00 | **26** |
| 2 | Panel, usuarios y puesta en produccion | 2.7, 2.8 | 5 | 52.50 | **66** |
| | **Total** | | **45** | **472.50** | **590** |

- Subtotal Etapa 1: **USD 374** · Subtotal Etapa 2: **USD 216** · Total desarrollo: **USD 590** (lista 472.50 + Tokens IA 118.13 = 590.63; redondeo −0.63 repartido por area).
- R = (1.1: 4 + 1.7: 4 + 2.1: 1 + 2.2: 2 + 2.3: 1.5 + 2.4: 3 + 2.7: 2) / 45 = 17.5 / 45 = **39% → Tier 3 (0%)**. Volumen lista 472.50 < 600 → **V0 (0%)**. Sin descuento. Piso USD 280 no aplica. Dentro del rango Build USD 400-1.000.
- Mantenimiento: 8 tablas → **PRO USD 400/año, año 1 gratis**. Solo si se hace la Etapa 2.
- Etapa 1 sola (sin Etapa 2): USD 374, sin mantenimiento.

### Opcion B — AI Agents
- Paso 1 (servicio unico, formula Build): **USD 374** (= Etapa 1 de la opcion A).
- Paso 2: **AI Agents Intermedio** (2-3 pasos, 1 integracion externa por API: MercadoLibre) setup **USD 800** (techo del rango 600-800 por volumen 67k + aprobacion humana + doble direccion) + **USD 650/año**. Control de costo por formula: Etapa 2 USD 216 → el setup cubre 3.7x.
- Variante Avanzado (Fixed por API) **eliminada**: Fixed no expone stock.
- Recurrente sin "año 1 gratis" (regla de Build, no definida en AI Agents) — pendiente Joaquin.

### Comparacion para el cliente a 5 años
- Opcion A Build: 590 + 4 x 400 = **USD 2.190**. Recurrente al estudio USD 400/año.
- Opcion B AI Agents: 374 + 800 + 5 x 650 = **USD 4.424**. Recurrente al estudio USD 650/año.

### Costo interno de IA (solo estudio, nunca al cliente)
- 13.5 h facturables x USD 4/h = USD 54 → 11.4% de lista (umbral 15%) → **sin ajuste**.
- Gasto real por API del residuo (Message Batches): USD 10-75 segun 1.000-10.000 casos, cubierto por Tokens IA (USD 118). Si el residuo supera ~10.000, avisar a Joaquin antes de correrlo.
- Llamadas a la API de MercadoLibre: sin costo.
- Overhead Ask-mode: 4 h x USD 1 = USD 4.

### Tasa vigente y contingencia aplicada
- USD 35/h, formula Build M x $10.50 (factor 4.0). Contingencia 15%/25% por item solo en horas PERT internas.

### Riesgos y supuestos del presupuesto
- Bloqueante: Fixed exporta stock a Excel (no hay API de stock, confirmado).
- Supone 1 cuenta ML y publicaciones sin variantes; supone que la cuenta permite crear la app y autorizarla.
- Gatillos de reestimacion: variantes / User Products con multi-origen; residuo > 10.000 casos; mas de una cuenta ML; auto-reactivacion con stock no disponible en MLU (+ ajuste menor en 1.5).

### Pruebas minimas requeridas
- Etapa 1: categorias = total de publicaciones leidas; corrida en simulacion antes de escribir; 3 publicaciones de prueba (pausa por stock 0 y reactivacion); muestra de 30 verificada; cero eliminaciones.
- Etapa 2: aprobar/aplicar/reintentar lote; refresh token rotativo y reconexion; venta unica en pendientes; vinculo manual persistente; "a pedido" nunca se pausa.

### Calibraciones historicas usadas
- contadores-bma-conversor (parser Excel), KOI/Ayres (integracion REST + habilitacion de acceso), Ganaderia (total), rangos 27-presupuesto-parametros vigentes 2026-09-08.

### Cierre estimado vs real (si disponible)
- Pendiente (sin implementacion).

## Historial de ajustes
- 2026-09-15: Presupuesto inicial: Paso 1 USD 300 (formula Build, Excel masivo), Paso 2 AI Agents Intermedio USD 800 + 650/año (condicional Avanzado 1.200 + 1.000/año). Sin descuento.
- 2026-09-15: Alternativa todo como Build: USD 590 (300 + 290) + PRO USD 400/año con año 1 gratis. Pedido de Joaquin.
- 2026-09-15: Research de integraciones incorporado: ML por API en Etapa 1 (+1.7/1.8, sin archivos de edicion masiva), Fixed por API descartado (variante Avanzado eliminada). Build se mantiene en USD 590 con nuevo reparto (Etapa 1 374 / Etapa 2 216); AI Agents pasa a 374 + 800 + 650/año.
