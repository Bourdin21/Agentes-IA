# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-07-30 15:00 - orquestador (analista-funcional / disenador-funcional / arquitecto-mvc / presupuesto-mvc)
- Etapa: Analisis → Diseno → Arquitectura → Presupuesto
- Cambio: Creado el proyecto Diercas SA — sitio institucional en Astro, modernización con branding estricto del cliente, estructura de referencia `labipac-front` (repo real del estudio), más una sección nueva de "trabajos realizados" (Content Collection, actualización semestral, cargada por Joaquín). WBS de 5 módulos (20h), R=45% → Tier 2 (15% descuento). Total presupuestado ≈ USD 370.
- Motivo: pedido explícito de Joaquín de armar el presupuesto para este cliente nuevo.
- Impacto en capas: Presentación únicamente — proyecto sin backend de negocio ni base de datos (excepción al patrón MVC habitual del estudio).
- Riesgos/supuestos: primer proyecto puramente front-end (sin cierre real de referencia) presupuestado en el estudio — declarado explícitamente en `4-presupuestador.md`. Quedan 2 dependencias bloqueantes antes de poder ejecutar con precisión: (1) assets de marca reales de Diercas (logo/paleta/tipografía), (2) confirmar el rubro/actividad real de Diercas para cerrar el conteo exacto de páginas institucionales (se usó `labipac-front`, 7 páginas, como ancla estructural). Hosting y mantenimiento quedaron fuera de este presupuesto, a definir aparte.

### 2026-07-30 16:00 - orquestador (analista-funcional / arquitecto-mvc / presupuesto-mvc)
- Etapa: Analisis → Arquitectura → Presupuesto (ajuste en cadena)
- Cambio: Joaquín compartió el brandbook real, el dossier corporativo y una presentación de arquitectura digital de Diercas SA. Esto **resolvió las 2 dependencias bloqueantes** declaradas en la entrada anterior: (1) el rubro real de Diercas es infraestructura de conectividad (Redes LAN, Fibra Óptica/FTTH) y Ciberseguridad, con clientes reales de sector público/privado/instituciones; (2) existe un brandbook real (logo "D" en gradiente cian→violeta, tipografía bold, fondo azul marino) con aplicaciones de marca ya definidas (firma de mail, social media, mailing). La estructura de páginas se recalculó de una analogía genérica (5 módulos, ~20h) a una estructura real basada en contenido (7 módulos, ~23h): 4 páginas institucionales simples + página de Servicios con 3 tablas técnicas + sección nueva "Clientes/Nodos de confianza" + formulario + blog/portfolio + deploy.
- Motivo: el cliente proveyó material real que reemplaza las hipótesis de la v1 del análisis.
- Impacto en capas: solo Presentación (sigue sin backend de negocio ni BD). Se revisó `C:\Users\joaco\Downloads` en busca de archivos adicionales del proyecto — no se encontró nada más allá de los 3 PDF ya recibidos (sin logo vectorial ni fuentes tipográficas todavía).
- Riesgos/supuestos: **Total actualizado de USD 370 a USD 425** (R bajó levemente de 45% a 43,5%, mismo Tier 2). Nueva dependencia: confirmar si la sección de clientes de referencia puede mostrar logos reales (autorización de terceros) o solo texto. Persiste la necesidad de archivos fuente editables del logo (vector/fuente tipográfica) para agilizar la implementación, aunque el brandbook PDF ya resuelve la ambigüedad de diseño.

### 2026-07-30 17:00 - analista-funcional
- Etapa: Analisis
- Cambio: Joaquín pasó la URL del sitio actual (`https://diercas.com.ar/`) — relevado vía WebFetch. Es un one-pager (Inicio/Servicios/Clientes/Contacto por anclas), sin formulario de contacto, con 14 logos de clientes ya publicados. Detectada discrepancia de posicionamiento: el sitio actual describe "venta de equipos, Informática + Audio/Video", mientras que el dossier/brandbook (más nuevos) posicionan a Diercas en Redes LAN/Fibra Óptica/Ciberseguridad institucional.
- Motivo: verificar el punto de partida real antes de cerrar el diseño — pedido implícito al compartir la URL.
- Impacto en capas: ninguno técnico — ajuste de alcance/contenido.
- Riesgos/supuestos: nueva dependencia bloqueante para Diseño (no resuelta unilateralmente): confirmar si Servicios mantiene 3 líneas (dossier, ya presupuestado) o suma Informática/Audio-Video del sitio viejo (5 líneas, requeriría re-cotización). Riesgo de autorización de logos de clientes bajó — ya es práctica existente en el sitio actual.

