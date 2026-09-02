# Memoria - Analista funcional

## Proyecto: kite-punta-lara
## Ultima actualizacion: 2026-09-01

## Definiciones vigentes

### Modulos/features analizados
- Pronóstico de viento y "días de kite" para el spot de Punta Lara (Club Universitario, sede náutica, Ensenada). Etapa: **Análisis cerrado** (Discovery + Análisis en una sola etapa, 3 rondas de preguntas resueltas el mismo día).

### Investigación de dominio
**CARP (Comisión Administradora del Río de la Plata)**: portal comisionriodelaplata.org/servicios_main.php?sid=VM. Publica viento en vivo (nudos, UTC-3) de estaciones del Canal Martín García (Pilote Norden, Colonia, Conchillas, Carmelo), dato crudo sin procesar. Estas estaciones están del lado uruguayo/zona del canal, no en Punta Lara — la estación exacta que mira el cliente queda para confirmar en Arquitectura (endpoint concreto).

**SHN (Servicio de Hidrografía Naval)**: portal hidro.gob.ar. Fuerte en pronóstico mareológico y altura de agua del Río de la Plata (incluye La Plata). No se confirmó endpoint de viento en tiempo real específico — su aporte principal es altura de agua/marea, relevante para la señal de sudestada/bajante.

**SMN (Servicio Meteorológico Nacional)**: API no oficial en ws.smn.gob.ar (sin documentación formal, sin garantía de estabilidad). Endpoint de referencia: /map_items/weather. Estación de referencia probable: Aeropuerto La Plata.

**Open-Meteo**: API gratuita, sin key, expone modelos globales (GFS/ICON/otros). **Fuente de pronóstico multi-modelo confirmada para el MVP**, en reemplazo del "promedio de modelos" manual que el cliente hace hoy en Windguru (Windguru no tiene API pública de pronóstico — solo una Upload API para estaciones propias y widgets pagos).

**Sudestada**: viento sostenido del sudeste >~50 km/h, 24-72hs, por anticiclón en Patagonia/Mar Argentino + baja presión al sur del litoral/oeste de Uruguay. Sube el nivel del río (hasta ~3m en casos extremos), suele venir con lluvia/tormenta. Más frecuente en primavera/otoño.

**Birazón**: sin definición formal en fuentes oficiales (SMN/SHN) — término local de club. El cliente confirmó que engloba dos fenómenos que se plantearon como alternativos: brisa de calma (tipo térmica invertida) y bajante del río por viento sostenido de un sector. Confirmado que son **dos señales independientes**, no una cadena causa-efecto.

**Spot Punta Lara / Club Universitario**: dirección más consistente y segura: sudeste (cross-onshore). Velocidad típica 10-18 nudos. Agua poco profunda y plana (sedimento del río) — bueno para freestyle/principiantes. Mejor temporada: primavera/principio de verano (térmicas más confiables). Mejores horarios: mediodía y tarde.

### Reglas funcionales acordadas
- **Fuente de pronóstico**: Open-Meteo como fuente principal del MVP. Windy API queda documentada como fallback futuro (no implementado en el MVP). Scraping de Windguru queda documentado como tercera opción de último recurso (no implementado en el MVP).
- **Usuarios**: multiusuario, registro abierto (email/contraseña, sin aprobación manual).
- **Acceso al dashboard de pronóstico (CU-01/CU-03)**: público, sin login. Se pide cuenta solo para la recomendación de equipo personalizada y la bitácora (CU-02, CU-04, CU-06).
- **Definición de "navegable"**: recomendación de equipo (tamaño de kite), no un simple sí/no, usando una tabla nudos→metros de kite por usuario.
- **Tabla de equipo (quiver)**: arranca con una tabla default (la del cliente) que cada usuario nuevo puede clonar y editar.
- **Birazón**: dos señales independientes en el modelo de cálculo — (a) posible brisa de calma, (b) posible bajante por viento sostenido de un sector — cada una se muestra y pesa por separado, no como una única regla secuencial.
- **Sudestada**: se usa como oportunidad condicional — el modelo distingue "sudestada con temporal asociado" (no recomendable) de "viento del SE fuerte y sostenido sin mal tiempo" (recomendable, con equipo más chico).
- **Historial**: con bitácora — registro por usuario de fecha, fui/no fui, nudos reales medidos (opcional). Sirve para calibrar el modelo con el tiempo y como bitácora social visible para todo el club.
- **Notificaciones**: proactivas por email cuando el modelo detecta un "día de kite" dentro del horizonte de pronóstico.
- **Horizonte de pronóstico**: hoy + 3 días.
- **Hosting**: subdominio nuevo dedicado en DonWeb (PHP), proyecto independiente.

