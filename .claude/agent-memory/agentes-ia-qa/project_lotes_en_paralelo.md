---
name: lotes-en-paralelo
description: Trampas de correr dos lotes de QA en paralelo sobre el mismo repo — colision de ids de catalogo, keys/ de Data Protection y la app que se cae sola
metadata:
  type: project
---

Cuando dos o mas corridas de QA van en paralelo sobre el mismo sistema, hay seis cosas que muerden y ninguna es obvia.

**1. Colision de ids del catalogo.** Los dos lotes toman el "siguiente id libre" de `docs/qa/regresiones-manuales.yml` al mismo tiempo y escriben el mismo. Paso el 2026-10-01 en eleven-la-plata: lote B tomo ELV-003/004 y lote A tambien, y hubo que renumerar a ELV-005/006/007 y regenerar el indice.

**Why:** el yml es un archivo compartido sin reserva de rango; cada lote corre en contexto propio y no ve lo que el otro acaba de escribir.

**How to apply:** antes de arrancar un lote que corre en paralelo, pedirle al orquestador el rango de ids reservado para ese lote (ej. lote A: 005-009, lote B: 010-014), o escribir los items recien al cerrar y verificar `grep -n "^  - id: <PREFIJO>-" ` antes de elegir el numero. Al terminar, validar que no hay duplicados: `python -c "...Counter(ids)..."`. Y regenerar el indice con `python scripts/contexto.py resumenes`, nunca editarlo a mano.

**2. `Eleven.Web/keys/` aparece como untracked y no es tuyo del todo.** Levantar la app con `dotnet run` hace que Data Protection escriba su clave ahi. Hay que borrarlo al cerrar — pero si el otro lote todavia tiene la app corriendo, reaparece. Verificar `git status --porcelain` al final y, si reaparecio, declararlo como artefacto generado del otro lote en vez de pelearlo.

**3. La app levantada en background se cae sola.** Un `dotnet run` lanzado con `run_in_background` se murio en medio de un barrido largo de paginacion (exit 127, sin excepcion en el log). Relanzarlo con `nohup ... &` aguanto. Despues de relevantarla hay que **re-loguearse**: la cookie vieja no sirve porque la clave de Data Protection cambia.

**4. El nombre del clon que manda la convencion de aislamiento es el que los arneses RECHAZAN.** La guarda de base de los nueve arneses de la-platense corta por **substring** contra `laplatense_qa`, y esta puesto a proposito (`tools/MigracionCatalogo/Program.cs` lo deja escrito: "`laplatense_qa` entra por substring, asi que cubre `laplatense_qa_l1`..`laplatense_qa_d9`"). O sea: el clon `laplatense_qa_l<n>` que el brief de aislamiento manda crear hace que TODO arnes aborte con exit 2 y el mensaje "la cadena de conexion apunta a 'laplatense_qa'". Se lee como un arnes roto y son tres intentos perdidos.

**How to apply:** dos clones por lote con nombres distintos — uno `laplatense_qa_l<n>` para la app por HTTP (ahi el nombre no molesta a nadie) y otro **sin** ese prefijo (`lp_lote<n>_arnes`) para los arneses. Conviene crearlos juntos al arrancar; el dump de `laplatense_dev` se reusa para los dos.

**5. El puerto asignado puede estar tomado por otro lote y el error no dice que lote.** El 2026-10-08 el 7253 del brief ya lo tenia un `dotnet` ajeno y el 7254 un `FerreteriaLaPlatense.Web` de otra corrida. El log de arranque dice `address already in use` y, si el redirect de salida se reusa, se puede leer el log de OTRA app (vi un content root de `olvidatasoft-crm` en mi propio `app.log`). Antes de levantar: `netstat -ano | grep ":<puerto>"`, y si esta ocupado se corre el puerto (7353/7354) y **se declara en el informe**, porque el brief dice otro numero.

**6. Los `bin/` de los arneses hay que verificarlos SIEMPRE al arrancar, no solo despues de mutar.** Dos de los tres arneses de mi lote tenian `FerreteriaLaPlatense.Infrastructure.dll` en un hash de la semana anterior (`f5a5f97`, Oct 7) mientras la referencia de hoy era `71bcaa42`. Ninguna mutacion de por medio: simplemente nadie los recompilo desde entonces. Correrlos asi habria publicado una "linea base re-medida hoy" del codigo de hace cuatro dias. El chequeo es una linea y va antes de la primera corrida: `md5sum <Proyecto>.Infrastructure/bin/Debug/net10.0/*.dll tools/*/bin/Debug/net10.0/<Proyecto>.Infrastructure.dll` y `dotnet build tools/<Arnes>` para cada uno que no coincida.

Ver tambien [[metodo-qa-datos-reales]].
