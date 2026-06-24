# Memoria QA

Proyecto: labipac
Ultima actualizacion: 2026-06-15

---

## Nomenclatura de dominio vigente

UnidadBioquimica -> label Practica en UI
Practica (entidad) -> label Perfil en UI
TipoItemProduccion.Practica -> badge Perfil
TipoItemProduccion.UnidadBioquimica -> badge Practica

---

## Maquina de estados

No aplica. P4-A confirmado: periodo siempre editable, sin cierre.
Estados de entidades: Activa / Inactiva via soft delete (DeletedAt).

---

## Reglas de negocio cubiertas

RN-01: PrecioActual(Perfil) < SumatoriaComponentes
RN-02: Perfil requiere al menos 1 Practica componente
RN-03: Snapshot precio inmutable retroactivamente
RN-04: No duplicar mismo item en mismo periodo
RN-05: Precio AJAX pre-completado al seleccionar item
RN-06: Aviso visual periodo historico
RN-07: Cantidad entero >= 1
RN-08: PrecioSnapshot >= 0
RN-09: Solo items activos en nuevas lineas
RN-10: Total recalculado en tiempo real
RN-11: No duplicar periodo mismo mes+anio

---

## Casos de prueba

TC-UB-01 a TC-UB-07 PASS - modulo Practicas
TC-P-01 a TC-P-07 PASS - modulo Perfiles
TC-PM-01 a TC-PM-15 PASS - modulo Produccion Mensual
TC-PM-08: BUG-001 CORREGIDO - Eliminar linea ahora funciona.

---

## Bugs resueltos

BUG-001 [2026-06-15] CRITICAL
Modulo: Produccion Mensual / Eliminar linea
Causa: site.js usaba closest-form ignorando data-form del boton externo al form.
Fix: getElementById con data-form attribute en site.js
Verificacion: codigo inspeccionado + build OK + suite 50/50 PASS

---

## Evidencia sesion 2026-06-15

Suite 50 checks: 29 positivos + 21 negativos = 50/50 PASS
Build: OK
Renombre: Unidades Bioquimicas -> Practicas; Practicas -> Perfiles
Tildes: Layout, Home, ProduccionMensual, Practicas

---

## Historial

2026-06-15: Primera carga QA. Fix BUG-001. Renombre UI. Tildes. 50/50 PASS. Build OK.
