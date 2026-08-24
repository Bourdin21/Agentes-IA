# Olvidata**Soft**
---

**Labipac — Propuesta: Precio por Unidad Bioquímica y por Perfil según Centro de Salud**
**OlvidataSoft · Agosto 2026**

## Sobre el cambio propuesto

Hoy el sistema calcula la producción mensual con un precio único por cada Práctica y por cada Perfil, sin importar dónde se realizó el estudio. Nos comentaste que en la realidad eso no es así: la Unidad Bioquímica se cobra distinto según el Centro de Salud donde se hace — un valor para un centro privado, otro para una mutual, y así con cada uno.

Esta propuesta describe cómo adaptaríamos el sistema para que el precio de cada Práctica y cada Perfil varíe según el Centro de Salud, y qué implica eso para tu forma de trabajar. Todavía no se implementó nada — es la base para que confirmes el alcance antes de pasar a presupuesto.

## Cómo va a funcionar — paso a paso

**1. Cada Práctica pasa a tener una "cantidad de unidades bioquímicas" propia.** Es un dato nuevo que vas a cargar en cada Práctica (por ejemplo, "esta Práctica vale 3 unidades bioquímicas"). Reemplaza al precio en pesos que cargás hoy directamente.

**2. El precio de un Perfil se calcula sumando las unidades bioquímicas de las Prácticas que lo componen.** Si un Perfil está formado por 3 Prácticas y cada una tiene su cantidad de unidades bioquímicas cargada, el sistema suma todo automáticamente para saber cuántas unidades bioquímicas representa ese Perfil en total. **Esto es un cambio importante respecto a como funciona hoy:** actualmente, qué Prácticas componen un Perfil es solo información de referencia y no afecta el precio (vos cargás la cantidad de unidades a mano). Con este cambio, la composición vuelve a ser necesaria: todo Perfil va a tener que tener al menos una Práctica asociada, y cada una de esas Prácticas va a necesitar su cantidad de unidades bioquímicas cargada — si falta alguna, el Perfil no va a poder calcular su precio.

**3. Cada Centro de Salud tiene un único "Precio de Unidad Bioquímica".** No es un precio distinto por cada Práctica en cada centro — es un solo valor por centro (por ejemplo, "en la Clínica X la unidad bioquímica vale $850, en la Mutual Y vale $700"), y ese valor multiplica la cantidad de unidades de cualquier Práctica o Perfil que factures en ese centro. Es una pantalla chica y simple: un valor editable por cada Centro de Salud, con la opción de aumentarlo por porcentaje — igual que ya funciona hoy el precio general único, pero repetido una vez por centro.

**4. Elegir Centro de Salud pasa a ser obligatorio al crear un período nuevo.** Hoy es opcional. De acá en adelante, todo período nuevo de Producción Mensual va a pedirte que elijas a qué Centro de Salud corresponde, porque sin eso el sistema no sabe qué precio de unidad bioquímica aplicar.

**5. Cada línea que cargás usa el precio de ese centro.** El precio de una Práctica = su cantidad de unidades bioquímicas × el precio de unidad bioquímica de ese centro. El precio de un Perfil = la suma de unidades bioquímicas de sus Prácticas componentes × el precio de unidad bioquímica de ese centro.

**6. Si falta algún dato para calcular el precio, el sistema te avisa y no te deja cargarlo mal.** Puede faltar el precio de unidad bioquímica de ese centro, o la cantidad de unidades bioquímicas de alguna Práctica, o que un Perfil no tenga su composición completa. En cualquiera de esos casos, el sistema te lo va a decir con un mensaje claro en vez de calcular un precio incorrecto.

**7. Tus períodos ya cargados no cambian.** Los períodos que cargaste hasta ahora sin Centro de Salud siguen funcionando exactamente igual que hoy — no necesitás tocar nada de tu historial.

**8. El catálogo general de Prácticas y Perfiles sigue mostrando un precio de referencia.** Cuando mirás el listado general (fuera de un período puntual), vas a seguir viendo un precio único de referencia, tal como hoy.

## Qué incluye esta propuesta

- Cada Práctica pasa a tener una cantidad de unidades bioquímicas propia (reemplaza el precio en pesos que se carga hoy a mano).
- El precio de cada Perfil se calcula automáticamente a partir de las Prácticas que lo componen — la composición vuelve a ser obligatoria.
- Pantalla nueva y simple para cargar el "Precio de Unidad Bioquímica" de cada Centro de Salud (un valor por centro, con opción de aumento por porcentaje).
- Centro de Salud obligatorio al crear un período nuevo de Producción Mensual.
- Cálculo automático del precio correcto según el centro elegido, al cargar cada línea.
- Aviso claro cuando falta algún dato para calcular un precio, sin dejar pasar un cobro incorrecto.
- Compatibilidad total con tu historial: nada de lo ya cargado cambia ni se recalcula.

## Qué no incluye este alcance

- No hay forma de completar automáticamente la cantidad de unidades bioquímicas de tus Prácticas actuales — es un dato nuevo que no existe hoy en el sistema, así que la carga inicial la hacés vos (o la coordinamos juntos).
- No se modifican ni se les asigna centro a los períodos que ya tenés cargados.
- No se vincula el catálogo de Centro de Salud con el catálogo de Mutuales de FABA (eso ya estaba definido así desde el cambio anterior).

## Lo que necesitamos de tu parte

- **Cargar la cantidad de unidades bioquímicas de cada Práctica activa.** Es un valor por Práctica (no por cada combinación con un centro), pero es un dato nuevo que hay que completar antes de que el cálculo funcione.
- **Revisar que tus Perfiles tengan su composición completa.** Como la composición vuelve a determinar el precio, te pedimos que antes de este cambio revisemos juntos qué Perfiles no tienen Prácticas asociadas (o las tienen, pero sin su cantidad de unidades cargada) — para que ninguno quede sin precio calculable el día del lanzamiento.
- **Cargar el "Precio de Unidad Bioquímica" de cada Centro de Salud que uses habitualmente.** Es un solo valor por centro, rápido de cargar una vez que estén dados de alta tus Centros de Salud.
- Confirmarnos si estás de acuerdo con que Centro de Salud pase a ser obligatorio en los períodos nuevos (hoy es opcional).

## Próximo paso sugerido

Si estás de acuerdo con este alcance, el paso siguiente es que te preparemos el presupuesto formal (con horas y costo) para poder arrancar la implementación. Antes de eso, te proponemos revisar juntos el estado actual de tus Perfiles (composición completa o no) para dimensionar bien la carga de datos previa al lanzamiento.

**Olvidata Soft — contacto@olvidatasoft.com — olvidatasoft.com**
