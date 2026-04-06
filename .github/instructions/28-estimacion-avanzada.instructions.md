---
description: Metodo avanzado de estimacion para presupuestos mas asertivos en cambios MVC + EF Core + MySQL.
applyTo: "**/*.{md,prompt.md,agent.md,instructions.md}"
---

# Objetivo
- Reducir desvio entre horas estimadas y horas reales.
- Entregar presupuesto en rango (no punto unico) cuando exista incertidumbre.
- Estandarizar supuestos, exclusiones y gatillos de reestimacion.

# Metodo obligatorio de estimacion

## 1) Descomposicion minima (WBS)
- Toda estimacion debe separarse por item funcional de negocio (no por capa tecnica).
- Cada item debe incluir al menos: analisis, implementacion, pruebas, documentacion.

## 2) Tres puntos por item (PERT)
- O (optimista): mejor caso realista.
- M (mas probable): caso esperado con contexto actual.
- P (pesimista): caso adverso razonable, sin eventos catastroficos.
- Estimacion esperada por item: (O + 4M + P) / 6.

## 3) Riesgo y contingencia variable
- Riesgo bajo: +8%.
- Riesgo medio: +15%.
- Riesgo alto: +25%.
- No usar contingencia fija para todos los proyectos.

## 4) Seleccion del nivel de riesgo
- Bajo: alcance estable, sin integraciones externas, sin migracion de datos.
- Medio: cambios en reglas de negocio, validaciones, o multiples modulos acoplados.
- Alto: integraciones externas, migraciones complejas, estados criticos, legado inestable.

## 5) Conversion a costo
- Horas finales = suma PERT por item + contingencia por riesgo.
- Costo = horas finales x tasa vigente (ver 27-presupuesto-parametros).

# Formato de entrega de presupuesto
- Mostrar por item funcional: O, M, P, horas PERT, riesgo, horas finales, USD.
- Incluir explicitamente:
- Supuestos.
- Exclusiones.
- Dependencias del cliente.
- Criterios de aceptacion minimos.

# Gatillos de reestimacion obligatoria
- Cambio de alcance funcional.
- Cambio de reglas de negocio o permisos.
- Aparicion de integracion externa no relevada.
- Necesidad de nuevas migraciones EF no contempladas.

# Seguimiento y calibracion
- Registrar por cada item: horas estimadas, horas reales, desvio porcentual.
- Revisar calibracion cada 3 meses o cada 5 presupuestos cerrados.
- Si el desvio promedio absoluto supera 20%, recalibrar rangos por tipo de modulo.

# Reglas practicas para asertividad
- Evitar prometer fecha cerrada con requerimientos abiertos.
- Si discovery es incompleto, emitir presupuesto por rango y fase.
- Mantener trazabilidad: cada numero debe mapear a un item funcional concreto.
