# Olvidata**Soft**

---

**Cuenta corriente de clientes y control de usuarios — Delicias Naturales**

**OlvidataSoft · Octubre 2026**

---

## Sobre el sistema

Esta propuesta cubre dos cosas distintas: la **cuenta corriente de clientes**, que ya esta funcionando en el sistema desde fines de julio, y un **control de usuarios** que conversamos y todavia esta por hacerse.

- Cada cliente tiene ahora su **saldo a favor** registrado y visible, con el detalle de como se formo.
- Cuando un cliente **paga de mas** una venta, esa diferencia ya no se pierde ni queda anotada aparte: queda como credito suyo en el sistema.
- Ese credito despues se **usa para pagar** otra venta, y el sistema lo descuenta de verdad del saldo del cliente.
- Si un pago se borra o una venta se elimina, el sistema **deshace solo** el movimiento de cuenta corriente que habia generado.
- Vos podes **cargar un ajuste a mano** (a favor o en contra) cuando hace falta corregir algo, dejando siempre escrito el motivo.
- Y en el listado de clientes ves el saldo de un pantallazo, sin entrar a cada ficha.

## Como funciona la cuenta corriente — paso a paso

**1. El cliente paga de mas.** Cargas el pago por el monto que te dio, incluso si supera lo que debia por esa venta. El sistema cubre la venta y lo que sobra queda como **credito del cliente**.

**2. El credito queda a la vista.** Entrando a la ficha del cliente hay una pantalla de Cuenta Corriente con todos los movimientos: que dia se genero cada credito, de que venta salio, y como quedo el saldo.

**3. Ese saldo se usa para cobrar.** En la proxima venta de ese cliente, al registrar el pago podes elegir "saldo a favor". El sistema valida que el cliente realmente tenga ese saldo y lo descuenta.

**4. Si algo se borra, se deshace solo.** Borrar un pago o eliminar una venta completa deshace el movimiento de cuenta corriente que ese pago habia generado. No queda saldo inventado ni saldo perdido.

**5. Ajuste a mano cuando hace falta.** El Administrador puede cargar un credito o un debito manual sobre cualquier cliente, con una observacion obligatoria explicando por que. Queda registrado como cualquier otro movimiento.

**Casos especiales contemplados:**

- Si una venta tiene una **Nota de Credito** aprobada y ademas pagos registrados, el sistema te avisa en la pantalla de la venta para que la revises: ahi la correccion del saldo la decidis vos, porque adivinarla automaticamente seria riesgoso.
- Las **correcciones de los primeros dias** de funcionamiento (dos clientes a los que no se les habia reflejado un sobrepago) ya quedaron arregladas en la base, sin cargo.

## Como va a funcionar el control de usuarios — paso a paso

*Este flujo todavia no esta hecho: es lo que te propongo construir.*

**1. Ves quien usa el sistema y quien no.** En el listado de usuarios se agrega la columna **Ultimo acceso**, y un filtro para ver directamente los que no entran desde hace mas de X dias.

**2. Desactivas al que no lo usa.** Con un boton, desde el mismo listado. El usuario no se borra: queda desactivado, con todo su historico intacto.

**3. El usuario desactivado no puede entrar.** Si intenta ingresar, el sistema no lo deja y el intento queda registrado en la auditoria de accesos que ya tenes.

**4. Se puede volver atras en cualquier momento.** Reactivar es el mismo boton. Si la persona vuelve, sigue con su usuario de siempre.

**Protecciones incluidas:** no podes desactivarte a vos mismo por error, y el sistema no te deja quedarte sin ningun Administrador activo.

*A confirmar antes de arrancar: si la desactivacion la decidis vos a mano (es lo que estoy cotizando) o preferis que el sistema la haga solo despues de X dias sin entrar, y si hace falta avisarle por mail al usuario cuando se lo desactiva.*

## Rol de usuario

| Rol | Accesos |
|---|---|
| Administrador | Ve y usa la cuenta corriente de todos los clientes, carga los ajustes manuales, y administra los usuarios (crear, editar, activar y desactivar). |
| Vendedor | Ve el saldo a favor del cliente y lo usa al registrar un pago. No carga ajustes manuales ni administra usuarios. |

*Las altas de usuario y la configuracion de roles las gestiono yo si lo preferis; de lo contrario queda del lado del Administrador.*

## Inversion

### Ya entregado y funcionando

| Area | USD |
|---|---:|
| Cuenta corriente del cliente: saldo, movimientos y ajuste manual | 67 |
| Pagos con cuenta corriente: sobrepago que genera credito, cobro con saldo a favor y reversion automatica | 67 |
| Saldo a la vista en el listado y la ficha del cliente, y en el momento de cobrar | 16 |
| Correcciones de los primeros dias de uso (concurrencia de pagos, reversiones, avisos) | Sin cargo |
| **Subtotal** | **150** |

### Para desarrollar

| Area | USD |
|---|---:|
| Activar y desactivar usuarios, con bloqueo real del acceso | 34 |
| Ultimo acceso de cada usuario y filtro de inactivos | 16 |
| **Subtotal** | **50** |

| Total | USD |
|---|---:|
| **Total** | **200** |

*Opcional, si lo queres: desactivacion automatica por inactividad (el sistema desactiva solo al que no entra en X dias), **USD 17**. No lo incluyo por defecto porque desactivar una cuenta por error deja a alguien sin poder trabajar, y la decision manual es mas segura.*

## Que incluye

- Todo lo listado arriba, funcionando en tu servidor de produccion.
- Las pruebas y los ajustes posteriores a la entrega de lo que se desarrolle.
- La correccion sin cargo de cualquier error propio de lo que entrego.

## Que no esta incluido

- Funcionalidades nuevas que no esten en las tablas de arriba.
- Aviso por mail al usuario cuando se lo desactiva.
- Migracion o recalculo de saldos historicos anteriores a agosto de 2026.
- Cambios en la cuenta corriente de proveedores (esta propuesta es solo de clientes).
- Capacitacion presencial.

## Lo que necesitamos de tu parte

- Confirmarme los tres puntos del control de usuarios: si la desactivacion es a mano o automatica, si hace falta avisar por mail, y desde cuantos dias sin entrar consideras que un usuario "no usa el sistema".
- Una persona de referencia para probar la pantalla de usuarios cuando este lista.

## Condiciones comerciales

- **Lo ya entregado (USD 150):** se abona contra presentacion, sin anticipo — ya esta funcionando.
- **Lo por desarrollar (USD 50):** 50% para arrancar y 50% contra entrega.
- Precios en dolares.
- Si el alcance del control de usuarios crece sobre lo descripto, lo volvemos a conversar antes de arrancar.

---

**Olvidata Soft — bourdinjoaquin@gmail.com — olvidatasoft.com**
