<!-- Archivado de docs/olvidata-agentes-multirubro/trazabilidad.md el 2026-10-05 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# trazabilidad - 2026-10 (1 bloques archivados)

- 2026-10-03 - Verificacion del despliegue y estado del bloqueo

---

## 2026-10-03 - Verificacion del despliegue y estado del bloqueo

- **El saldo de Anthropic sigue agotado** (chequeado con una llamada a Haiku de 5 tokens: el 400 de
  `credit balance is too low` se repite). La evaluacion de la corrida #20 sigue cortada y **la publicacion del chat
  libre sigue bloqueada**.
- **El despliegue quedo verificado desde afuera, sin tocar datos:** `/health/vivo` 200, `/Account/Login` 200, y los tres
  assets nuevos servidos — `js/chat-libre-3d.js` (8.505 bytes, la pieza 3D), `js/site.js` (30.449, con el autocomplete
  de menciones) y `css/site.css` (71.420). El codigo de M28 + M29 esta entero en produccion.
- **Decision tecnica que conviene dejar escrita: NO publicar el agente hasta que haya saldo.** Publicar ahora lo pondria
  en el menu y **fallaria en el primer mensaje**, porque sin credito el proveedor devuelve un 400. El estado actual
  —codigo desplegado, agente en **Borrador**, menu que no lo ofrece (CA-01.2)— **es el estado seguro**, no un trabajo a
  medio terminar. Usar `evaluacion-excepcion` para saltear el gate seria doblemente malo: saltea la evaluacion **y**
  publica una funcionalidad que no puede funcionar.
- **Secuencia cuando haya saldo, sin cambios:** cargar credito -> `evaluacion-reintentar 20 --confirmar` (solo los 10
  casos cortados) -> si queda aprobada, `publicar 66` (la v3) -> humo minimo: abrir el chat libre, escribir `@`, probar
  la casilla de internet.
