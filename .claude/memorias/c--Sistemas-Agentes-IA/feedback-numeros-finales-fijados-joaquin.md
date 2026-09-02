---
name: feedback-numeros-finales-fijados-joaquin
description: "Patron recurrente confirmado: Joaquin frecuentemente fija el numero FINAL de un presupuesto a mano, pisando el resultado calculado por la formula/tiers — es una decision comercial esperada, no un error a corregir ni a resistir"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2bb59244-3415-45d6-9052-8072386118cb
  modified: 2026-08-30T14:06:53.456Z
---

Patron de comportamiento confirmado varias veces (ganaderia, luciano-inmobiliaria, y de nuevo en la tanda de leads de dieteticas del 2026-08-25/27: desborder-sin-gluten Opcion B 351→350→400, dietetica-mitre heredado, Peras del Olmo Opcion A 670→650): Joaquin, como dueño del estudio, tiene la ultima palabra sobre el precio final de un presupuesto y frecuentemente lo ajusta a mano despues de ver el calculo formal (formula + tiers de descuento) — a veces subiendo, a veces bajando, casi siempre para llegar a un numero "redondo" o comercialmente comodo, no a un numero recalculado por una razon tecnica.

**Como reaccionar cuando esto pasa:**
- No tratarlo como un error a corregir ni pedir que "recalcule bien" — es una decision de negocio legitima, documentada como tal.
- Registrar en `4-presupuestador.md` el numero formal (el que da la formula/tier) Y el numero final fijado, con el % de descuento efectivo resultante (aunque no coincida con ningun tier de la tabla) — mismo criterio ya usado en Ganaderia y Luciano Inmobiliaria ("numeros finales fijados por Joaquin").
- Actualizar el documento cliente (`presupuesto-cliente.md`) con el numero final, no con el numero formal.
- Si Joaquin corrige el mismo numero mas de una vez en la misma sesion (paso 2+ veces con desborder-sin-gluten y con Peras del Olmo), no cuestionarlo — simplemente aplicar el ultimo valor dado y dejar rastro de las versiones anteriores en el historial de ajustes, para que quede claro cual es la vigente si se reenvia el documento.

**Por que importa:** evita que en sesiones futuras se intente "defender" el calculo formal cuando Joaquin pide cambiar un numero, o que se pierda de vista cual fue el ultimo numero realmente comunicado al cliente cuando hubo varias correcciones seguidas.
