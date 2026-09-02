---
name: feedback-venta-iva-pago-multiple
description: Regla cross-proyecto (2026-08-15) - en modulos de venta, el pago de una venta puede dividirse en multiples medios (efectivo/tarjeta/transferencia) y debe validarse contra el total con IVA incluido
metadata:
  type: feedback
  originSessionId: 2bb59244-3415-45d6-9052-8072386118cb
  modified: 2026-08-15T17:24:36.408Z
---

El usuario planteo (2026-08-15) un caso de negocio que aplica a **todo proyecto con modulo de venta de productos**: un producto se cobra con % IVA aplicado, pero el pago de esa venta puede repartirse en mas de un medio de pago (parte efectivo, parte tarjeta, parte transferencia) sobre la misma venta.

**Modelo funcional confirmado:** el IVA es propiedad de las lineas de PRODUCTO (VentaDetalle: PorcentajeIVA/ImporteIVA por linea), nunca del pago. El pago es una lista independiente de N lineas (VentaPago: MedioPago + Importe + campos condicionales segun medio). Las dos cosas se cruzan solo en una validacion de cierre: **la suma de los Importe de todas las lineas de pago debe ser exactamente igual al Total de la venta (que ya incluye el IVA)** — bloqueante en JS (recalculo en vivo de la diferencia pendiente) Y en el Service antes de persistir, nunca solo uno de los dos lados.

**Por que era un gap:** el patron de "venta con N lineas de pago" ya existia de facto en ShowroomGriffin y ganaderia (ver GAN-001 en `32-estandares-qa-implementador.instructions.md`, guard de "al menos un item" sobre `Pagos[i]`), pero nunca se habia formalizado la regla de que la suma de esos pagos debe cerrar exactamente contra el total con IVA. Era una validacion implicita, no documentada ni chequeada sistematicamente.

**Donde quedo codificado:**
- `32-estandares-qa-implementador.instructions.md` — nueva seccion "Venta con IVA + pago dividido en multiples metodos (PAT-003)": regla, como implementarla (client+server), criterio de redondeo a documentar explicitamente, como detectarla en QA.
- `docs/patrones/catalogo.yml` — PAT-003 actualizado para reflejar el modelo completo (antes solo cubria Cuotas, ahora cubre IVA por linea + pago multi-medio).
- `33-verificacion-automatizada-qa.instructions.md` — nuevo item en el alcance automatizable por navegador: pago que no suma el total (con IVA) debe bloquear el guardado.

**Como aplicar:** todo proyecto nuevo o existente con modulo de venta de productos debe implementar esta validacion — no es opcional ni especifico de un proyecto. Al diseñar/arquitecturar/implementar un modulo de ventas nuevo, consultar PAT-003 en el catalogo antes de modelar Venta/VentaPago desde cero. Relacionado: [[project-agentes-ia-mejoras-2026-08-15]].
