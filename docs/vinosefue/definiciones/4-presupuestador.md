# Memoria - Presupuestador

## Proyecto: vinosefue
## Ultima actualizacion: 2025-07-01

## Datos de cierre reales

- Sistema: Gestion Comercial de Vinos VinoSeFue
- Modulos funcionales: 16
- Stack: Clean Architecture, .NET 10, MySQL
- Horas reales totales: 30 h
- Costo total real: USD 420
- Tasa efectiva: USD 14 / hora
- Fecha de cierre: Julio 2025
- Estado: cerrado y validado

## Perfil tecnico

- Maquinas de estado: Pedidos + CompraProveedor
- Flujo de concesiones con ajuste de cuenta corriente
- Importacion automatica de catalogo: HTML / PDF / CSV con Background Worker
- Ledger de movimientos
- Migraciones EF: 6
- Entidades de dominio: 17
- Servicios: 13
- Vistas: 40

## Valor como referencia de calibracion

- Referencia para: proyectos con maquinas de estado, workflows, integraciones de importacion
- Horas promedio por modulo: 30 / 16 = ~1.87 h/modulo (base, sin contingencia)
- Alta complejidad por modulo pero total acotado por equipo experimentado
- Confirma tasa USD 14/h como solida

## Cierre de calibracion — Sprint "Compras al proveedor: armado manual y cuenta corriente" (2026-07-03)

**Contexto:** este sprint NO paso por la etapa formal de Presupuesto (el cliente decidio implementar directamente tras Arquitectura). Este cierre es una reconstruccion retroactiva del PERT que se hubiese usado, solo para fines de calibracion — no fue el numero cobrado (no se cobro nada, es el mismo cliente/owner del estudio).

**Real reportado por el cliente:** 4 h reales totales para todo el lote (5 items originales + 2 rondas de ajuste post-QA + simplificacion de 2 reportes). El cliente dio el numero como total agregado, sin desglose por item — el reparto por item de abajo es una **aproximacion proporcional no confirmada** (marcada como hipotesis), util solo para calibrar tipos de modulo; el dato solido es el TOTAL (28.27 h estimadas vs 4 h reales).

### Reconstruccion PERT retroactiva por item

| # | Item | Tipo | Anclaje historico (Paso 0) | O | M | P | PERT | Riesgo | Final (h) |
|---|---|---|---|---:|---:|---:|---:|---|---:|
| 1 | Fix stock propio en Compras/Detalle | Ajuste puntual | Rango 0.5-1h | 0.35 | 0.5 | 0.8 | 0.53 | Bajo +8% | 0.57 |
| 2 | Fix orden columna Fecha | Ajuste puntual (solo vista) | Rango 0.5-1h | 0.2 | 0.3 | 0.5 | 0.32 | Bajo +8% | 0.34 |
| 3 | Compra manual por item + desacople total de estados | ABM complejo / workflow (refactor FK Pedido→PedidoItem, nueva pantalla, 2 migraciones) | Ganaderia (modulo financiero+workflow, mediana ~10h base/modulo) | 6 | 9 | 15 | 9.5 | Medio +15% (migracion + multiples modulos acoplados) | 10.93 |
| 4 | Cuenta corriente unica del proveedor (ledger nuevo) | Modulo financiero (5-8h), ajustado a la baja por reutilizacion real del patron ya existente (CuentaCorriente/MovimientoCC de Cliente) | Ganaderia + patron Cliente ya resuelto | 4 | 6 | 10 | 6.33 | Medio +15% (dato financiero + migracion) | 7.28 |
| 5 | Pagos y Notas de Credito manuales del proveedor | ABM intermedio, reutiliza AdjuntoService/MetodoPago existentes | Rango 4-7h, ajustado a la baja por reutilizacion | 3 | 4 | 6.5 | 4.25 | Bajo +8% (CRUD sobre patron probado) | 4.59 |
| 6 | Fix item huerfano al cancelar/eliminar pedido + recalculo costo | Regla de negocio sobre modulo existente | "Agregar regla de negocio: M~1-2h" | 1 | 1.5 | 2.5 | 1.58 | Bajo +8% | 1.71 |
| 7 | Simplificacion Reportes/DeudaProveedor + Reportes/Riesgo | Modificacion de reporte existente (x2) | "Nuevo reporte: M~1-2h", ajustado al alza por tocar 2 reportes a la vez | 1.3 | 2 | 3.3 | 2.10 | Bajo +8% | 2.27 |
| 8 | 2 auto-fixes de QA (VSF-001, VSF-002) | Ajuste puntual x2 | Rango 0.5-1h | 0.35 | 0.5 | 0.9 | 0.54 | Bajo +8% | 0.59 |

