---
name: convertimetoutc-y-el-kind-del-datetime
description: TimeZoneInfo.ConvertTimeToUtc tira ArgumentException (500) segun el Kind del DateTime que reciba; el camino de la pantalla nunca falla y el del scheduler si, asi que el bug nace dormido.
metadata:
  type: feedback
---

Todo `TimeZoneInfo.ConvertTimeToUtc(fecha, ZonaArgentina)` que reciba un `DateTime` de un parametro
publico va con `DateTime.SpecifyKind(fecha.Date, DateTimeKind.Unspecified)` adentro.

**Why:** el metodo tira `ArgumentException: the supplied DateTime did not have the Kind property set
correctly` si el `Kind` es `Local` y la zona de origen no es la local, o si es `Utc` y la zona no es
UTC. En una pantalla MVC eso es un **500 directo**. Y el bug nace dormido: el camino de la UI pasa por
`DateTime.TryParse` de un string del formulario, que devuelve `Unspecified` y **no falla nunca**, asi
que el filtro anda perfecto en el navegador. Revienta recien cuando otro llamador pasa
`DateTime.Today` (que es `Local`) — el scheduler que se construye el mes que viene, una sonda, un
endpoint nuevo. Es el patron del estudio de que la pantalla y el proceso de fondo comparten el
helper y el sintoma se manifiesta distinto en cada uno (misma familia que CRM-019).

**How to apply:** aparece en todo filtro de "fecha calendario en ART contra una columna UTC", que es
un patron copiado literal en varios proyectos (`ContactosController`, cualquier daterangepicker). El
precedente del repo lo tiene **sin el SpecifyKind**, asi que copiarlo tal cual arrastra la trampa: ahi
funciona de casualidad porque el unico llamador es un `TryParse`. Si el metodo nuevo es un Service
con firma `DateTime?`, el guard va adentro del Service, no en el controller.

Encontrado en crm-olvidata (2026-10-15, cola de seguimiento) **ejecutando el filtro con los 3 `Kind`
desde una sonda** — ver [[sonda-ef-desechable]]. `dotnet build` lo daba por bueno y la pantalla
tambien: la unica forma de verlo es llamar al metodo con `DateTime.Today`. Candidato a regla del
catalogo cross-proyecto (`32-estandares-qa-implementador`), pendiente de la suite de evals que exige
tocar ese archivo.
