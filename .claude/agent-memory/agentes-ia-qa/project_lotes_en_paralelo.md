---
name: lotes-en-paralelo
description: Trampas de correr dos lotes de QA en paralelo sobre el mismo repo — colision de ids de catalogo, keys/ de Data Protection y la app que se cae sola
metadata:
  type: project
---

Cuando dos corridas de QA van en paralelo sobre el mismo sistema, hay tres cosas que muerden y ninguna es obvia.

**1. Colision de ids del catalogo.** Los dos lotes toman el "siguiente id libre" de `docs/qa/regresiones-manuales.yml` al mismo tiempo y escriben el mismo. Paso el 2026-10-01 en eleven-la-plata: lote B tomo ELV-003/004 y lote A tambien, y hubo que renumerar a ELV-005/006/007 y regenerar el indice.

**Why:** el yml es un archivo compartido sin reserva de rango; cada lote corre en contexto propio y no ve lo que el otro acaba de escribir.

**How to apply:** antes de arrancar un lote que corre en paralelo, pedirle al orquestador el rango de ids reservado para ese lote (ej. lote A: 005-009, lote B: 010-014), o escribir los items recien al cerrar y verificar `grep -n "^  - id: <PREFIJO>-" ` antes de elegir el numero. Al terminar, validar que no hay duplicados: `python -c "...Counter(ids)..."`. Y regenerar el indice con `python scripts/contexto.py resumenes`, nunca editarlo a mano.

**2. `Eleven.Web/keys/` aparece como untracked y no es tuyo del todo.** Levantar la app con `dotnet run` hace que Data Protection escriba su clave ahi. Hay que borrarlo al cerrar — pero si el otro lote todavia tiene la app corriendo, reaparece. Verificar `git status --porcelain` al final y, si reaparecio, declararlo como artefacto generado del otro lote en vez de pelearlo.

**3. La app levantada en background se cae sola.** Un `dotnet run` lanzado con `run_in_background` se murio en medio de un barrido largo de paginacion (exit 127, sin excepcion en el log). Relanzarlo con `nohup ... &` aguanto. Despues de relevantarla hay que **re-loguearse**: la cookie vieja no sirve porque la clave de Data Protection cambia.

Ver tambien [[metodo-qa-datos-reales]].
