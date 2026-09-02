# Metadata del proyecto

- nombre: kite-punta-lara
- fecha_inicio: 2026-09-01
- estado: **en producción** — https://club.olvidata.com.ar/ en vivo desde 2026-09-02 (API PHP bajo /api/* + P1 en Astro en la raíz, contra la base real de DonWeb). Deploy reproducible con `bash scripts/deploy.sh` (credenciales en `.env.deploy`, gitignored; aplica migraciones y limpia caché). Etapa 1 creció bastante más allá del núcleo original a partir del conocimiento de campo de Joaquín: modelo GDPS validado empíricamente, viento/ráfaga/marea en vivo corregidos al equivalente en la costa (la estación lee ~2,5 kt de más), rango navegable por usuario con estado "al límite", señales de virazón/terral/sudestada/racheado/viento desparejo/creciente/bajante, bloqueo por viento de tierra, y panel público de acertividad de modelos. Etapa 2 (cuentas) no arrancada. Widget de pantalla de inicio: pedido y postergado a segunda etapa — requiere app nativa, una PWA no accede a esa API.
- owner: Joaquín (proyecto de uso personal, no cliente de estudio)
- descripcion: Herramienta de pronóstico de viento y "días de kite" para el spot de Punta Lara (Club Universitario, sede náutica, Ensenada). Combina medidores en vivo (CARP/SHN/SMN), promedio de modelos de pronóstico (referencia: Windguru) y fenómenos climáticos locales del Río de la Plata (birazón, sudestada) en un modelo de cálculo propio.
- ruta_definiciones: /docs/kite-punta-lara/definiciones
- ruta_repositorio: C:\Sistemas\kite-punta-lara (MONOREPO: backend PHP / API JSON en la raíz + front Astro en /front). Remoto: https://gitlab.com/bourdinjoaquin/kite-punta-lara.git
- ruta_repositorio_front: C:\Sistemas\kite-punta-lara\front (subcarpeta del monorepo; el repo hermano `kite-punta-lara-front` quedó abandonado el 2026-09-02)
- workspace: C:\Sistemas\kite-punta-lara.code-workspace
- subdominio: club.olvidata.com.ar (confirmado 2026-09-01) — alojado bajo el dominio olvidata.com.ar en DonWeb, mismo esquema que otros bots/subdominios de Olvidata Soft (no es un dominio propio nuevo)

## Archivos de memoria por agente
- analista-funcional: /docs/kite-punta-lara/definiciones/1-analista-funcional.md
- disenador-funcional: /docs/kite-punta-lara/definiciones/2-disenador-funcional.md
- arquitecto-mvc: /docs/kite-punta-lara/definiciones/3-arquitecto-mvc.md
- presupuestador: /docs/kite-punta-lara/definiciones/4-presupuestador.md
- implementador: /docs/kite-punta-lara/definiciones/5-implementador.md
- qa: /docs/kite-punta-lara/definiciones/6-qa.md
- documentador: /docs/kite-punta-lara/definiciones/7-documentador.md

## Nota de stack
Proyecto **híbrido** desde el cambio de arquitectura del 2026-09-02: backend PHP sobre DonWeb (API JSON, sin agente implementador PHP dedicado en el catálogo — se trabaja con el rol .NET adaptado) + front Astro estático construido con `implementador-astro-front`. Es el primer proyecto del estudio que combina la variante Astro con un backend propio de negocio: hasta ahora Astro se usaba solo para sitios institucionales sin backend (diercas-front, labipac-front, olvidatasoft-new), con PHP limitado al formulario de contacto (PAT-007).

Ambos se despliegan en el mismo subdominio `club.olvidata.com.ar` (Astro en la raíz, PHP bajo `/api/*`) para que compartan origen y no haga falta CORS.