### 2026-07-30 18:00 - orquestador (cierre de presupuesto)
- Etapa: Presupuesto → Cierre (gate hacia Implementación)
- Cambio: **Cliente aprobó el presupuesto** — USD 425 desarrollo (pago 50%/50%) + **USD 400/año de mantenimiento** (hosting, SSL, dominio y actualización semestral del portfolio).
- Motivo: aprobación formal del cliente, habilita el inicio de Implementación según la secuencia obligatoria de `CLAUDE.md`.
- Impacto en capas: ninguno técnico todavía — gate administrativo. `presupuesto-cliente.md` actualizado con la tabla de mantenimiento (antes decía "se cotiza aparte").
- Riesgos/supuestos: la pregunta abierta sobre posicionamiento de Servicios (3 líneas del dossier vs. mantener también Informática/Audio-Video del sitio viejo) **sigue sin resolverse** — confirmar antes de arrancar Diseño de detalle, ya que puede ampliar el alcance ya aprobado. Repositorio del proyecto todavía no creado (candidato: `C:\Sistemas\diercas-front`).

### 2026-07-30 18:30 - analista-funcional
- Etapa: Analisis (preparación de reunión)
- Cambio: armado `cuestionario-reunion-inicial.md` — cuestionario multiple choice para cerrar en una sola reunión con Diercas todas las definiciones abiertas: posicionamiento de Servicios (3 vs 5 líneas), Nosotros/Sectores, Clientes/Nodos de confianza (logos vs texto, mismo listado de 14 o cambia), portfolio de trabajos (cantidad inicial, formato de material), contacto (destinatario, campos), marca (assets vectoriales, tipografía), hosting/dominio, cronograma.
- Motivo: pedido explícito de Joaquín — resolver todo lo pendiente en una sola instancia con el cliente en vez de rondas de preguntas sueltas.
- Impacto en capas: ninguno técnico — herramienta de discovery.
- Riesgos/supuestos: las respuestas de las preguntas 1.1/1.2 (posicionamiento de Servicios) son las que más pueden mover el presupuesto ya aprobado (USD 425) — si el cliente elige sumar Informática y/o Audio/Video, recalcular `4-presupuestador.md` antes de arrancar Diseño.

### 2026-08-13 12:00 - orquestador (aprobación confirmada, contenido real, plan de implementación)
- Etapa: Cierre de Presupuesto → preparación de Implementación (sin delegar todavía al subagent implementador, a pedido de Joaquín)
- Cambio: Joaquín confirmó que el cliente aprobó el presupuesto y trajo contenido real de negocio para cerrar el diseño antes de codear: 3 ramas de servicio en palabras del cliente (Infraestructura con OTDR/Fusionadora propios, Provisión de equipos/insumos, Infraestructura de eventos — esta última nueva, sin precedente en dossier ni sitio viejo), listado de clientes ampliado agrupado por rubro (suma Presidencia de la Nación, EDELP, LPRC, Colegio Patris, CAAITBA, Bodegón Urquiza, Flora Café, Lo de Edgardo, Hospitales), certificaciones RITE y QR Data Fiscal (investigadas — ambas son credenciales oficiales reales, no marketing: RITE es el registro de la Oficina Anticorrupción, Data Fiscal es el QR oficial de ARCA vía Formulario 960/D), confirmación de stack (Astro) y hosting (DonWeb), y destino exacto del formulario (no-reply@olvidata.com.ar → administracion@diercas.com.ar). Se relevó `C:\Sistemas\labipac-front` (base técnica real) confirmando el patrón reutilizable: `Layout.astro` compartido + páginas planas + endpoint `/api/contact.php`. Actualizados `1-analista-funcional.md`, `2-disenador-funcional.md` y `3-arquitecto-mvc.md` con el contenido real y un plan de implementación armado para confirmación de Joaquín (no se delegó a `agentes-ia-implementador` todavía, a pedido explícito).
- Motivo: el cliente proveyó insumos reales que reemplazan/resuelven en parte las hipótesis pendientes desde v3, y pidió research sobre cómo mostrar mejor esta información.
- Impacto en capas: solo Presentación (sigue sin backend de negocio ni BD, salvo el endpoint de contacto ya existente). Nueva Content Collection de Clientes.
- Riesgos/supuestos: **la discrepancia de posicionamiento de v3 no se resolvió, cambió de forma** — el cliente no mencionó Ciberseguridad ni Audio/Video al describir sus 3 ramas de énfasis; no se asume en ningún sentido, queda como bloqueo puntual de la página de Servicios hasta confirmación de Joaquín. Dos dependencias del cliente quedan explícitas y no bloqueantes para el resto del sitio: logo vectorial (Etapa 2, según el cliente) y QR Data Fiscal (a generar por el cliente desde ARCA).

