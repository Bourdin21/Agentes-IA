# Olvidata**Soft**
---

**Labipac — Mejoras funcionales sobre Producción Mensual y Perfiles**
**OlvidataSoft · Julio 2026**

## Sobre el sistema

Labipac es tu calculadora de producción mensual: te permite cargar cuántas Prácticas y Perfiles se realizaron cada mes y te calcula automáticamente el monto estimado a cobrar. Esta propuesta suma tres mejoras sobre lo que ya está funcionando:

- Vas a poder configurar un **Precio por Unidad** único, y que el precio de cada Perfil se calcule solo a partir de cuántas Unidades tiene — sin tener que fijar el precio de cada Perfil a mano.
- Cuando el Precio por Unidad sube, vas a poder aplicar el aumento con un solo click y que se actualice automáticamente el precio de todos tus Perfiles activos.
- Vas a poder cargar varias líneas de producción mensual de una sola vez, en lugar de una por una, y crear un Perfil o una Práctica nuevos sin salir de esa pantalla.
- El reporte en PDF de tu producción mensual va a mostrar el precio unitario completo, sin que se corten los números.

## Cómo funciona el nuevo Precio por Unidad — paso a paso

**1. Configurás el Precio por Unidad.** Desde el listado de Perfiles vas a ver un panel con el valor vigente (hoy $ 892,03). Lo podés editar a mano cuando quieras.

**2. Cargás la cantidad de Unidades de cada Perfil.** Al crear o editar un Perfil, en lugar de tipear un precio, indicás cuántas Unidades tiene. El sistema te muestra al instante el precio resultante (Unidades × Precio por Unidad).

**3. Aplicás un aumento con un click.** Ingresás un porcentaje y confirmás — el Precio por Unidad sube ese porcentaje y **todos** tus Perfiles activos recalculan su precio automáticamente, sin que tengas que tocarlos uno por uno.

*Los Perfiles que ya tenés cargados van a recibir una cantidad de Unidades aproximada automáticamente al activar esta mejora (a partir de su precio actual), para que no queden en $ 0. Te recomendamos revisarlos y ajustarlos una vez activo el cambio.*

## Cómo funciona la carga masiva — paso a paso

**1. Abrís la nueva pantalla "Carga masiva"** desde el detalle de tu Producción Mensual.

**2. Agregás tantas filas como necesites,** cada una con tipo (Perfil o Práctica), ítem, cantidad y precio.

**3. Si necesitás un Perfil o una Práctica que todavía no existe,** lo creás ahí mismo sin salir de la pantalla, y queda seleccionado automáticamente en la fila.

**4. Guardás todo junto** con un solo click. Si hay algún error en una fila, no se guarda nada hasta que lo corrijas — así no quedan cargas a medias.

## Rol de usuario

| Rol | Accesos |
|---|---|
| Administrador | Acceso completo: configurar el Precio por Unidad y aplicar aumentos, cargar producción mensual (individual y masiva), crear Perfiles y Prácticas, generar reportes. |
| Usuario | Cargar producción mensual (individual y masiva), crear Perfiles y Prácticas, generar reportes. No puede modificar el Precio por Unidad. |

*El proveedor gestiona internamente el usuario de administración técnica del sistema; no forma parte de los roles operativos del cliente.*

## Inversión

### Etapa 1 (base del nuevo modelo de precios)

| Área funcional | USD |
|---|---:|
| Unidad y Precio por Unidad en Perfiles (configuración, cálculo automático, aumento por %) | 75.60 |
| Ajuste de ancho de columna en el reporte PDF | 8.40 |
| **Subtotal Etapa 1** | **84.00** |

### Etapa 2 (carga masiva y alta rápida)

| Área funcional | USD |
|---|---:|
| Carga masiva de Producción Mensual + creación rápida de Perfiles/Prácticas | 109.20 |
| **Subtotal Etapa 2** | **109.20** |

### Total del proyecto

| Concepto | USD |
|---|---:|
| Subtotal Etapa 1 + Etapa 2 | 193.20 |
| Tokens IA (10% del total) | 19.32 |
| **Total del proyecto** | **212.52** |

*Etapa 1 resuelve primero la base del modelo de precios (necesaria para que el resto funcione de forma consistente) y corrige el defecto del PDF. Etapa 2 suma la mejora de carga masiva, que se apoya en la Etapa 1 ya funcionando.*

## Mantenimiento anual

Tu plan de mantenimiento actual (**Plan PRO — USD 300/año**) no cambia con esta ampliación: la nueva tabla de configuración se mantiene dentro del mismo rango de cantidad de tablas cubierto por tu plan vigente.

## Qué incluye

- Configuración de Precio por Unidad, editable a mano y con aumento por porcentaje.
- Cálculo automático del precio de cada Perfil según su cantidad de Unidades.
- Actualización automática de todos los Perfiles activos al cambiar el Precio por Unidad.
- Pantalla nueva de carga masiva de Producción Mensual con filas múltiples y guardado atómico.
- Creación de Perfiles y Prácticas nuevas desde la carga masiva, sin salir de la pantalla.
- Corrección del ancho de columna en el reporte PDF de Producción Mensual.

## Qué no está incluido

- Migración de datos desde otro sistema.
- Configuración y costo del servidor / hosting (cubierto por tu plan de mantenimiento).
- Facturación electrónica AFIP/ARCA.
- Aplicación móvil.
- Integración con hardware externo.
- Cambios de alcance posteriores al inicio de esta propuesta (se cotizan por separado).

## Lo que necesitamos de tu parte

- Confirmar el valor vigente de Precio por Unidad ($ 892,03) o el que corresponda al momento de activar la mejora.
- Revisar y ajustar manualmente la cantidad de Unidades de tus Perfiles existentes una vez desplegado el cambio (el sistema te da un valor aproximado inicial para que no queden en $ 0, pero solo vos podés confirmar el valor exacto de cada uno).
- Confirmar esta propuesta para arrancar con la Etapa 1.

## Condiciones comerciales

- Forma de pago: 50% al inicio de cada etapa, 50% a la entrega de esa etapa.
- Moneda: dólares estadounidenses (USD).
- Si durante el desarrollo surge un cambio de alcance no contemplado acá, se cotiza aparte antes de incorporarlo.

**Olvidata Soft — contacto@olvidatasoft.com — olvidatasoft.com**
