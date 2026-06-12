# Memoria - Analista funcional

## Proyecto: labipac
## Ultima actualizacion: 2026-06-12

## Definiciones vigentes

### Modulos/features analizados
- Acceso al sistema con usuario y contrasena.
- Catalogo de unidades bioquimicas (estudios individuales) con precio.
- Catalogo de practicas (conjuntos de estudios) con precio propio.
- Carga mensual de cantidades realizadas por estudio y por practica.
- Calculo del monto estimado a cobrar en base a cantidades y precios configurados.
- Consulta de historial mensual y resumen de calculo.

### Reglas funcionales acordadas
- El sistema es web y de uso para un unico usuario.
- El acceso requiere autenticacion con usuario y contrasena.
- Cada unidad bioquimica tiene un precio monetario.
- Cada practica tiene un precio monetario propio.
- El precio de una practica debe ser menor que la sumatoria de los estudios que la componen.
- El usuario debe poder cargar cuantas unidades realizo por mes.
- El sistema debe estimar el total a cobrar a partir de las cantidades y precios configurados.

### Criterios de aceptacion vigentes
- El usuario solo accede al sistema con credenciales validas.
- Pueden configurarse estudios individuales con nombre y precio.
- Pueden configurarse practicas con nombre, precio y composicion.
- El sistema bloquea una practica cuyo precio sea mayor o igual a la suma de sus estudios componentes.
- Al cargar cantidades mensuales, el sistema calcula el total estimado con los precios vigentes.
- El sistema permite consultar el detalle y el total estimado por mes.

### Supuestos y dependencias
- Se asume que el dominio de practicas y estudios sera administrado dentro del mismo sistema.
- Se asume que la carga sera mensual, aunque falta confirmar si el mes puede reabrirse y editarse.
- Se asume que el precio de cada item puede cambiar en el tiempo, pero falta confirmar si debe conservarse historial por mes.
- Depende de que el cliente confirme la regla exacta de composicion entre practicas y estudios para evitar doble conteo.

### Exclusiones confirmadas
- No se definieron integraciones externas.
- No se pidio facturacion electronica.
- No se pidio gestion de pacientes, resultados clinicos ni turnos.
- No se pidio aplicacion movil nativa.

## Historial de ajustes
- 2026-06-12: Se creo la memoria inicial del proyecto y se fijo el alcance base de calculo, catalogos y carga mensual.
- 2026-06-12: Se marco a .NET 10 en smarteasp como destino recomendado por coherencia con el stack y el tipo de aplicacion.

## Alcance funcional resumido

### Incluido
1. Login con usuario y contrasena.
2. Alta, edicion y baja logica de unidades bioquimicas.
3. Alta, edicion y baja logica de practicas.
4. Configuracion del precio de cada item.
5. Carga mensual de cantidades realizadas.
6. Calculo automatico del total estimado a cobrar.
7. Consulta de historial y detalle por mes.

### No incluido
1. Integracion con laboratorios, sistemas externos o APIs.
2. Emision de factura o comprobante fiscal.
3. Gestion de pacientes, historias clinicas o resultados de estudios.
4. App movil nativa.
5. Multiusuario con roles complejos, salvo que luego se confirme otro alcance.

### Dependencias
- Definir si una practica se factura como paquete cerrado o si ademas deben registrarse sus estudios componentes.
- Definir si los precios se manejan por vigencia historica mensual o como valor unico actual.
- Definir si los periodos mensuales quedan cerrados o siempre editables.

## Casos de uso principales

| # | Caso de uso | Actor | Resumen |
|---|---|---|---|
| CU-01 | Iniciar sesion | Usuario unico | Acceso al sistema con credenciales validas. |
| CU-02 | Administrar estudios individuales | Usuario unico | ABM de unidades bioquimicas con precio. |
| CU-03 | Administrar practicas | Usuario unico | ABM de practicas con composicion y precio propio. |
| CU-04 | Cargar produccion mensual | Usuario unico | Registrar cantidades realizadas por mes. |
| CU-05 | Calcular estimacion de cobro | Sistema | Sumar cantidades por precio y mostrar el total estimado. |
| CU-06 | Consultar historial mensual | Usuario unico | Ver detalle y total calculado por mes. |

## Criterios de aceptacion verificables por caso de uso

