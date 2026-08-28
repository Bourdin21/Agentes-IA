# Memoria - Analista funcional

## Proyecto: dietetica-mitre
## Ultima actualizacion: 2026-08-26

## Definiciones vigentes

### Contexto del lead
Dietetica Mitre — dietetica (rubro "Dieteticas y venta de productos") en Av. Godoy Cruz 394, Mendoza. Entro por outbound frio con el mismo mensaje de rubro usado con desborder-sin-gluten (pitch de stock/ventas en tiempo real + cierre de caja automatico). Contacto registrado como "Equipo" (sin nombre de persona), telefono 5492617751219, sin email.

Cuestionario de calificacion (3 preguntas, esta vez **sin el problema de respuestas fuera de orden** que tuvo desborder-sin-gluten — respuestas limpias y coherentes con su pregunta):

1. ¿Que es lo mas te complica hoy?: **"Facturo todo a mano"** — identico pain point a desborder-sin-gluten.
2. ¿Con que lo manejas ahora?: **"Papel"** — mas simple que desborder-sin-gluten (que declaro "otro sistema" no identificado); aca no hay ningun sistema de por medio, es puramente manual.
3. ¿Cuantas personas lo van a usar?: **"1"** — sin ambiguedad (a diferencia de desborder-sin-gluten, que quedo entre "1 o 2").

### Lectura del dolor real
Mismo pain point exacto que desborder-sin-gluten (facturacion manual), con un discovery mas limpio y sin contradicciones: papel = 100% manual, coherente con "facturo todo a mano" (a diferencia de desborder, donde "otro sistema" generaba una pregunta abierta sobre por que no cubria la facturacion). Sin necesidad de research de mercado sobre "que sistema usan" — no usan ninguno.

### Modulos/features analizados
Identicos a desborder-sin-gluten — mismo concepto de negocio (dietetica), mismo pain point, mismo pitch outbound:
- Facturacion electronica AFIP/ARCA (nucleo de ambas propuestas).
- Catalogo de productos (granel y empaquetados, %IVA por producto).
- Control de stock (Propuesta A).
- Ventas con cobro (PAT-003) integradas a la facturacion (Propuesta A).
- Cierre de caja automatico (Propuesta A).
- Compras a proveedor simples (Propuesta A).
- Usuarios con roles — aca alcanza con 1 solo rol (Administracion), sin necesidad de rol Vendedor separado dado que declararon 1 sola persona.

### Reglas funcionales acordadas (hipotesis, a confirmar)
Identicas a desborder-sin-gluten: ambas propuestas emiten comprobantes AFIP reales; Propuesta B sin stock; Propuesta A descuenta stock al facturar una venta.

### Criterios de aceptacion vigentes
Identicos a desborder-sin-gluten (ver `docs/desborder-sin-gluten/definiciones/1-analista-funcional.md` para el detalle completo — mismo dominio, mismo alcance).

### Supuestos y dependencias
- **[SUPUESTO — pregunta abierta para la demo]** Condicion fiscal de Dietetica Mitre ante AFIP/ARCA (Monotributo o Responsable Inscripto) — igual que desborder-sin-gluten, define el tipo de comprobante.
- **[SUPUESTO]** Certificado digital .p12 disponible o tramitable por el cliente — dependencia dura, no resoluble por el estudio.
- **1 sola persona** confirmado sin ambiguedad — simplifica el diseño de roles (no hace falta el rol Vendedor separado de audifonos-bariloche/desborder-sin-gluten, aunque se deja preparado por si suman una segunda persona mas adelante).
- Discovery limpio, sin el problema de respuestas desordenadas de otros leads recientes del mismo bot de calificacion.

### Exclusiones confirmadas
Identicas a desborder-sin-gluten: migracion de datos (no aplica de todas formas, es papel puro), app movil nativa, hardware fiscal dedicado, multi-sucursal.

## Historial de ajustes
- 2026-08-26: primera version, a partir del cuestionario de calificacion outbound (respuestas limpias, sin reconstruccion necesaria). Mismo concepto que desborder-sin-gluten — pendiente de confirmacion con el lead antes de iniciar implementacion (condicion fiscal AFIP).
