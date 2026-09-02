---
name: project-ipac
description: "IPAC Laboratorio website — Astro project details, branding, stack, and page inventory"
metadata: 
  node_type: memory
  type: project
  originSessionId: 88aeb0ce-6964-439b-afd0-5f1c0b5731dc
---

# IPAC Laboratorio – labipac-front

**Stack:** Astro + Tailwind CSS v4 (via @tailwindcss/vite), TypeScript strict, static output.

**Branding:**
- Full name: Instituto Privado de Análisis Clínicos
- Short name: IPAC
- Address: Calle 12 N° 1088, 1er Piso, La Plata, Buenos Aires
- Phone: (0221) 444-4444 (placeholder — update when real number provided)
- Email: info@ipac.com.ar (placeholder)
- Hours: Mon–Fri 7:00–19:00 / Sat 7:00–12:00

**Design system:** Dark navy (#0a1628) primary, electric cyan (#00d4ff) accent, glass morphism cards, CSS grid background texture, glow effects via box-shadow.

**Pages built:**
- `/` — Home (hero, stats, about, services grid, CTA banner, location)
- `/servicios` — Full analysis catalog by category
- `/equipamiento` — Equipment by category (MALDI-TOF, HPLC, etc.)
- `/indicaciones` — Pre-test patient instructions by sample type
- `/contacto` — Contact info + inquiry form
- `/turnos` — Appointment request form
- `/resultados` — Results access form (sample # + DOB)

**Why:** Migration from old site at ipac.com.ar (Neuquén-based) to a new La Plata identity. The user wants a modern, technological UX.

**How to apply:** All future additions should use the existing design tokens in global.css (.glass, .card-service, .btn-primary, .btn-outline, .gradient-text, .glow-accent, .grid-bg). The Layout.astro navbar auto-scrolls and has a mobile menu.
