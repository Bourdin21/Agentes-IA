# Catalogo de Regresiones Manuales (consumible por agente QA)

Este directorio guarda **parametros comunes** de pruebas funcionales reproducidas manualmente y de las soluciones aplicadas. El objetivo es que el agente QA pueda:

1. Cargar `regresiones-manuales.yml` como entrada estructurada.
2. Reproducir cada caso (UI / API / data) usando los `pasos` y `deteccion_qa.selector_o_endpoint`.
3. Marcar **falla** si se cumple `deteccion_qa.condicion_falla`.
4. Ofrecer correccion automatica leyendo `archivos_fix` (pistas de patch) y `migracion_ef` cuando aplica.
5. Validar el cierre con `criterio_aceptacion` y correr `pruebas_minimas`.

## Reglas de mantenimiento

- Todo bug funcional **reproducido manualmente** y corregido en el repo debe agregarse aqui antes del merge.
- El `id` es estable (no renombrar). Si se invalida, marcar `severidad: deprecated` y dejar el item.
- `archivos_fix` debe listar **rutas reales** existentes en la solucion al momento del fix.
- `migracion_ef` se completa solo si el fix incluyo migracion EF. Caso contrario `null`.
- Cada item debe poder ejecutarse **independiente** por el agente QA (sin orden implicito).
- Mantener el archivo en YAML 1.2, sin tabs, ASCII puro (sin tildes en claves).

## Convenciones

- `capa`: `Domain`, `Application`, `Infrastructure`, `Web`, o combinaciones con `+`.
- `severidad`: `blocker`, `critical`, `major`, `minor`.
- `deteccion_qa.tipo`:
  - `ui`: requiere navegacion / Playwright / Selenium.
  - `api`: HTTP request directo (curl/HttpClient).
  - `data`: query SQL/EF a la base.
  - `static`: chequeo estatico de codigo o config.
- `pruebas_minimas`: nombres de escenarios funcionales que el agente QA debe correr y reportar OK/Fail.

## Como debe consumirlo el agente QA

```yaml
# pseudocode del agente QA
for caso in regresiones:
    if caso.severidad == "deprecated":
        continue
    resultado = ejecutar(caso.deteccion_qa)
    if resultado.cumple(caso.deteccion_qa.condicion_falla):
        reportar_falla(caso.id, caso.titulo)
        if modo == "auto-fix":
            sugerir_patch(caso.archivos_fix, caso.migracion_ef)
    else:
        validar_pruebas_minimas(caso.pruebas_minimas)
```

## Indice rapido (snapshot al 2026-04-29)

| id      | modulo                  | severidad | resumen                                              |
|---------|-------------------------|-----------|------------------------------------------------------|
| REG-001 | Variantes/Stock         | blocker   | RowVersion MySQL                                     |
| REG-002 | Variantes/Stock         | major     | Stock inicial al crear/editar variante               |
| REG-003 | Compras/Crear           | major     | Autocomplete proveedor/variantes                     |
| REG-004 | Compras/Detalle         | major     | Maquina de estados de Compra                         |
| REG-005 | Ventas/Crear            | major     | Autocomplete variantes vacio                         |
| REG-006 | Ventas/Crear            | major     | Cuotas (cantidad >=2 y % financiamiento)             |
| REG-007 | Devoluciones/Crear      | major     | Autocomplete Nueva variante                          |
| REG-008 | Ventas/Crear (pagos)    | major     | Importe pierde foco al tipear                        |
| REG-009 | AumentoMasivo           | major     | Cascada Categoria -> Subgrupo                        |
| REG-010 | Sidebar/Auditoria       | minor     | Menu Auditoria visible solo SuperUsuario             |
