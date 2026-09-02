---
name: joaquin-experto-de-dominio-kite
description: Joaquín es kitesurfista activo en Punta Lara y su conocimiento de campo corrige al modelo — priorizarlo sobre la bibliografía.
metadata: 
  node_type: memory
  type: user
  originSessionId: aeabc362-0545-4e4d-b049-1f477db62add
  modified: 2026-09-02T21:32:44.027Z
---

En kite-punta-lara, Joaquín no es solo el cliente: es **la fuente de verdad del
dominio**. Navega en el spot y su conocimiento de campo corrigió al sistema
varias veces, siempre para mejor.

Casos concretos (2026-09-02):

- Dijo que los modelos que mejor le funcionan son GFS 13 km, WRF 12 km y
  GDPS 15 km. La validación empírica contra mediciones reales le dio la razón:
  **GDPS ganó** (MAE 1,87 kt vs 4,67 del que estaba en uso).
- Corrigió que la bajante la causa el **norte**, no el O/NO que teníamos
  configurado — un sector que habíamos inventado nosotros.
- Aportó que el SE entra arrachado, que con sudestada el viento no entra
  parejo cerca de la costa, y que **la estación de Norden lee 2-3 kt más que
  la costa** (dato que destapó un error silencioso: el motor calculaba las
  señales sobre la lectura cruda).
- Definió los rumbos navegables en sus términos: "SE, E, NE, N, NO son vientos
  navegables". Eso llevó a modelar el sector **por rumbo y no por grados**, así
  su criterio entra sin traducción.

**Cómo aplicar esto:** cuando aporta un dato de campo, implementarlo aunque
contradiga la bibliografía o lo que dice el modelo. Y cuando una decisión
depende del spot (sectores, umbrales, qué se considera navegable),
preguntarle en vez de deducir — pero preguntarle **en rumbos y situaciones
concretas, no en grados**, que es como razona.

Ver [[kite-punta-lara-decisiones-de-producto]] y
[[kite-punta-lara-hosting-donweb]].
