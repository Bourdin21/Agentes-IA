# Olvidata**Soft**
---

**Labipac — Resumen de sprint: Precio por Unidad, carga masiva y fix de PDF**
**OlvidataSoft · Julio 2026**

## Sobre el proyecto

Este sprint sumó tres mejoras a Labipac, tu calculadora de producción mensual: un nuevo modelo de precios más simple para tus Perfiles, una forma más rápida de cargar la producción de cada mes, y una corrección en el reporte PDF. Las tres mejoras ya están implementadas, validadas y listas para que las pruebes.

## Cambios entregados

- **Precio por Unidad:** ahora configurás un único valor de referencia (Precio por Unidad, hoy $ 892,03) y el precio de cada Perfil se calcula solo, según cuántas Unidades tiene. Ya no hace falta tipear el precio de cada Perfil a mano.
- **Aumento con un click:** cuando el Precio por Unidad sube, lo actualizás una sola vez y el precio de todos tus Perfiles activos se recalcula automáticamente.
- **Carga masiva de producción mensual:** nueva pantalla para cargar varias líneas de un mes de una sola vez, en lugar de una por una.
- **Alta rápida desde la carga:** si necesitás un Perfil o una Práctica que todavía no existe, lo creás ahí mismo sin salir de la pantalla.
- **Reporte PDF corregido:** la columna de precio unitario ya no corta los números en montos grandes.

## Qué gana tu equipo con esto

- Menos carga manual y menos margen de error al fijar precios: un solo valor controla el precio de todos los Perfiles.
- Actualizar precios ante un aumento general te toma un click en vez de editar Perfil por Perfil.
- Cargar la producción de un mes es más rápido cuando tenés varias líneas para registrar.
- El PDF que compartís o archivás ahora se lee bien, sin números cortados.

## Pendientes de tu parte

- **Revisar los valores de Unidad** que el sistema calculó automáticamente para tus Perfiles ya existentes (se estimaron a partir del precio que tenían antes, para que ninguno quede en $0). Te pedimos que los repases y ajustes los que no coincidan con el valor real.
- Confirmarnos que el valor vigente de Precio por Unidad ($ 892,03) es el correcto para arrancar a operar con el nuevo modelo.

## Consideraciones

- La pantalla de "Aumento masivo de precios" que ya usabas para tus Prácticas sigue funcionando igual que antes; dejó de aplicar a Perfiles porque ahora su precio se calcula automáticamente por Unidad.
- Ya no es obligatorio asociar componentes a un Perfil para poder guardarlo — la composición quedó como un dato informativo, no como un requisito.

## Próximo paso sugerido

Te pedimos que hagas una prueba rápida de los tres flujos (configurar/aumentar el Precio por Unidad, cargar producción mensual de varias líneas juntas, y descargar un PDF) y nos confirmes que todo se ve como esperás antes de darlo por cerrado.

**Olvidata Soft — contacto@olvidatasoft.com — olvidatasoft.com**
