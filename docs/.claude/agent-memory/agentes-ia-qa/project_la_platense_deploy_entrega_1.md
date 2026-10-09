---
name: project-la-platense-deploy-entrega-1
description: LP-050 cerrado 2026-10-07; el deploy de La Platense exige base y sitio en la MISMA ventana, y el FTP esta trabado por credencial rotada
metadata:
  type: project
---

Al 2026-10-07, el deploy de La Platense (rama `entrega-1-migracion`, HEAD `fcfa077`) tiene **`LP-050`
cerrado** y GO, pero con una condicion de **secuencia**: la base (10 migraciones) y el sitio van en la
**misma ventana**. Verificar el estado actual antes de actuar sobre esto — es lo que cambia mas rapido.

**Why:** el esquema nuevo **aguanta al codigo viejo sin romperse** (se midio: de 31 columnas nuevas sobre
tablas preexistentes, ninguna es `NOT NULL` sin default, con `sql_mode=STRICT_TRANS_TABLES` en prod; el unico
UNIQUE nuevo, `IX_Proveedores_CUIT`, convive con 85 `CUIT` NULL; la unica FK nueva es nullable). Pero los
backfills del `Up` **corren una sola vez y ningun `Down` los revierte**, asi que toda escritura del codigo
viejo *posterior* a la migracion deja datos que nadie va a volver a arreglar: `CajaMovimientos.MedioPago`
NULL permanente (= `LP-050` reabierto, invisible), `EsReversion=0` donde corresponde `1`, y
`Proveedores.Moneda=0`, que no es valor valido del enum. Produccion **esta activa** (su unico movimiento de
caja es del 2026-10-06), asi que la ventana no es teorica.

**How to apply:** si alguien propone migrar la base primero para destrabar el deploy del sitio, **decir que
no**, o exigir que la ferreteria no opere entre las dos mitades. Cambia un problema de deploy (visible y
reversible) por uno de integridad de datos silencioso. El rollback es **restaurar el snapshot**, no
desmigrar: `C:/Sistemas/backups/laplatense/laplatense_PROD_2026-10-07_pre-migracion-18.sql`, probado
restaurable en 17 s.

Bloqueante vivo y ajeno a QA: **la password de FTP/Web Deploy no autentica** (`530`, usuario activo → fue
rotada). La resuelve Joaquin. Agrava lo de arriba porque es justo lo que tienta a separar las dos mitades.

Pendiente menor: `LP-051` `trivial`, abierto. Entrega 5 (AFIP real, NC/ND) no esta construida.
Metodo con el que se cerro esto: [[feedback-medicion-default-fail]].
