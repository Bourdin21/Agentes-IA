# Metadata del proyecto

- nombre: luciano-inmobiliaria
- fecha_inicio: 2026-08-13
- estado: presupuesto CERRADO y listo para enviar (2026-08-14) — alcance definitivo: individual+lote asíncronos con polling, certificados por FTP sin seguimiento proactivo (solo mail reactivo), alta de CUIT/puntos de venta consumida por el sistema del cliente, control de uso exclusivo de Olvidata, extracción de contratos por PDF+IA incluida. Precios finales fijados directamente por Joaquín: Opción A (SaaS) USD 950 desarrollo + USD 750/año suscripción (primer año incluido); Opción B (código fuente) USD 2.250 pago único — ver `presupuesto-cliente.md`. Pendiente antes de Implementación (no bloquea el envío del presupuesto): confirmar con el cliente qué significa "sueldos" como tipo de comprobante, y el campo exacto de WSFEv1 para facturación por cuenta y orden de terceros (R11)
- owner: Luciano Inmobiliaria
- descripcion: API de facturación electrónica ARCA (ex-AFIP) multi-tenant que se conecta al ERP actual del cliente, para emitir comprobantes (honorarios, alquileres, etc.) individuales o en lote, soportando múltiples CUIT/puntos de venta por cliente, con gestión de suscripción y control de uso para evitar reventa no autorizada. Primer producto tipo "API/SaaS" del estudio (no una app MVC de línea de negocio).
- ruta_definiciones: /docs/luciano-inmobiliaria/definiciones
- ruta_repositorio: <pendiente>

## Archivos de memoria por agente
- analista-funcional: /docs/luciano-inmobiliaria/definiciones/1-analista-funcional.md
- disenador-funcional: /docs/luciano-inmobiliaria/definiciones/2-disenador-funcional.md
- arquitecto-mvc: /docs/luciano-inmobiliaria/definiciones/3-arquitecto-mvc.md
- presupuestador: /docs/luciano-inmobiliaria/definiciones/4-presupuestador.md
- implementador: /docs/luciano-inmobiliaria/definiciones/5-implementador.md
- qa: /docs/luciano-inmobiliaria/definiciones/6-qa.md
- documentador: /docs/luciano-inmobiliaria/definiciones/7-documentador.md

## Reutilización cross-proyecto detectada (Discovery)
- **Motor de facturación AFIP/ARCA (WSAA/WSFEv1, .p12)**: `AfipService`/`AfipTokenCache` — patrón hand-rolled (SOAP armado a mano, sin SDK de terceros) ya resuelto y portado 3 veces (`marihogar` → `delicias-naturales` → `la-platense`, ver `docs/la-platense/definiciones/5-implementador.md`). Hoy asume **1 CUIT / 1 certificado por deploy** (config en `appsettings`) — para Luciano hace falta extenderlo a credenciales por tenant en base de datos, no un rediseño desde cero.
- **Cifrado de credenciales por tenant**: `WhatsAppCredentialCipherService` de `century-21` (cifra token de WhatsApp por `Grupo`) — mismo patrón aplicable para custodiar el certificado `.p12`+password de cada inmobiliaria por separado.
- **Multi-tenant + Plan/suscripción con límite**: `Plan`/`Grupo`/`ITenantContext` de `century-21` (plataforma SaaS "pensada para reventa a otras agencias", con `Plan.LimiteAsesores` y aislamiento de datos por `GrupoId`) — reutilizable como base conceptual para modelar Cliente/Suscripción/límite de puntos de venta, aunque el mecanismo de control anti-reventa es un problema distinto (ver `1-analista-funcional.md`).
- **Emisión de NC/ND AFIP**: patrón ya extendido en `century-21`/`la-platense` sobre el mismo `AfipService` — reutilizable si Luciano necesita notas de crédito/débito.
- **Sin precedente en el estudio**: producto tipo API pura (sin vistas MVC), multi-CUIT con múltiples puntos de venta por cliente, facturación en lote, certificado gestionado por el propio cliente final (self-service), y control técnico anti-reventa por volumen de uso.
