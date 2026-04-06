---
description: Parametros base de estimacion y presupuesto para proyectos del cliente Eleven La Plata.
applyTo: "**/*.{md,prompt.md,agent.md,instructions.md}"
---

# Parametros de referencia — Eleven La Plata

## Proyecto de referencia calibrado
- **Sistema:** Gestion Integral Eleven La Plata (27 modulos funcionales, Clean Architecture, .NET 10 + MySQL)
- **Horas reales totales:** 30 horas
- **Costo total real:** USD 500
- **Tasa efectiva:** USD 17 / hora

## Tasa vigente
- **Tasa base:** USD 17 / hora
- Aplicar a todos los presupuestos futuros salvo indicacion contraria del cliente.
- Si el cliente negocia descuento, no bajar de USD 14/h sin aprobacion explicita.

## Distribucion proporcional de referencia

| Area funcional | % del total | Horas ref. | USD ref. |
|---|---|---|---|
| Arquitectura y base del sistema | 26.7% | 8 h | $ 133 |
| Operaciones comerciales | 26.7% | 8 h | $ 133 |
| Servicio tecnico | 20.0% | 6 h | $ 100 |
| Modulo financiero | 16.7% | 5 h | $ 84 |
| Dashboard, reportes y sistema | 10.0% | 3 h | $ 50 |
| **TOTAL** | **100%** | **30 h** | **$ 500** |

## Reglas de escala para nuevos presupuestos

### Por modulo individual (nuevo modulo simple)
- Catalogo / ABM basico: 1 - 2 h · USD 17 - 34
- ABM con relaciones y validaciones: 2 - 4 h · USD 34 - 68
- Modulo con workflow / estados: 4 - 6 h · USD 68 - 102
- Modulo financiero o con logica compleja: 5 - 8 h · USD 85 - 136

### Modificacion sobre modulo existente
- Agregar campo simple: 0.5 h · USD 8
- Agregar regla de negocio: 1 - 2 h · USD 17 - 34
- Nuevo reporte o exportacion: 1 - 2 h · USD 17 - 34
- Migracion EF requerida: sumar 0.5 h · USD 8 por cada migracion

## Formato de entrega al cliente

- Documento simple, sin jerga tecnica
- Agrupado por area funcional (no por capa tecnica)
- Incluir tabla: Area | Horas | USD
- Incluir seccion "Que esta incluido" y "Que NO esta incluido"
- Condiciones estandar: 50% al inicio / 50% a la entrega
- Validez de oferta: 30 dias

## Exclusiones fijas (siempre aplicar salvo excepcion documentada)

- Migracion de datos desde sistema anterior
- Configuracion y costo del servidor / hosting
- Facturacion electronica AFIP / ARCA
- Aplicacion movil (iOS / Android)
- Integracion con hardware externo
- Cambios de alcance posteriores al inicio (se presupuestan por separado)

## Notas de calibracion

- Este parametro fue calibrado en base al proyecto real finalizado en 2025.
- Revisar y actualizar la tasa cada 6 meses o ante cambio de contexto economico.
- Para proyectos > 50h aplicar contingencia adicional del 15%.
- Para proyectos que incluyan migracion de datos, agregar entre 20% y 30% al total.
