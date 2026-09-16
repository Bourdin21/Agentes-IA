---
name: estandares-qa
description: Catalogo cross-proyecto de bugs recurrentes y reglas preventivas del estudio (MH-001, CRM-0xx, LP-0xx, KOI-Bxx). Usar ANTES de escribir o revisar codigo .NET/MVC, y al cerrar QA, para no repetir un bug ya resuelto en otro proyecto.
paths:
  - "**/*.cs"
  - "**/*.cshtml"
---

# Estandares QA / implementador (catalogo cross-proyecto)

La fuente completa es `.github/instructions/32-estandares-qa-implementador.instructions.md` (~58 KB). **No la leas entera**: buscá la seccion que aplica al cambio que estas haciendo.

## Como usarla

1. Listar las reglas vigentes (una linea por regla):
   `grep -n "^## " .github/instructions/32-estandares-qa-implementador.instructions.md`
2. Leer SOLO las secciones relacionadas con lo que tocas (ej. una query EF nueva, un checkbox, un combo en Editar, un decimal en un input, un tope de gasto).
3. Al terminar, si encontraste un bug generalizable, agregar la regla nueva ahi **y** el item reproducible en `docs/qa/regresiones-manuales.yml`.

## Las que mas se reincidieron (chequeo rapido)

- **MH-001** — nunca `Where(listaLocalDeString.Contains(x))` contra MySQL: revienta incluso con la lista vacia. Materializar y filtrar en memoria, o pasar el `IN` a ints.
- **CRM-019** — `StartsWith`/`EndsWith`/`Contains` de substring tampoco traducen: usar `EF.Functions.Like`.
- **CRM-001** — campo nuevo con varios puntos de alta: un solo metodo de dominio que lo escriba.
- **CRM-017** — un tope de gasto se chequea en TODOS los caminos que lo consumen, y el contador tambien.
- **CRM-018** — un flag que es decision de negocio se persiste en base, nunca en un `static`.
- **CRM-020** — una feature opcional dentro de un flujo critico va envuelta: si falla, degrada, no tira el flujo.
- **LP-002** — al extender un campo existente, actualizar TODOS los lugares que ya lo leen, no solo el que motivo el pedido.
- **LP-003** — decimales que vuelven al server se renderizan en cultura invariante.
- **KOI-B01** — checkbox + hidden: el checkbox va primero.

## Regresiones ejecutables

`docs/qa/regresiones-manuales.yml` es el playbook que QA corre sobre el sistema bajo prueba. Greppeable por `- id:`.
