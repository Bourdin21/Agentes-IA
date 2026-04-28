# Manual de uso - Agentes-IA OlvidataSoft

Guia practica para procesar un proyecto/feature de punta a punta usando los 7 agentes definidos en `.github/agents/`.

## 1. Antes de empezar

Verificar que el repo destino tenga:
- `.github/copilot-instructions.md` y `.github/instructions/` copiados.
- VS Code con Copilot Chat habilitado.
- `configs/github-copilot/settings.json` aplicado en `.vscode/settings.json`.

Y en este repo (Agentes-IA):
- Carpeta del proyecto en `/docs/<proyecto>/` con `metadata.md`, `trazabilidad.md` y `definiciones/`.
- Si no existe, copiar desde `/docs/templates/proyecto/`.

## 2. Mapa rapido de agentes

| # | Agente | Archivo de salida en `/docs/<proyecto>/definiciones/` | Modo |
|---|--------|--------------------------------------------------------|------|
| 1 | Analista funcional | `1-analista-funcional.md` | Ask |
| 2 | Disenador funcional | `2-disenador-funcional.md` | Ask |
| 3 | Arquitecto MVC | `3-arquitecto-mvc.md` | Ask |
| 4 | Presupuestador | `4-presupuestador.md` | Ask |
| 5 | Implementador .NET | `5-implementador.md` | Agent |
| 6 | QA | `6-qa.md` | Agent |
| 7 | Documentador | `7-documentador.md` | Ask |

Regla de oro: **no se inicia una etapa hasta que la anterior haya cerrado su archivo**.

## 3. Flujo paso a paso

### Paso 1 - Analista funcional (Discovery + Analisis)
- Invocar: `@1 - analista-funcional`
- Input: pedido del cliente, `metadata.md`, `trazabilidad.md`.
- Pedirle: alcance, casos de uso, **criterios de aceptacion**, permisos/estados/validaciones, banderas tempranas (EF si/no, integracion si/no, maquina de estados si/no).
- Cierre: el agente actualiza `1-analista-funcional.md` y registra entrada en `trazabilidad.md`.
- Gate: revisar y aprobar antes de seguir.

### Paso 2 - Disenador funcional
- Invocar: `@2 - disenador-funcional`
- Input: `1-analista-funcional.md` aprobado.
- Pedirle: flujo de pantallas, ViewModels, **maquina de estados** (tabla origen/evento/destino/guarda/accion/error), reglas y permisos por accion, plan funcional para el arquitecto.
- Cierre: actualiza `2-disenador-funcional.md` + trazabilidad.

### Paso 3 - Arquitecto MVC
- Invocar: `@3 - arquitecto-mvc`
- Input: 1 y 2 aprobados.
- Pedirle: impacto por capa (Domain/Application/Infrastructure/Web), modelo de permisos, migraciones EF si/no, riesgos.
- Cierre: actualiza `3-arquitecto-mvc.md`.

### Paso 4 - Presupuestador
- Invocar: `@4 - presupuestador`
- Input: 1, 2 y 3 aprobados.
- Pedirle: tabla por modulo funcional con O/M/P, PERT, contingencia, horas finales y USD a tasa vigente; bloque de autocorreccion contra historicos.
- Entregar al cliente y obtener aprobacion **antes** de implementar.

### Paso 5 - Implementador .NET (Agent mode)
- Invocar: `@5 - implementador`
- Input: 2, 3 y 4 aprobados.
- Pedirle: plan tecnico por etapas, cambios por capa, migraciones EF si aplica, **evidencia de build y pruebas minimas**.
- Cierre: actualiza `5-implementador.md`.

### Paso 6 - QA (Agent mode)
- Invocar: `@6 - QA`
- Input: 1 (criterios), 2 (maquina de estados) y 5 (cambios).
- Pedirle: cobertura PASS/FAIL/BLOCKED por criterio, recorrido de transiciones validas e invalidas, defectos con severidad, riesgos de release.
- Gate: no documentar al cliente hasta que QA apruebe.

### Paso 7 - Documentador
- Invocar: `@7 - documentador`
- Input: 5 y 6.
- Pedirle: resumen ejecutivo en una pagina, sin tecnicismos, solo lo entregado y validado.

### Paso 8 - Cierre de calibracion (lo hace el presupuestador)
- Reinvocar `@4 - presupuestador` al cierre del sprint.
- Pedirle: tabla horas estimadas vs reales, desvio %, ratios observados y acciones de recalibracion sobre `27-presupuesto-parametros.instructions.md` si el desvio promedio supera 20%.

## 4. Como invocar un agente en Copilot Chat

1. Abrir Copilot Chat.
2. Escribir `@` y elegir el agente por nombre (ej: `@1 - analista-funcional`).
3. Adjuntar archivos relevantes con `#file:` (ej: `#file:docs/<proyecto>/definiciones/1-analista-funcional.md`).
4. Enviar el pedido funcional concreto.
5. Revisar la salida contra la **Salida minima** del `.agent.md` correspondiente.

## 5. Plantilla de pedido al agente

```
Proyecto: <nombre>
Etapa: <numero y nombre>
Contexto: <breve, 2-4 lineas>
Inputs:
- <archivo o decision previa>
Pedido concreto:
- <que se necesita resolver>
Restricciones / supuestos:
- <si aplica>
```

## 6. Reglas a no romper

- Una etapa, un agente, un archivo de salida.
- Cada ajuste registra entrada en `trazabilidad.md`.
- Si cambia el alcance: volver al agente 1 y bajar en cascada.
- Migracion EF se declara en analista (bandera) y se confirma en arquitecto.
- Contingencia: una sola vez en toda la cadena (no doble).
- Tarifa vigente: USD 14/h salvo aprobacion explicita por debajo.

## 7. Checklist por sprint

- [ ] `1-analista-funcional.md` con criterios de aceptacion.
- [ ] `2-disenador-funcional.md` con maquina de estados (si aplica).
- [ ] `3-arquitecto-mvc.md` con permisos y EF declarado.
- [ ] `4-presupuestador.md` con autocorreccion historica + aprobacion del cliente.
- [ ] `5-implementador.md` con build OK y pruebas minimas.
- [ ] `6-qa.md` con cobertura PASS/FAIL por criterio.
- [ ] `7-documentador.md` listo para enviar al cliente.
- [ ] `4-presupuestador.md` actualizado con cierre de calibracion estimado vs real.
- [ ] `trazabilidad.md` con entradas por cada paso.

## 8. Referencias

- Reglas globales: [.github/instructions/00-operativa-global.instructions.md](../.github/instructions/00-operativa-global.instructions.md)
- Fronteras por capa: [.github/instructions/01-fronteras-por-capa.instructions.md](../.github/instructions/01-fronteras-por-capa.instructions.md)
- Trazabilidad documental: [.github/instructions/29-trazabilidad-conversacion.instructions.md](../.github/instructions/29-trazabilidad-conversacion.instructions.md)
- Checklists tecnicos: [.github/instructions/26-checklists.instructions.md](../.github/instructions/26-checklists.instructions.md)
- Tarifas y rangos: [.github/instructions/27-presupuesto-parametros.instructions.md](../.github/instructions/27-presupuesto-parametros.instructions.md)
- Metodo PERT y calibracion: [.github/instructions/28-estimacion-avanzada.instructions.md](../.github/instructions/28-estimacion-avanzada.instructions.md)
