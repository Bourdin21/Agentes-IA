# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-09-15 - olvidata-sales / olvidata-ceo (pre-proyecto)
- Etapa: Discovery (calificacion del lead)
- Cambio: lead del CRM mal clasificado como "Comercio o alquiler de maquinaria" → es libreria. Dolor Fixed ↔ MercadoLibre. Respuestas de calificacion: Fixed plan Basico (stock 1 sucursal), 67.534 publicaciones ML sin saber cuales activas, actualizacion manual.
- Motivo: consultas en paralelo a olvidata-sales (mensaje) y olvidata-ceo (producto/precio). CEO: no reemplazar Fixed; separar limpieza unica de sincronizacion continua; sin descuento agresivo; Fixed solo documenta API de facturacion (CFE/DGI), no de stock.
- Impacto en capas: —
- Riesgos/supuestos: primer cliente fuera de Argentina (cobro en USD, metodo a definir).

### 2026-09-15 - orquestador (analista-funcional)
- Etapa: Discovery + Analisis
- Cambio: alcance en dos pasos (limpieza unica + sincronizacion diaria), 9 casos de uso, 9 criterios de aceptacion, 6 reglas (nunca borrar, nunca escribir en Fixed, cruce en cascada, sin cruzar no se pausa, aprobacion humana, solo stock/estado), 4 preguntas abiertas con variantes.
- Motivo: pedido de Joaquin ("analizar problema, diseñar solucion, armar presupuesto").
- Impacto en capas: Negocio (motor de cruce), Datos (Paso 2), Presentacion (panel Paso 2).
- Riesgos/supuestos: S-01 export de stock de Fixed (bloqueante), S-03 una cuenta ML, S-04 stock real << publicaciones.

### 2026-09-15 - orquestador (disenador-funcional)
- Etapa: Diseno
- Cambio: flujo de servicio del Paso 1 (sin UI), 6 historias y 6 pantallas del Paso 2, maquina de estados del lote de cambios. Reutiliza PAT-012/005/008; concepto de PAT-032/034. Nuevo PAT-036 en catalogo.
- Motivo: gate de Analisis cerrado en la misma corrida por pedido explicito de las tres etapas.
- Impacto en capas: Presentacion (P1-P6), Negocio (estados, reglas "a pedido").
- Riesgos/supuestos: publicaciones con variantes fuera de alcance; reserva de seguridad de stock sin definir.

### 2026-09-15 - orquestador (arquitecto-mvc)
- Etapa: Arquitectura
- Cambio: consola .NET 10 + biblioteca `Horizonte.Matching` compartida; Paso 2 en MVC .NET 10/MySQL con cliente OAuth de ML, token cache (PAT-024) y workers (PAT-025). 8 tablas, migracion inicial solo en Paso 2. olvidata-agentes-multirubro evaluado como host y descartado por ahora (no esta en produccion).
- Motivo: escribir el motor una vez y reutilizarlo literal en el Paso 2.
- Impacto en capas: Domain/Application/Infrastructure/Web (Paso 2); sin base en Paso 1.
- Riesgos/supuestos: R-01 Fixed sin API, R-02 habilitacion de acceso ML (MLU), R-03 limites de ML no verificados.

### 2026-09-15 - orquestador (presupuestador)
- Etapa: Presupuesto
- Cambio: Paso 1 USD 300 (formula Build: M 23 h, lista 241.50 + Tokens IA; Tier 3/V0 sin descuento). Paso 2 AI Agents Intermedio setup USD 800 + USD 650/año (promo hasta 2026-12-31); condicional Avanzado USD 1.200 + 1.000/año si Fixed tiene API de stock.
- Motivo: Paso 1 sin fila de catalogo → formula; Paso 2 encaja en el frente AI Agents vigente.
- Impacto en capas: —
- Riesgos/supuestos: Paso 1 queda debajo del orientativo 400-700 del CEO; año 1 gratis no aplicado al recurrente AI Agents; metodo de cobro UY pendiente. **Gate cliente pendiente** (no iniciar Implementacion).

### 2026-09-15 - orquestador (presupuestador)
- Etapa: Presupuesto
- Cambio: alternativa B cotizada como Build: USD 590 (Etapa 1 limpieza USD 300 + Etapa 2 sincronizacion USD 290) + mantenimiento PRO USD 400/año con año 1 gratis. R 30% (Tier 3), V0, sin descuento. Variante con API de Fixed USD 642.
- Motivo: Joaquin pidio presupuestar el mismo alcance con el servicio Build en lugar de AI Agents.
- Impacto en capas: — (mismo WBS y arquitectura)
- Riesgos/supuestos: a 5 años el cliente paga USD 2.190 (Build) vs USD 4.350 (AI Agents); el estudio resigna USD 250/año de recurrente. Opcion comercial a elegir por Joaquin.

### 2026-09-15 - orquestador (arquitecto-mvc + presupuestador)
- Etapa: Arquitectura + Presupuesto
- Cambio: research de integraciones. Fixed: unica API = facturacion electronica (CFE/DGI), plan aparte ($ 1.480/mes), declara "No incluye control de stock"; sin integracion con ML/e-commerce → Fixed por API descartado. MercadoLibre: OAuth de vendedor (refresh token de un uso, 6 meses), scan + multiget (20 ids), PUT de available_quantity/status, stock 0 pausa y reactiva solo (MLU sin confirmar explicito), User Products en Uruguay desde 2025, 1.500 req/min, notificaciones orders_v2/items → viable. Etapa 1 pasa de Excel masivo a API (items 1.7/1.8 nuevos). Build USD 590 (Etapa 1 374 / Etapa 2 216) + PRO 400/año año 1 gratis; AI Agents 374 + 800 + 650/año; variante Avanzado eliminada.
- Motivo: pedido de Joaquin de investigar ambas APIs e incluirlas en el presupuesto.
- Impacto en capas: Infrastructure (biblioteca Horizonte.MercadoLibre compartida por consola y web).
- Riesgos/supuestos: export de stock de Fixed sigue bloqueante; verificar auto-reactivacion y User Products con la cuenta real.

### 2026-09-15 - orquestador (presupuestador)
- Etapa: Presupuesto (envio)
- Cambio: propuesta ENVIADA por WhatsApp: Etapa 1 USD 374 (50/50) + dos caminos sin precio para que el cliente elija: A = sincronizacion diaria con Fixed (cotizada internamente USD 216 + PRO 400/año, año 1 gratis); B = unica fuente de verdad (stock y ventas del local en sistema Olvidata, Fixed solo factura via su API, ML en tiempo real) — sin presupuesto formal, orientativo interno USD 900-1.300.
- Motivo: Joaquin pidio mensaje con Etapa 1 cerrada y opciones abiertas para enviar el presupuesto de la opcion elegida.
- Impacto en capas: — (opcion B requeriria nuevo Diseño/Arquitectura/Presupuesto)
- Riesgos/supuestos: opcion B depende de que la API de Fixed emita e-ticket de mostrador y del cambio de flujo en caja (posnet integrado a Fixed). Metodo de cobro UY pendiente.