**Paso A (preliminar):** suma = **28.27 h** (PERT + contingencia, sin doble contingencia).
**Sanity check total (Paso 8):** comparado contra Ganaderia (20 h reales / 8 modulos financiero+workflow, el comparable mas cercano), ratio 28.27/20 = 1.41x — coherente con que este lote tiene 1 item de complejidad equivalente a un modulo completo de Ganaderia (item 3) mas 7 items adicionales menores. No amerita ajuste adicional.
**Paso B (final):** se mantiene 28.27 h (sin cambios respecto a Paso A).

**M total (para formula de facturacion, sin O/P):** 0.5+0.3+9+6+4+1.5+2+0.5(prom. autofixes) = **23.8 h**.
Horas facturables (M/2.5×1.20) = 11.42 h → Costo formula vigente = 11.42 × $35 = **USD 400** (nunca cobrado — referencia interna).

### Comparacion estimado vs real

| Metrica | Valor |
|---|---:|
| Horas PERT+contingencia (Paso B) | 28.27 h |
| Horas real | 4 h |
| **Ratio PERT-contingencia/real** | **7.07x — nuevo record del dataset** (supera a Ganaderia 5.05x y ShowroomGriffin 4.0x) |
| Horas formula vigente (M/2.5×1.20) | 11.42 h |
| **Ratio formula/real** | **2.86x — tambien nuevo record** (supera a Ganaderia 1.93x) |
| Costo formula (nunca cobrado) | USD 400 |
| Costo a real×$35/h (referencia) | USD 140 |

### Reparto proporcional por item (hipotesis, NO confirmada por el cliente)

Si se reparte el total real (4h) proporcionalmente al peso de cada item en el M estimado: item 3 ≈1.8h, item 4 ≈1.0h, item 5 ≈0.5h, items 1+2+6+7+8 ≈0.7h combinados. **Esto es una estimacion de reparto, no un dato medido** — si el cliente confirma horas reales por item en el futuro, reemplazar esta fila.

### Lecciones aprendidas y acciones de recalibracion

1. **Nuevo record de eficiencia IA en el dataset** (7.07x PERT/real, 2.86x formula/real). Refuerza — sin cambiarlo unilateralmente (politica vigente: factor 2.5 fijo hasta cierre de Energy Nutrition) — la evidencia a favor de subir el factor de eficiencia por encima de 2.5.
2. **Distincion de granularidad clave:** este lote es una **iteracion evolutiva sobre un sistema ya entregado** (reutiliza patrones ya resueltos: `CuentaCorriente`/`MovimientoCC` de Cliente, `AdjuntoService`, `MetodoPago`), no un modulo nuevo desde cero. Anclar este tipo de trabajo en los rangos de "Modulo nuevo" (ABM complejo 7.7-11.5h, Financiero 5-8h) sobreestima sistematicamente — la seccion "Modificacion sobre modulo existente" de `27-presupuesto-parametros.instructions.md` es el ancla correcta, y se le agregaron 2 filas nuevas a partir de este cierre (ver ese archivo).
3. Los 2 "fixes" simples (items 1 y 2) confirmaron el piso del rango "Ajuste puntual" (0.5-1h) — sin sorpresas ahi.
4. Los 2 fixes post-QA (item 6) y la simplificacion de 2 reportes (item 7) confirman que "modificar reglas de negocio o reportes sobre un modulo existente" sigue barato (1-2h) incluso cuando toca varias capas, siempre que no haya migracion nueva.

