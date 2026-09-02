---
name: kite-punta-lara-decisiones-de-producto
description: "Criterios de producto de kite-punta-lara que no se deducen del código: qué bloquea, qué solo avisa, y por qué."
metadata: 
  node_type: memory
  type: project
  originSessionId: aeabc362-0545-4e4d-b049-1f477db62add
  modified: 2026-09-02T21:33:00.802Z
---

Decisiones tomadas con Joaquín el 2026-09-02 que gobiernan cómo el sitio
recomienda o descarta un día. No se deducen leyendo el código.

**Bloquean (no se navega):**
- **Viento de tierra (S/SO/O)** — textual: *"es condición justa y necesaria
  para no navegar"*. Se evalúa por HORA, no por día, porque una mañana
  bloqueada y una tarde limpia siguen siendo un día para ir a la tarde. Es la
  única señal de riesgo **físico** del sistema.
- **Sudestada con temporal.**

**Solo avisan (el día sigue siendo navegable):**
- **Viento racheado** — textual: *"no te lo esconde ni te lo prohíbe"*.
- **Creciente y bajante** del río.

**Criterio de navegabilidad:** lo decide un rango de viento que elige cada
usuario, **sin cuenta** (queda en el navegador). Tres estados: plena, "al
límite" (el sostenido no llega al mínimo pero las rachas sí, margen de 1 kt) y
fuera. El margen se estira **solo por abajo**: quedarse corto es una molestia,
pasarse es un riesgo.

**Dos principios que se sostuvieron en todas las capas y conviene no romper:**

1. **Nunca presentar una inferencia como si fuera un dato.** Las dos mareas
   (medida vs. modelo) nunca comparten eje ni se "corrigen" una con la otra; la
   lectura de la estación y su equivalente estimado en la costa viajan en
   campos separados. Cuando algo es estimado, se dice.
2. **Ante datos faltantes o desconocidos, cerrar hacia el lado seguro.** Una
   señal de riesgo que el front no reconoce bloquea el día; sin dato de rachas
   una hora no puede ser "al límite". Un falso "sí" es mucho peor que un falso
   "no" cuando decide si alguien se mete al río con una cometa.

Pendiente decidido: el **widget de pantalla de inicio** se postergó a segunda
etapa — requiere app nativa, una PWA no accede a esa API.

Ver [[joaquin-experto-de-dominio-kite]].
