# Trazabilidad — contadores-bma-conversor

| Fecha | Etapa | Agente | Cambio | Notas |
|---|---|---|---|---|
| 2026-06-24 | Setup | — | Proyecto creado e incorporado al framework Agentes-IA | — |
| 2026-06-24 | Discovery/Análisis | analista-funcional | Discovery completo: 108 empleados, 122 conceptos, pivot tall→wide, solo Hoja2 del STR. Issue 4 (datos fijos empleado) pendiente. Stack: FastAPI + openpyxl + Passenger WSGI. | Ver definiciones/1-analista-funcional.md |
| 2026-06-25 | Implementación | implementador-php | Reescritura completa en PHP 8.3 + PhpSpreadsheet. Input: solo Grilla (reemplaza Cubo). Mapping completo cols 1-8 empleado desde Grilla. Conceptos por código. Totales calculados por Tipo de Concepto: TOTAL PROV, TOTAL CARGAS PROV, Redondeo, Neto a Cobrar. Estilos Excel: encabezados azules, zebra, freeze, autosize. | app/convert.php |
| 2026-06-25 | UI/UX | implementador-php | UI drag-and-drop. Footer patrón nav-logo OlvidataSoft (isotipo-color.svg + texto HTML). Logo fuente de verdad: C:\Sistemas\olvidatasoft-new. | app/index.php, app/static/ |
| 2026-06-25 | Documentación | documentador | Manual de usuario .md generado para entrega al cliente. | Docs/Manual de Usuario.md |
| 2026-06-25 | DevOps | implementador-php | Repo GitLab creado: gitlab.com/olvidata/conversor-bma.git. Commit inicial pusheado. .gitignore excluye vendor/, deploy.env, archivos de datos. | — |
| 2026-06-29 | Presupuesto | presupuestador | Presupuesto retroactivo ajustado. 3 módulos cobrables, 8h reales. Deploy elevado a 3h. Descuento referido 15%. Total USD 199 (bruto USD 234 − USD 35 descuento). Hosting sin cargo (servidor existente contadoresbma.com.ar). | Ver definiciones/4-presupuestador.md |
| 2026-06-29 | Documento funcional | documentador | Documento funcional del sistema generado. Flujo, archivos de entrada/salida, reglas de negocio, UI, specs técnicas, presupuesto cliente. | Ver documento-funcional.md |
| 2026-07-23 | Corrección (barrido cross-proyecto) | orquestador | `documento-funcional.md` describía el diseño original de 3 archivos de entrada (Informe jerárquico + Grilla + Cubo), contradiciendo la reescritura del 2026-06-25 (solo Grilla) ya registrada en esta misma tabla y en `Docs/Manual de Usuario.md` del repo del proyecto. Corregidas las secciones 1.3, 2, 3, 4.2, 4.4, 5 y 6 para reflejar el único archivo de entrada real. Se dejó pendiente de QA la verificación de columnas calculadas (Total haberes, Base Imponible, Neto, Bruto, Retenciones) que el Manual de Usuario no confirma explícitamente. | Ver documento-funcional.md §1.3/§3/§4/§5/§6 |