## Cierre de calibracion — Feature "Filtro de categoria al exportar catalogo de Productos" (2026-07-13)

**Real reportado por el cliente:** 1 h 30 min (1.5 h) totales, cubriendo diseño+analisis (identificar que no existia campo de categoria, decidir tabla nueva vs enum), implementacion completa (entidad, migracion, servicio, pantalla admin, modal de exportar) y el deploy de la migracion + script de clasificacion en produccion.

### Reconstruccion PERT retroactiva por item (ancla ya corregida: "iteracion evolutiva", no "modulo nuevo")

| # | Item | Anclaje | M | PERT | Riesgo | Final (h) |
|---|---|---|---:|---:|---|---:|
| 1 | Entidad `CategoriaProducto` + FK nullable + migracion (copia patron de `GrupoProducto`) | Iteracion evolutiva — ledger/entidad reutilizando patron existente (~1-1.5h) | 1.0 | 1.04 | Bajo +8% | 1.12 |
| 2 | Extender `ProductoCatalogoService` (filtro `categoriaIds` + `GetCategoriasAsync`) | Agregar regla de negocio sobre modulo existente (~1-2h, tomado en el piso) | 0.75 | 0.78 | Bajo +8% | 0.85 |
| 3 | Pantalla admin `Productos/Categorias` (tabla + autosave + contador) reutilizando patron de autosave ya construido en Compras/Detalle | ABM simple nuevo, con reutilizacion fuerte | 1.5 | 1.57 | Bajo +8% | 1.69 |
| 4 | Modal de exportar: 4 checkboxes + validacion + JS (copia patron exacto de columnas ya existente) | Ajuste puntual sobre UI existente | 0.5 | 0.53 | Bajo +8% | 0.57 |
| 5 | Script de clasificacion inicial (reglas + verificacion por SELECT antes de UPDATE) | Iteracion evolutiva — script de datos | 1.0 | 1.04 | Bajo +8% | 1.12 |
| 6 | Deploy migracion + script en produccion (incluye backup, hallazgo del seed en `SeedData.cs`, discrepancia 123 vs 134 grupos) | Iteracion evolutiva — deploy con dato real | 1.0 | 1.04 | Medio +15% | 1.20 |

**M total (formula):** 5.75 h. **PERT+contingencia (Paso B):** 6.55 h.

### Comparacion estimado vs real

| Metrica | Valor |
|---|---:|
| Horas PERT+contingencia | 6.55 h |
| Horas reales | 1.5 h |
| Ratio PERT-contingencia/real | **4.37x** |
| Horas formula vigente (M/2.5×1.20) | 2.76 h |
| Ratio formula/real | **1.84x** |

### Lectura: la recalibracion anterior esta funcionando

Este es el **segundo cierre real desde que se corrigio la regla de granularidad** ("iteracion evolutiva vs modulo nuevo", ver cierre del 2026-07-03). Los ratios de este cierre (4.37x / 1.84x) son mas bajos que el cierre anterior (7.07x / 2.86x) — es decir, anclar explicitamente en reutilizacion de patrones desde el arranque de la reconstruccion (en vez de partir de rangos de "modulo nuevo" y corregir despues) ya esta produciendo estimaciones mas ajustadas a la realidad, aunque todavia sobreestiman. Sigue habiendo margen de ajuste a la baja en los rangos de "iteracion evolutiva" (ver `27-presupuesto-parametros.instructions.md`).

## Historial de ajustes
- 2025-07-01: cierre real registrado
- 2026-07-03: cierre de calibracion (reconstruccion retroactiva) del sprint "Compras al proveedor: armado manual y cuenta corriente" — 4h reales vs 28.27h PERT reconstruido, ratio record 7.07x. Ver `27-presupuesto-parametros.instructions.md` para los ajustes de parametros derivados.
- 2026-07-13: cierre de calibracion del feature "Filtro de categoria al exportar catalogo" — 1.5h reales vs 6.55h PERT reconstruido (ya anclado en "iteracion evolutiva"), ratio 4.37x — mas bajo que el cierre anterior, confirma que la recalibracion de granularidad esta reduciendo la sobreestimacion.