### CU-01
- Con credenciales validas, el usuario ingresa al sistema.
- Con credenciales invalidas, el sistema rechaza el acceso.

### CU-02
- Se pueden guardar estudios con nombre y precio.
- No se aceptan precios negativos.
- El estudio queda disponible para usarse en calculos mensuales.

### CU-03
- Se pueden guardar practicas con nombre, precio y estudios asociados.
- El sistema impide guardar una practica cuyo precio no sea menor que la suma de sus estudios.
- La composicion de la practica queda visible para su validacion.

### CU-04
- El usuario puede seleccionar un mes y cargar cantidades por item.
- No se permiten cantidades negativas.
- La informacion queda disponible para recalculo y consulta posterior.

### CU-05
- El total estimado se obtiene a partir de cantidades x precio por cada item cargado.
- El sistema muestra el detalle de los importes calculados.
- Si no hay cantidades cargadas, el total del mes es cero.

### CU-06
- El usuario puede recuperar el calculo de un mes ya cargado.
- El historial muestra cantidades, precios y total estimado.

## Permisos, estados y validaciones identificados

### Permisos
- Un unico usuario autenticado con capacidad de administracion total.

### Estados
- Catalogos: activo / inactivo.
- Periodo mensual: por confirmar si sera editable o cerrado.

### Validaciones
- Usuario y contrasena obligatorios para acceso.
- Precio mayor o igual a cero para estudios y practicas.
- Precio de practica estrictamente menor que la suma de sus estudios.
- Cantidades mensuales mayores o iguales a cero.
- No debe haber ambiguedad en la composicion de una practica.

## Riesgos y supuestos

### Riesgos
- R1: La regla de negocio sobre practicas puede generar doble conteo si no se define si se cargan como paquete o junto con sus estudios.
- R2: Si los precios cambian en el tiempo, el historico puede no coincidir con liquidaciones previas sin vigencia por mes.
- R3: Si el periodo mensual no queda cerrado, el usuario puede modificar calculos historicos sin trazabilidad.

### Supuestos
- S1: El sistema sera de uso local para un solo usuario.
- S2: El calculo buscado es una estimacion de cobro, no una facturacion fiscal.
- S3: El stack destino recomendado es ASP.NET Core MVC sobre .NET 10 en el servidor smarteasp.

## Banderas tempranas

| Bandera | Valor | Nota |
|---|---|---|
| Requiere migracion EF | Si | Se necesita un esquema persistente nuevo para catalogos, composicion y carga mensual. |
| Integracion externa | No | No se pidieron sistemas externos en el alcance base. |
| Maquina de estados | No por ahora | Solo seria necesaria si se confirma cierre/reapertura de periodos o cambios de estado mas complejos. |

## Preguntas para aclarar requerimientos

### 1. Como se usa una practica frente a sus estudios componentes?
- **Hipotesis A:** la practica es un paquete cerrado. Ejemplo: "Rutina" se carga como un solo item con su precio y no se suman aparte hemograma, glucemia y orina.
- **Hipotesis B:** la practica solo agrupa estudios para configuracion, pero en el mes tambien se cargan los estudios individuales por separado. Ejemplo: se registra "Libreta sanitaria" y ademas cada estudio que la compone.

### 2. Un estudio puede pertenecer a mas de una practica?
- **Hipotesis A:** no, cada estudio pertenece a una sola practica. Ejemplo: un estudio de laboratorio solo forma parte de "Rutina".
- **Hipotesis B:** si, un mismo estudio puede reutilizarse en varias practicas. Ejemplo: la glucemia puede estar tanto en "Rutina" como en "Libreta sanitaria".

### 3. Los precios cambian por mes o son valores unicos vigentes?
- **Hipotesis A:** el precio vigente se modifica y vale desde ese momento en adelante. Ejemplo: hoy una practica vale $10.000 y desde el proximo mes pasa a $12.000.
- **Hipotesis B:** cada mes guarda su propio precio historico. Ejemplo: marzo conserva $10.000 y abril conserva $12.000 aunque luego el valor actual cambie otra vez.

### 4. El mes cargado queda editable o se cierra?
- **Hipotesis A:** siempre editable. Ejemplo: si aparece una practica olvidada, el usuario corrige el mes ya cargado.
- **Hipotesis B:** el mes se cierra y solo puede reabrirse con una accion explicita. Ejemplo: febrero queda bloqueado una vez confirmado el total.
