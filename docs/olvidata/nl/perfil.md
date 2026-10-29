# Perfil de Instagram NL: configuración completa

La cuenta en inglés dirigida a Países Bajos. Este documento sale de
`docs/olvidata/marca/posicionamiento-nl.md` (§ 2 propuesta, § 3 voz, § 6 canal, § 7 legal). Creado el
2026-10-29. Todo lo que dice **pendiente** es un dato que el repo no tiene y que no se inventa.

**Decisión de fondo:** el perfil dice desde dónde trabajamos. No hay dirección, número ni dominio
holandés. Instagram muestra igual el país de la cuenta en *About this account*: si dijera otra cosa,
el perfil se contradiría solo.

## 1. Cuenta

| Campo | Valor | Nota |
|---|---|---|
| Tipo | **Cuenta profesional → Business** (no Creator) | Business es la que permite botones de contacto y vincularse a la cartera de Meta Business para pautar |
| Usuario | **pendiente de disponibilidad**. Orden de preferencia: `@olvidata.studio` → `@olvidatasoft` → `@olvidata.en` | `@olvidata.soft` es la cuenta en castellano y no se toca. Evitar `nl` en el handle: la cuenta es en inglés y después sirve también para Suiza |
| Privacidad | Pública | |
| Seguridad | Autenticación en dos pasos con app (no SMS) | La cuenta va a tener pauta vinculada |
| Cuenta vinculada | Misma cartera de Meta Business que `@olvidata.soft`, con una **página de Facebook propia en inglés** | Separar la página evita mezclar idioma y reseñas entre mercados |

## 2. Lo que se ve en el perfil

