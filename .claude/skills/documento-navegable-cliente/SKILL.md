---
name: documento-navegable-cliente
description: Pagina navegable (artifact) de un documento de entrega al cliente con la marca Olvidata — manual de uso, resumen de sprint, instructivo. Capturas de produccion, indice con seccion activa, envoltorio oscuro de marca. Usar cuando el entregable se va a leer y compartir, no solo adjuntar.
---

# Documento navegable para el cliente

Fuente completa: `.github/instructions/41-documento-navegable-cliente.instructions.md`.
Contenido y tono del `.md` fuente: `31-formato-documento-cliente`. Tokens de marca: `/olvidata-diseno`.

**El `.md` es la fuente; la pagina es la copia de lectura.** Se publica como artifact privado y se
actualiza **sobre la misma URL**, que queda anotada en `7-documentador.md` del proyecto.

## Las seis reglas que se verifican

1. **El contenido se verifica contra PRODUCCION, no contra los documentos.** Entrar con un usuario
   real, leer el menu renderizado y copiar los textos que la pantalla muestra. Los manuales previos y
   las memorias envejecen: ya paso que un manual declarara pendiente algo que llevaba nueve dias en
   produccion.
2. **Tema oscuro, uno solo.** `color-scheme: dark`, `--dark #0A0A0A`, acento `--accent #2B9DE4` y
   nada mas. Sin par claro/oscuro. Blanco, naranja y rojo prohibidos como acento.
3. **Los dos vidrios.** Las capturas de los sistemas son **claras** → van sobre `.vidrio` (ahumado).
   `.vidrio-claro` es solo para tarjetas/tablas/avisos sobre fondo plano. Elegir mal da panel blanco
   con texto blanco y **ningun chequeo de contraste lo detecta**.
4. **Luz por debajo de `.14` de alfa**, y el **isotipo sin resplandor** (un `drop-shadow` de acento lo
   convierte en logo de gaming).
5. **El logotipo es una unidad.** `Olvidata<b>Soft</b>` dentro de su propio `<span>`: hijo directo de
   un flex con `gap`, el wordmark se parte en dos. Zona de respeto = radio del anillo del isotipo,
   como separacion real.
6. **Capturas: solo GET.** El unico POST es el login. 1500×940 @2x → WebP 1500px q80. Cada captura con
   epigrafe que dice **que mirar**. El artifact nace privado porque las capturas traen datos reales.

## Antes de publicar

Renderizar una vez, **una sola pasada de correcciones**, y medir: `scrollWidth === innerWidth` a 400px,
cero `pageerror`, y el indice marcando bien la seccion al abrir, en el medio y al final.

## Estructura

Indice lateral sticky con la seccion activa resaltada (`aria-current`, traida a la vista con
`scrollTop` del `<nav>`, nunca `scrollIntoView`) · columna de lectura a `70ch` · secciones numeradas
solo si se leen en orden · pasos numerados por flujo · tablas en `overflow-x: auto` · avisos en dos
tonos (acento = hay que saberlo, gris = pendiente, con **de que depende**) · tarjetas "Antes" para los
huecos que el sistema tapa · plan de arranque al final si el cliente todavia no opera.

## Trampas de la captura

- `https://127.0.0.1`, nunca `localhost` (Chromium resuelve a `::1`, Kestrel escucha IPv4).
- Los `Listar` de DataTables son **POST**: los ids se cosechan del DOM tras ~5 s, no del endpoint.
- `page.click('form button[type=submit]')` engancha el logout del layout → usar `requestSubmit()`.
- Los scripts de captura se escriben con la herramienta de archivos, **nunca con heredoc de bash**.

## Indice de la fuente

```
grep -n "^## " .github/instructions/41-documento-navegable-cliente.instructions.md
```
