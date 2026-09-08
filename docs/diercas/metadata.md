# Metadata del proyecto

- nombre: Diercas SA (sitio institucional)
- fecha_inicio: 2026-07-30
- estado: **Desarrollo cerrado 2026-09-08, aprobado por el cliente.** Etapa 1 (sitio institucional, 5 paginas) y Etapa 2 ("Trabajos realizados") completas y en produccion. Dominio real ya migrado: el sitio esta en vivo en https://diercas.com.ar (hosting Hostinger, administrado por el propio Diercas; DonWeb descartado). Formulario de contacto migrado a casilla propia del cliente (no-reply@diercas.com.ar via smtp.hostinger.com, auth SMTP verificada en vivo). **Item abierto en produccion:** tras la migracion de dominio falta recrear `storagedir/` (4 archivos del backend de correo) un nivel arriba del document root nuevo — solo se puede via hPanel; hasta entonces el formulario responde 500. Otros pendientes sin definicion, a cargo del cliente: logos de varios clientes y fechas/nombre institucional de 2 de los 4 casos de Trabajos. Detalle en trazabilidad.md (entrada 2026-09-08).
- owner: Joaquín Bourdin (OlvidataSoft)
- descripcion: Modernización del sitio web institucional de Diercas SA — front estático en Astro, siguiendo estrictamente el branding/assets de marca provistos por el cliente, con estructura de referencia similar a `labipac-front`, más un blog/portfolio de trabajos realizados con actualización cada 6 meses (cargado por Joaquín, contenido provisto por el cliente).
- ruta_definiciones: /docs/diercas/definiciones
- ruta_repositorio: `C:\Sistemas\diercas-front` (creado 2026-08-13, workspace `C:\Sistemas\Diercas.code-workspace` vinculado a `Agentes-IA`)

## Archivos de memoria por agente
- analista-funcional: /docs/diercas/definiciones/1-analista-funcional.md
- disenador-funcional: /docs/diercas/definiciones/2-disenador-funcional.md
- arquitecto-mvc: /docs/diercas/definiciones/3-arquitecto-mvc.md
- presupuestador: /docs/diercas/definiciones/4-presupuestador.md
- implementador: /docs/diercas/definiciones/5-implementador.md
- qa: /docs/diercas/definiciones/6-qa.md
- documentador: /docs/diercas/definiciones/7-documentador.md