**Foto:** el isotipo con anillo de color (`04_isotipo_con_anillo_color.png`, assets de marca en
`BotPublicitario\Veo\reference_photos\logo-olvidata\`), sobre navy `#0c1424`. Es la misma foto que la
cuenta ES: la marca es una sola.

**Nombre** (es campo de búsqueda, máximo 30 caracteres):

```
Olvidata · Custom Software
```

**Categoría:** `Software Company`. Se muestra en el perfil.

**Bio** (133 de 150 caracteres):

```
Custom business software & AI agents for SMEs.
Built by Joaquín, from Argentina 🇦🇷 · 4–5 h overlap with CET.
Build your own Software.
```

Por qué está escrita así:

- La primera línea dice qué hacemos, con las palabras que busca un holandés.
- La segunda cumple con decir quién está detrás y desde dónde (§ 7, transparencia de origen) y
  convierte la distancia en un argumento: el solapamiento horario.
- La tercera es el slogan de marca, sin traducir ni tocar (`MARCA.md` § 2).
- No hay precio, ni "DM for a quote", ni "link in bio to buy". El perfil tampoco vende.

**Pronombres:** ninguno.

**Link** (uno solo, en la bio):

| Etiqueta | Destino | Estado |
|---|---|---|
| `Work, contact & legal` | Página en inglés del sitio (`olvidatasoft-new`, por ejemplo `/en`) con: los casos operando, el formulario de contacto con **consentimiento GDPR explícito**, el link a Calendly para la demo, la **política de privacidad** y los **datos del titular** (nombre legal, país Argentina, email verificable) | **pendiente: la página `/en` no existe.** Se pide a `agentes-ia-implementador-astro-front`. Hasta que exista, el perfil no se pauta |

No usar Linktree: la página propia es la que cumple con identificar al titular y con el GDPR en el
mismo lugar.

## 3. Botones de contacto

| Botón | Configuración | Motivo |
|---|---|---|
| Email | **pendiente: email de dominio propio** (no Gmail) | Para un primer contacto profesional en NL, el email es lo esperado (§ 6) |
| Teléfono / WhatsApp | **Apagado** | En NL no se abre por WhatsApp. Se ofrece solo si el prospecto lo pide (§ 6) |
| Dirección | **No mostrar** | No hay dirección en NL y no se inventa. La de Argentina no le aporta nada a un holandés y sí expone datos |
| Botón de acción | Ninguno al principio | "Book now" en el perfil es CTA de venta. La demo se agenda desde la página `/en` |

## 4. Mensajes directos (DM)

- **Preguntas frecuentes** (se muestran al abrir un chat nuevo, en inglés):
  1. *What kind of software do you build?*
  2. *How does working with a studio in Argentina work?*
  3. *Can I see a system running?*
- **Respuestas guardadas:** las escribe `olvidata-traductor` a partir de las de la cuenta ES. Ninguna
  lleva precio: el precio en EUR está pendiente en `decisiones.md` DEC-010.
- **Respuesta automática (Meta Business Suite → Inbox):** una línea que avisa el horario (CET y ART) y
  que contesta Joaquín en persona. No poner bot de ventas en NL hasta que el ladder de § 6 esté
  operando con consentimiento.
- Cualquier dato de un lead de NL **no se carga al CRM** sin consentimiento registrado (§ 7).

## 5. Destacadas (stories fijadas)

Cuatro, con portadas en el mismo sistema visual de la cuenta ES (navy, acento `#2B9DE4`, ícono
lineal):

| Destacada | Contenido |
|---|---|
| `Work` | Los casos operando: NL-002, NL-004 y NL-005 del feed |
| `AI Agents` | El estudio contable con tres agentes andando. Solo resultado, nunca el método (COM-004) |
| `About` | Quién soy, desde dónde, en qué horario, cómo se trabaja a distancia, en qué idioma |
| `FAQ` | Contrato, propiedad del código, soporte, GDPR. **Sin precios** |

El contenido de cada story lo produce `olvidata-cm` y lo adapta `olvidata-traductor`.

## 6. Publicaciones fijadas (las 3 de arriba de la grilla)

1. **Presentación:** quién soy, desde dónde y qué construyo, mostrando un sistema andando. Es la
   única pieza nueva que necesita la cuenta antes de arrancar. **Pendiente de producir por
   `olvidata-cm`**, con apertura de concepto y no de dolor, y sin venta.
2. **NL-002:** el Reel de la ferretería, con el producto operando.
3. **NL-001:** el carrusel *A prompt is not a rule*, el argumento del Second Brain.

## 7. Meta Business y pauta (configurar, sin encender)

| Ítem | Configuración | Estado |
|---|---|---|
| Cuenta publicitaria | **Nueva, en EUR**, zona horaria `Europe/Amsterdam` | Separada de la cuenta en ARS, para que el costo por mercado se lea sin conversiones. A crear |
| Verificación del negocio | Completar en Business Suite con los datos reales (Argentina) | pendiente |
| Beneficiario y pagador (UE) | Meta lo exige en todo anuncio que llegue a la UE: se declara Olvidata como beneficiario y quien paga | se completa al crear el primer ad set |
| Geo | Ciudades de NL con pin y radio, **verificado releyendo el ad set**. Destildar *"reach more people likely to respond"* | En AR se fue el 35–52 % del gasto fuera de zona por no hacer esto (`olvidata-cm.md` § Meta Ads) |
| Advantage+ Creative | *Translations* **apagado**, y todo lo que cambia qué dice la pieza también | La traducción la hace `olvidata-traductor` |
| Encendido | **No.** Lo firma `olvidata-ceo` y el gasto espera la confirmación de Joaquín | Requisitos previos: página `/en` andando, al menos 6 piezas en la grilla, DEC-010 resuelta |

## 8. Checklist de alta (en este orden)

- [ ] Elegir el usuario disponible (§ 1) y crear la cuenta Business
- [ ] 2FA, foto, nombre, categoría, bio (§ 2)
- [ ] Email de dominio propio y botones (§ 3)
- [ ] Página de Facebook en inglés y vinculación a la cartera de Meta Business
- [ ] Página `/en` del sitio con privacidad, titular y formulario con consentimiento (implementador astro)
- [ ] Link en la bio (§ 2)
- [ ] Preguntas frecuentes de los DM y respuesta automática (§ 4)
- [ ] Pieza de presentación (cm) y las primeras 6 piezas del feed traducidas y **aprobadas** (`feed.md`)
- [ ] Cuatro destacadas (§ 5) y tres fijadas (§ 6)
- [ ] Cuenta publicitaria en EUR y verificación del negocio (§ 7)
- [ ] DEC-010 (precio en EUR) resuelta por `olvidata-ceo` antes de la primera demo