### Criterios de aceptacion vigentes
- **CU-01** (consultar pronóstico): dado un día dentro de la ventana de 3 días, se muestra viento (nudos + dirección) y una recomendación de equipo (tamaño de kite) o "no navegable" si está fuera de rango; si hay señal de birazón (brisa de calma y/o bajante) o de sudestada activa, se muestra explícitamente junto con su interpretación (oportunidad/riesgo), de forma pública sin necesidad de login.
- **CU-02** (perfil/equipo): un usuario nuevo ve la tabla default precargada al registrarse y puede clonarla/editarla; sus cambios quedan asociados a su cuenta y afectan la recomendación que ve en CU-01 una vez logueado.
- **CU-03** (viento en vivo): se muestra el último dato disponible de cada estación configurada (CARP/SHN/SMN) con timestamp de la lectura; si una fuente no responde, se marca como "no disponible" sin romper el resto de la pantalla.
- **CU-04** (bitácora): un usuario logueado puede cargar una sesión (fecha hoy o pasada — nunca futura), con fui/no fui y nudos reales opcionales; el registro queda visible en su historial personal y en la bitácora social (CU-06).
- **CU-05** (notificación): cuando el score del modelo supera el umbral de "día de kite" para algún día del horizonte de 3 días, se dispara un email a los usuarios registrados.
- **CU-06** (bitácora social): lista de sesiones cargadas por todos los usuarios, ordenada por fecha, visible para cualquier usuario logueado.

### Supuestos y dependencias
- CARP, SHN y SMN no tienen API oficial documentada ni estabilidad garantizada — cada fuente debe poder fallar de forma aislada sin romper el resto del dashboard (ya reflejado en CU-03).
- Open-Meteo es la única fuente de pronóstico confirmada para el MVP. Su resolución de grilla cerca de la costa puede ser más gruesa que lo que el cliente obtiene hoy promediando modelos a mano en Windguru — se recomienda una validación empírica corta (comparar Open-Meteo vs. Windguru real durante algunas semanas) antes de dar la fuente por definitiva; si no alcanza, ahí se activan los fallbacks ya documentados (Windy API, scraping Windguru).
- Los umbrales de las reglas de birazón y sudestada nacen de research bibliográfico general, no de datos duros de Punta Lara — el modelo inicial es una aproximación que la bitácora (CU-04) permite ir calibrando con la realidad del spot.
- Registro abierto sin aprobación manual: cualquiera con el link puede crear cuenta y ver la bitácora social del club. Riesgo bajo dado el contexto (grupo chico, sin datos sensibles), a revisar si el sitio se difunde más de lo esperado.
- No hay agente implementador PHP en el catálogo del estudio (default es .NET MVC; alternativa existente es Astro estático) — Arquitectura/Presupuesto deben definir el enfoque técnico sin la plantilla BlankProject habitual.

### Exclusiones confirmadas
- Multi-spot: fuera de alcance, queda acotado a Punta Lara/Club Universitario.
- Implementación real de Windy API y scraping de Windguru: documentados como fallback futuro, no se implementan en el MVP.
- App móvil nativa: fuera de alcance, es sitio web.
- Aprobación manual de altas de usuario / panel de moderación: fuera de alcance, el registro es abierto.
- Notificación por WhatsApp/push: fuera de alcance del MVP (se eligió email).

### Perfil de cliente
No aplica clasificación B2B/B2C — proyecto de uso personal de Joaquín, extendido a uso compartido con el grupo del club, sin venta ni presupuesto a terceros.

## Banderas tempranas
- Migración de esquema / base de datos: **SÍ** — usuarios, tabla de equipo por usuario, bitácora de sesiones. (El stack es PHP/DonWeb, no .NET/EF Core — se documentará como migración de esquema en Arquitectura, no como migración EF literal.)
- Integración externa: **SÍ, múltiple** — CARP, SHN, SMN, Open-Meteo (implementadas en el MVP); Windy API y scraping de Windguru quedan documentados como fallback futuro no implementado.
- Máquina de estados: **NO** — es un sistema de cálculo/scoring, no de flujo de estados de negocio.

## Historial de ajustes
- 2026-09-01: Alta de proyecto. Discovery + investigación de dominio completa (CARP, SHN, SMN, Open-Meteo/Windguru, birazón, sudestada, spot). 3 rondas de preguntas al cliente (9 + 4 + 2 decisiones) resueltas el mismo día. Análisis funcional cerrado: alcance, 6 casos de uso con criterios de aceptación, permisos/validaciones, riesgos/supuestos y banderas tempranas definidos. Gate habilitado: queda lista para Diseño funcional.
