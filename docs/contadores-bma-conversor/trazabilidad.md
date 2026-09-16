# Trazabilidad - contadores-bma-conversor

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-06-24
- Etapa: Setup
- Cambio: Proyecto creado e incorporado al framework Agentes-IA

### 2026-06-24 - analista-funcional
- Etapa: Discovery/Análisis
- Cambio: Discovery completo: 108 empleados, 122 conceptos, pivot tall→wide, solo Hoja2 del STR. Issue 4 (datos fijos empleado) pendiente. Stack: FastAPI + openpyxl + Passenger WSGI.
- Notas: Ver definiciones/1-analista-funcional.md

### 2026-06-25 - implementador-php
- Etapa: Implementación
- Cambio: Reescritura completa en PHP 8.3 + PhpSpreadsheet. Input: solo Grilla (reemplaza Cubo). Mapping completo cols 1-8 empleado desde Grilla. Conceptos por código. Totales calculados por Tipo de Concepto: TOTAL PROV, TOTAL CARGAS PROV, Redondeo, Neto a Cobrar. Estilos Excel: encabezados azules, zebra, freeze, autosize.
- Notas: app/convert.php

### 2026-06-25 - implementador-php
- Etapa: UI/UX
- Cambio: UI drag-and-drop. Footer patrón nav-logo OlvidataSoft (isotipo-color.svg + texto HTML). Logo fuente de verdad: C:\Sistemas\olvidatasoft-new.
- Notas: app/index.php, app/static/

### 2026-06-25 - documentador
- Etapa: Documentación
- Cambio: Manual de usuario .md generado para entrega al cliente.
- Notas: Docs/Manual de Usuario.md

### 2026-06-25 - implementador-php
- Etapa: DevOps
- Cambio: Repo GitLab creado: gitlab.com/olvidata/conversor-bma.git. Commit inicial pusheado. .gitignore excluye vendor/, deploy.env, archivos de datos.

### 2026-06-29 - presupuestador
- Etapa: Presupuesto
- Cambio: Presupuesto retroactivo ajustado. 3 módulos cobrables, 8h reales. Deploy elevado a 3h. Descuento referido 15%. Total USD 199 (bruto USD 234 − USD 35 descuento). Hosting sin cargo (servidor existente contadoresbma.com.ar).
- Notas: Ver definiciones/4-presupuestador.md

### 2026-06-29 - documentador
- Etapa: Documento funcional
- Cambio: Documento funcional del sistema generado. Flujo, archivos de entrada/salida, reglas de negocio, UI, specs técnicas, presupuesto cliente.
- Notas: Ver documento-funcional.md

### 2026-07-23 - orquestador
- Etapa: Corrección (barrido cross-proyecto)
- Cambio: `documento-funcional.md` describía el diseño original de 3 archivos de entrada (Informe jerárquico + Grilla + Cubo), contradiciendo la reescritura del 2026-06-25 (solo Grilla) ya registrada en esta misma tabla y en `Docs/Manual de Usuario.md` del repo del proyecto. Corregidas las secciones 1.3, 2, 3, 4.2, 4.4, 5 y 6 para reflejar el único archivo de entrada real. Se dejó pendiente de QA la verificación de columnas calculadas (Total haberes, Base Imponible, Neto, Bruto, Retenciones) que el Manual de Usuario no confirma explícitamente.
- Notas: Ver documento-funcional.md §1.3/§3/§4/§5/§6

### 2026-08-20 - orquestador (directo, sin subagents .NET — proyecto es PHP)
- Etapa: Bugfix
- Cambio: Empresa San Bruno: columnas Lugar de Pago/CC/Obra Social vacías en el output (STR sí funcionaba). Causa: `convert.php` leía la Grilla por índices de columna fijos (4/10/19/30), pero el layout de columnas del export de Grilla es configurable por empresa en Bejerman Web y difiere entre STR y San Bruno — el legajo de San Bruno caía en una columna no numérica y el lookup no matcheaba nunca. Fix: nueva función `findColByHeader()` resuelve las columnas por texto del header (fila 1) en vez de índice fijo. Verificado con los archivos reales de San Bruno (`Docs/Informe de Liquidación.xls` + `Docs/Grilla...xlsx` + `Docs/Cubo...xlsx`): Lugar de Pago y CC ya se completan. Obra Social queda vacía porque el export de Grilla de San Bruno no tiene esa columna (dato ausente en origen, no bug) — pendiente confirmar con cliente si "Sindicato" debe usarse como proxy.
- Notas: `app/convert.php`, ver mapeo-archivos.md §2
