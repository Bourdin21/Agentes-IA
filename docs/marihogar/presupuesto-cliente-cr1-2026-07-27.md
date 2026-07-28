# Olvidata**Soft**
---

**marihogar — Ajustes post-demo (Change Request #1)**
**OlvidataSoft · Julio 2026**

## Sobre este ajuste

Después de la primera demo nos pasaste una serie de mejoras y correcciones sobre el sistema ya en producción. Las agrupamos acá como un ajuste puntual de alcance (no una etapa nueva) para que tengas el costo claro antes de arrancar.

## Qué incluye

| Ítem | Descripción | USD |
|---|---|---:|
| Órdenes de compra: tipo de factura + impuestos | Elegir si la compra tiene factura A/B/C o es sin factura, y cargar IVA/Ingresos Brutos/Otros impuestos discriminados sobre el total | 84 |
| Cheques: fecha de emisión | Cargar la fecha real de emisión del cheque, con cálculo automático (pero editable) del vencimiento a 30/60/90 días | 34 |
| Ventas: tarjeta de crédito y Banco Carrefour | Nueva forma de pago con cuotas (3/6/9/12) e interés opcional, más Banco Carrefour como medio de pago | 50 |
| Comprobante: descargar PDF y enviar por WhatsApp | Botón para descargar el comprobante y compartirlo por WhatsApp con el cliente (si tiene el teléfono cargado) | 67 |
| Gastos: nuevas categorías | Sueldos, Impuestos, Luz, APR, Publicidad y Otro (de resguardo) | 50 |
| Importación de tu historial | Carga de tus proveedores, compras, ventas y gastos del sistema anterior a marihogar | 168 |
| Cheques: acreditación manual | El sistema te avisa cuando un cheque vence, pero la acreditación la confirmás vos con un clic | 34 |
| **Total** | | **487** |

*Las horas de desarrollo son internas — el precio de cada ítem ya las incluye.*

## Qué necesitamos de tu parte antes de arrancar

- Confirmarnos si el comprobante que se descarga/envía por WhatsApp, cuando la venta todavía no tiene factura AFIP emitida, puede ser un "Detalle de venta" simple (no fiscal) — o si preferís otra cosa.
- Confirmarnos que las equivalencias "Marketing → Publicidad" y "APR → APR" del historial de gastos son correctas.
- Estar disponible para revisar, después de importar tu historial, la lista de productos que el sistema va a crear automáticamente (porque tu catálogo viejo tiene muchos más productos que los 8 que tenés cargados hoy) y completarles el precio de venta.

## Qué no está incluido

- Re-facturación retroactiva ante AFIP de tus ventas históricas (se importan como ventas cerradas, sin comprobante fiscal, tal cual estaban).
- Envío 100% automático por WhatsApp sin intervención del vendedor (eso requiere la integración de WhatsApp Business API, que es la Etapa 2 que quedó en pausa).

## Condiciones comerciales

- Total: **USD 487**, 100% al aprobar este ajuste (no aplica el esquema 50/50 por etapa, es un ajuste puntual).
- Sin cargo de Tokens IA (mismo criterio ya usado en tu presupuesto original).
- Cambios de alcance adicionales sobre este ajuste se cotizan aparte.

**Olvidata Soft — olvidatasoft@gmail.com — www.olvidata.com.ar**