### 2026-08-13 19:00 - implementador-dotnet (excepción de stack: Astro, no .NET)
- Etapa: Implementacion (Etapa 1)
- Cambio: Sitio Astro nuevo scaffoldeado en `C:\Sistemas\diercas-front` (Astro 7.2.2 + Tailwind v4, patrón técnico de `labipac-front` reutilizado y adaptado, no clonado). Implementadas las 5 páginas de Etapa 1 (Inicio, Nosotros con sección Certificaciones embebida, Servicios con 3 bloques + layout preparado para 4°/5° bloque futuro, Clientes vía Content Collection con 13 registros agrupados Público→Privado, Contacto con formulario `fetch` a `/api/contact.php`). Endpoint PHP de contacto adaptado (`server/api/contact.php`, `SmtpMailer.php` reutilizado sin cambios, `diercas_mail_cfg.php` con credenciales placeholder gitignoreadas). Build local limpio (`npm run build`, 5 páginas generadas sin errores).
- Motivo: ejecutar el alcance de Etapa 1 aprobado (USD 425), siguiendo instrucción explícita del orquestador de excluir Ciberseguridad/Audio-Video/QR Data Fiscal/Trabajos realizados (confirmado por el cliente el mismo día en `1-analista-funcional.md` v5).
- Impacto en capas: solo Presentación (Astro) + integración externa (PHP de contacto, fuera del build) — sin BD, sin Domain/Application/Infrastructure en sentido MVC, consistente con `3-arquitecto-mvc.md`.
- Riesgos/supuestos: copy de `/nosotros` es placeholder explícitamente marcado (el texto exacto del dossier corporativo no estaba disponible como cita literal en las definiciones del proyecto) — Joaquín debe reemplazarlo antes de publicar. Logo vectorial y logos de clientes siguen pendientes (Etapa 2, ya sabido). Credenciales SMTP y FTP DonWeb pendientes de Joaquín, documentadas en `README.md` del repo — no bloquean el cierre de esta etapa. Detalle completo en `5-implementador.md`.

## Historial de ajustes de alcance
- 2026-07-30: recibidos brandbook, dossier corporativo y presentación de Diercas SA — alcance de páginas pasa de analogía genérica (labipac-front, 5 módulos) a estructura real (7 módulos: Inicio/Nosotros/Sectores/Contacto + Servicios con 3 tablas técnicas + Clientes/Nodos de confianza + blog/portfolio). Total: USD 370 → USD 425.
- 2026-08-13: contenido real de negocio recibido post-aprobación — 3 ramas de servicio confirmadas por el cliente (distintas de las 3 del dossier: Infraestructura/Provisión de equipos/Eventos, no Redes LAN/Fibra/Ciberseguridad), clientes ampliados agrupados por rubro, certificaciones RITE+Data Fiscal nuevas. Sin cambio de precio todavía (el alcance de páginas no creció, cambió el contenido dentro de páginas ya presupuestadas) — a reevaluar si Ciberseguridad/Audio-Video se confirman como bloques adicionales.
