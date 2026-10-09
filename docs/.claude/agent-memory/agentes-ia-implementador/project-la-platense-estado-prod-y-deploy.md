---
name: project-la-platense-estado-prod-y-deploy
description: Produccion de La Platense esta en 8 de 18 migraciones con 10 pendientes ya ensayadas y aprobadas; el deploy esta listo salvo la credencial de Web Deploy
metadata:
  type: project
---

Al 2026-10-07, **produccion de la-platense (`db_a7251f_laplaten`) esta en 8 migraciones de las 18
del repo: 10 pendientes.** Tiene el catalogo cargado (112.485 productos, 2.990 clientes, 110.683
codigos de proveedor, 85 proveedores) y **casi cero operacion**: 0 ventas, 1 movimiento de caja,
1 gasto. `laplatense_dev` esta en 18 y se preserva como control.

**Las 10 pendientes ya se ensayaron sobre una copia fiel de produccion y pasaron**: 14 segundos,
ninguna fila perdida, ningun valor preexistente cambiado, y el backfill de `LP-050` dejo la unica
fila de `CajaMovimientos` bien clasificada. Snapshot de rollback en
`C:/Sistemas/backups/laplatense/laplatense_PROD_2026-10-07_pre-migracion-18.sql`.

**Why:** el riesgo que `LP-050` marcaba —un backfill que clasifica el medio de pago parseando
`Descripcion` con `ELSE NULL`— **no tiene superficie en produccion porque filtra por
`OrigenTipo IN ('Venta','CobroCC')` y no hay ni una fila de esos tipos.** Es el deploy mas barato
que este sistema va a tener: en cuanto produccion empiece a operar ventas, ese backfill pasa a
tener filas reales y el ensayo hay que repetirlo.

**How to apply:** si el tema vuelve, **el argumento tecnico es deployar pronto**, y es el unico que
el ensayo habilita (no habilita afirmar que el backfill de texto este verificado — no corrio).
Lo que falta no es tecnico: la credencial de Web Deploy no autentica, ver
[[reference-acceso-produccion-la-platense]]. Y antes de dar por buenos estos numeros, re-medirlos:
si alguien opero el sistema desde entonces, cambiaron — ver [[feedback-medir-antes-de-heredar]].
