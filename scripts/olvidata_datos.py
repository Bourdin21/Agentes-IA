# -*- coding: utf-8 -*-
"""Genera los archivos de datos reales de Olvidata desde el CRM productivo.

Hasta ahora la memoria de negocio guardaba reglas y supuestos: el plan financiero partia de un
ticket estimado de USD 426 por cliente y la lista de clientes era una linea de prosa sin plan ni
recurrente. Los datos que contestan "que esta pasando de verdad" ya existen, pero en la base del
CRM (`clientes`, `upsells`, `contactos`), donde ningun agente los puede leer. Este script los
baja a tres archivos que si entran en el contexto de un agente:

    docs/olvidata/clientes.md   una fila por cliente, con plan, recurrente y renovacion
    docs/olvidata/pipeline.md   el embudo por etapa y los leads abiertos que valen seguimiento
    docs/olvidata/metricas.md   una fila por mes, y el semaforo del umbral del Ministerio

Son SNAPSHOTS regenerables: no se editan a mano (el encabezado de cada uno lo aclara). Lo que el
CRM no sabe —el frente comercial de cada cliente, el umbral del Ministerio— vive en
`docs/olvidata/datos-manuales.yml`, que el script lee y nunca sobreescribe.

Uso:
    python scripts/olvidata_datos.py todo
    python scripts/olvidata_datos.py clientes --dry-run

La connection string sale de `appsettings.Production.json` del repo del CRM, que esta fuera de
este repo y gitignoreado alla: ningun secreto entra en Agentes-IA ni se imprime en pantalla.
"""
import argparse
import datetime
import io
import os
import re
import sys
from collections import OrderedDict, defaultdict
from decimal import Decimal

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "docs", "olvidata")
MANUALES = os.path.join(SALIDA, "datos-manuales.yml")
CRM_SETTINGS = r"C:\Sistemas\olvidatasoft-crm\OlvidataCRM.Web\appsettings.Production.json"

PLANES = {1: "Starter", 2: "Pro", 3: "Premium", 4: "Scale"}
ETAPAS = OrderedDict([
    (1, "Pendiente"), (2, "Mensaje enviado"), (3, "Follow-up enviado"), (4, "Respondio"),
    (5, "Presupuesto enviado"), (9, "Cerrado"), (10, "Frio"), (11, "Descartado"),
    (12, "Derivado manual"),
])
CANALES = {1: "Ads pagos", 2: "Outbound frio", 3: "Referido", 4: "Manual", 5: "Instagram organico"}
GANCHOS = {1: "Presencia web", 2: "Administracion", 3: "Consultas", 4: "Gestion"}
# El gancho es lo mas cerca que el CRM esta hoy de decir por que frente entro un lead.
GANCHO_A_FRENTE = {1: "Landing", 2: "Build", 3: "Chatbots", 4: "Build"}
# Etapas que siguen vivas: son las que tiene sentido mirar como pipeline abierto.
ABIERTAS = (4, 5, 12)

AVISO = (
    "> **Archivo generado — no editarlo a mano.** Lo regenera "
    "`python scripts/olvidata_datos.py %s` leyendo el CRM productivo.\n"
    "> Snapshot del %s. Lo que el CRM no sabe se edita en `datos-manuales.yml`.\n"
)


def manuales():
    import yaml
    with io.open(MANUALES, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def conectar():
    import pymysql
    if not os.path.isfile(CRM_SETTINGS):
        sys.exit("No encuentro %s — sin la connection string del CRM no hay datos reales." % CRM_SETTINGS)
    cfg = io.open(CRM_SETTINGS, encoding="utf-8-sig").read()

    def dato(clave, default=None):
        m = re.search(clave + r"=([^;\"]+)", cfg)
        if m:
            return m.group(1)
        if default is not None:
            return default
        sys.exit("La connection string del CRM no tiene %s." % clave)

    return pymysql.connect(
        host=dato("Server"), port=int(dato("Port", "3306")), user=dato("Uid"),
        password=dato("Pwd"), database=dato("Database"), charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def escribir(nombre, cuerpo, dry_run):
    destino = os.path.join(SALIDA, nombre)
    if dry_run:
        print("--- %s (dry-run, %d lineas)" % (nombre, cuerpo.count("\n")))
        print(cuerpo[:1500])
        return
    with io.open(destino, "w", encoding="utf-8", newline="") as fh:
        fh.write(cuerpo)
    print("%-14s %d lineas" % (nombre, cuerpo.count("\n")))


def hoy():
    return datetime.date.today().isoformat()


def plata(valor):
    return "%,.0f".replace(",", "") % valor if valor is None else "{:,.0f}".format(valor).replace(",", ".")


# ---------------------------------------------------------------------------- clientes
def traer_clientes(cx):
    with cx.cursor() as cur:
        cur.execute("""
            SELECT c.Id, co.NombreNegocio nombre, c.NombreSistema sistema, c.Plan plan,
                   c.TicketAnualUsd ticket, c.Activo activo, c.PrimerAnioGratis anio1gratis,
                   DATE(c.FechaAlta) alta, DATE(c.FechaProximaRenovacion) renovacion, c.Notas notas
              FROM clientes c
              LEFT JOIN contactos co ON co.Id = c.ContactoId
             WHERE c.DeletedAt IS NULL
             ORDER BY c.Activo DESC, co.NombreNegocio, c.NombreSistema""")
        filas = cur.fetchall()
        cur.execute("""SELECT ClienteId cliente, Tipo tipo, MontoUsd monto, DATE(Fecha) fecha
                         FROM upsells WHERE DeletedAt IS NULL ORDER BY Fecha""")
        ups = cur.fetchall()
    por_cliente = defaultdict(list)
    for u in ups:
        por_cliente[u["cliente"]].append(u)
    return filas, por_cliente


def frente_de(fila, mapa):
    for clave in ("%s|%s" % (fila["nombre"], fila["sistema"] or ""), fila["nombre"] or ""):
        if clave in mapa:
            return mapa[clave], True
    return "— *sin asignar*", False


def gen_clientes(cx, man, dry_run):
    filas, upsells = traer_clientes(cx)
    mapa = man["frente_por_cliente"]
    ticket_plan = Decimal(str(man["ticket_planificacion_usd_anual"]))

    lineas = ["# Clientes y su plan\n", AVISO % ("clientes", hoy()), "\n"]
    lineas.append("| Cliente | Sistema | Frente | Plan | Recurrente anual USD | Año 1 gratis | Alta | Próxima renovación |\n")
    lineas.append("|---|---|---|---|---:|---|---|---|\n")

    activos, bajas, sin_frente = [], [], []
    for f in filas:
        frente, ok = frente_de(f, mapa)
        if not ok:
            sin_frente.append(f["nombre"])
        fila_md = "| %s | %s | %s | %s | %s | %s | %s | %s |\n" % (
            f["nombre"] or "—", f["sistema"] or "—", frente, PLANES.get(f["plan"], "?"),
            plata(f["ticket"]), "sí" if f["anio1gratis"] else "no",
            f["alta"] or "—", f["renovacion"] or "—")
        (activos if f["activo"] else bajas).append((f, fila_md))

    for _, md in activos:
        lineas.append(md)
    lineas.append("\n")
    if bajas:
        lineas.append("### Bajas\n\n")
        lineas.append("El CRM marca el cliente como inactivo pero **no guarda la fecha de la baja**, así "
                      "que la última columna sigue siendo la renovación que tenía agendada, no el día en "
                      "que se fue. Por eso la serie mensual de `metricas.md` lo cuenta como vivo hasta "
                      "hoy y su total no coincide con el de este archivo.\n\n")
        lineas.append("| Cliente | Sistema | Frente | Plan | Recurrente anual USD | Año 1 gratis | Alta | Renovación que tenía agendada |\n")
        lineas.append("|---|---|---|---|---:|---|---|---|\n")
        for _, md in bajas:
            lineas.append(md)
        lineas.append("\n")

    contratado = sum((f["ticket"] or 0) for f, _ in activos)
    cobrable = sum((f["ticket"] or 0) for f, _ in activos if not f["anio1gratis"])
    con_recurrente = [f for f, _ in activos if (f["ticket"] or 0) > 0]
    ticket_real = (contratado / len(con_recurrente)) if con_recurrente else Decimal(0)
    total_upsells = sum(u["monto"] for lista in upsells.values() for u in lista)

    # Los regalados no son un dato faltante (DEC-005): se entregaron sin plan. Van aparte para no
    # ensuciar el ticket promedio ni el conteo de clientes que pagan.
    marcados = set(man.get("regalados") or [])
    def es_regalado(f):
        return ("%s|%s" % (f["nombre"], f["sistema"] or "")) in marcados or (f["nombre"] in marcados)
    regalados = [f for f, _ in activos if es_regalado(f)]
    pagan = [f for f, _ in activos if not es_regalado(f)]

    # A lista vigente: lo que el mismo parque pagaria hoy con los precios de `precios.md`. La
    # diferencia contra lo contratado es el costo de la politica de no recalibrar retroactivo
    # (DEC-004) — no es plata perdida, es lo que decidimos no cobrarle a la base vieja.
    lista = man.get("precios_lista_vigentes") or {}
    a_lista = sum(Decimal(str(lista.get(PLANES.get(f["plan"]), 0))) for f in pagan)
    ticket_lista = (a_lista / len(pagan)) if pagan else Decimal(0)

    lineas.append("## Lo que suma\n\n")
    lineas.append("| Concepto | Valor |\n|---|---:|\n")
    lineas.append("| Clientes activos | %d (%d con plan pago + %d regalados) |\n" % (
        len(activos), len(pagan), len(regalados)))
    lineas.append("| Recurrente anual **contratado** | USD %s |\n" % plata(contratado))
    lineas.append("| Recurrente anual **cobrable hoy** (sin los de año 1 gratis) | USD %s |\n" % plata(cobrable))
    lineas.append("| Recurrente mensual cobrable | USD %s |\n" % plata(cobrable / 12))
    lineas.append("| Ticket anual real promedio (solo los que pagan recurrente) | USD %s |\n" % plata(ticket_real))
    lineas.append("| El mismo parque **a lista vigente** | USD %s/año · ticket USD %s |\n" % (
        plata(a_lista), plata(ticket_lista)))
    lineas.append("| Ticket anual de planificación que usa el plan financiero | USD %s |\n" % plata(ticket_plan))
    lineas.append("| Ingresos **no recurrentes** registrados (setup, cuotas de implementación, trabajo adicional) | USD %s en %d operaciones |\n" % (
        plata(total_upsells), sum(len(v) for v in upsells.values())))
    lineas.append("\n")

    desvio = (ticket_real - ticket_plan) / ticket_plan * 100 if ticket_plan else 0
    lineas.append("**Por qué el ticket real está abajo del de planificación** (DEC-004, resuelta): el "
                  "promedio real es USD %s contra los USD %s del plan (%+.0f%%), y la razón es la "
                  "política, no un error de carga — **las subas no se aplican retroactivamente a "
                  "clientes ya firmados**, así que la base vieja quedó con el precio anterior "
                  "(precedente 2026-07-24, mismo criterio que el grandfathering de COM-016). El mismo "
                  "parque a lista vigente daría USD %s/año (ticket USD %s): esa diferencia de USD %s/año "
                  "es lo que decidimos no cobrarle a la base, no plata perdida.\n\n" % (
                      plata(ticket_real), plata(ticket_plan), desvio,
                      plata(a_lista), plata(ticket_lista), plata(a_lista - contratado)))
    lineas.append("> **Para proyectar clientes nuevos se usa la lista vigente (USD %s de ticket "
                  "promedio), no el promedio de la base.** Mezclar las dos cosas es lo que hacía que el "
                  "plan pareciera descalibrado.\n\n" % plata(ticket_lista))

    if regalados:
        lineas.append("**Sistemas regalados** (entregados sin plan de mantenimiento — su recurrente en 0 "
                      "es la decisión, no un dato faltante): %s.\n\n" %
                      ", ".join(sorted(set("%s%s" % (f["nombre"], " (%s)" % f["sistema"] if f["sistema"] else "")
                                           for f in regalados))))
    otros_en_cero = [f["nombre"] for f in pagan if not (f["ticket"] or 0)]
    if otros_en_cero:
        lineas.append("**Con recurrente en 0 y sin estar marcados como regalados** — o falta cargar el "
                      "plan en el CRM, o hay que marcarlos en `datos-manuales.yml`: %s.\n\n" %
                      ", ".join(sorted(set(otros_en_cero))))

    for c in (man.get("correcciones_pendientes_crm") or []):
        lineas.append("> ⚠️ **El CRM está desactualizado en %s.** Dice: %s. En realidad: %s "
                      "(confirmado el %s). %s\n\n" % (
                          c.get("cliente"), c.get("dice_el_crm"), c.get("es_en_realidad"),
                          c.get("confirmado"), (c.get("nota") or "").strip()))
    if sin_frente:
        lineas.append("**Sin frente asignado** en `datos-manuales.yml`: %s.\n\n" %
                      ", ".join(sorted(set(sin_frente))))

    # Renovaciones: el dato esta en el CRM y es lo unico de este archivo que pide una accion con
    # fecha, asi que va arriba de los upsells y no al final.
    hoy_d = datetime.date.today()
    limite = hoy_d + datetime.timedelta(days=90)
    vencidas = [f for f, _ in activos if f["renovacion"] and f["renovacion"] < hoy_d]
    proximas = [f for f, _ in activos if f["renovacion"] and hoy_d <= f["renovacion"] <= limite]
    if vencidas or proximas:
        lineas.append("## Renovaciones\n\n")
        if vencidas:
            lineas.append("**Vencidas** (la fecha ya pasó y el cliente sigue activo — o se renovó sin "
                          "actualizar el CRM, o hay que cobrarla):\n\n")
            for f in sorted(vencidas, key=lambda x: x["renovacion"]):
                lineas.append("- **%s** — vencía el %s, USD %s/año (%d días).\n" % (
                    f["nombre"], f["renovacion"], plata(f["ticket"]), (hoy_d - f["renovacion"]).days))
            lineas.append("\n")
        if proximas:
            lineas.append("**En los próximos 90 días:**\n\n")
            for f in sorted(proximas, key=lambda x: x["renovacion"]):
                lineas.append("- %s — %s, USD %s/año.\n" % (f["nombre"], f["renovacion"], plata(f["ticket"])))
            lineas.append("\n")

    if upsells:
        lineas.append("## Upsells por cliente\n\n| Cliente | Tipo | USD | Fecha |\n|---|---|---:|---|\n")
        por_id = {f["Id"]: f for f, _ in activos + bajas}
        for cid, lista in sorted(upsells.items(), key=lambda kv: (por_id.get(kv[0], {}).get("nombre") or "")):
            for u in lista:
                lineas.append("| %s | %s | %s | %s |\n" % (
                    (por_id.get(cid, {}).get("nombre") or "cliente %s" % cid),
                    u["tipo"] or "—", plata(u["monto"]), u["fecha"]))
    escribir("clientes.md", "".join(lineas), dry_run)
    return {"activos": len(activos), "contratado": contratado, "cobrable": cobrable}


# ---------------------------------------------------------------------------- pipeline
def gen_pipeline(cx, man, dry_run):
    with cx.cursor() as cur:
        cur.execute("""
            SELECT EstadoEmbudo etapa, COUNT(*) n,
                   SUM(COALESCE(PresupuestoCotizadoUsd,0)) cotizado
              FROM contactos WHERE DeletedAt IS NULL
             GROUP BY EstadoEmbudo""")
        por_etapa = {f["etapa"]: f for f in cur.fetchall()}
        cur.execute("""
            SELECT NombreNegocio nombre, NombreContacto contacto, Rubro rubro, Zona zona,
                   CanalOrigen canal, Gancho gancho, EstadoEmbudo etapa,
                   PresupuestoCotizadoUsd cotizado, DATE(FechaUltimaActividad) actividad,
                   DATE(FechaRespuesta) respuesta, CanalMensajeria mensajeria
              FROM contactos
             WHERE DeletedAt IS NULL AND EstadoEmbudo IN (%s)
             ORDER BY FechaUltimaActividad DESC""" % ",".join(str(e) for e in ABIERTAS))
        abiertos = cur.fetchall()

    lineas = ["# Pipeline\n", AVISO % ("pipeline", hoy()), "\n"]
    lineas.append("## El embudo, por etapa\n\n| Etapa | Contactos | Cotizado USD |\n|---|---:|---:|\n")
    total = 0
    for codigo, nombre in ETAPAS.items():
        f = por_etapa.get(codigo)
        n = f["n"] if f else 0
        total += n
        lineas.append("| %s | %s | %s |\n" % (nombre, n, plata(f["cotizado"]) if f and f["cotizado"] else "—"))
    lineas.append("| **Total** | **%s** | |\n\n" % n_fmt(total))

    enviados = sum(por_etapa.get(e, {}).get("n", 0) for e in (2, 3, 4, 5, 9, 10, 12))
    respondieron = sum(por_etapa.get(e, {}).get("n", 0) for e in (4, 5, 9, 12))
    presupuestados = sum(por_etapa.get(e, {}).get("n", 0) for e in (5, 9))
    cerrados = por_etapa.get(9, {}).get("n", 0)
    lineas.append("## Conversión del embudo\n\n| Paso | Cantidad | Tasa |\n|---|---:|---:|\n")
    lineas.append("| Contactados (mensaje o más) | %s | — |\n" % n_fmt(enviados))
    lineas.append("| Respondieron | %s | %s |\n" % (n_fmt(respondieron), tasa(respondieron, enviados)))
    lineas.append("| Con presupuesto enviado | %s | %s de los que respondieron |\n" % (
        n_fmt(presupuestados), tasa(presupuestados, respondieron)))
    lineas.append("| Cerrados | %s | %s de los presupuestados |\n\n" % (
        n_fmt(cerrados), tasa(cerrados, presupuestados)))
    lineas.append("> La tasa demo → cierre no sale de acá: el CRM registra el presupuesto enviado, "
                  "no la demo. Hasta que exista ese dato, se anota a mano en `metricas.md`.\n\n")

    # El pipeline vivo no son los 300 "Respondio" historicos: la lista completa pesaba 46 KB y se
    # comia el presupuesto de contexto de un agente (ver 39-presupuesto-contexto). Entran los que
    # tuvieron actividad en los ultimos VENTANA_DIAS, mas todos los que tienen presupuesto enviado o
    # estan derivados a mano, que son los que valen plata sin importar la fecha. El resto se cuenta.
    VENTANA_DIAS = 30
    corte = datetime.date.today() - datetime.timedelta(days=VENTANA_DIAS)
    vivos, dormidos = [], []
    for c in abiertos:
        reciente = c["actividad"] and c["actividad"] >= corte
        (vivos if (reciente or c["etapa"] in (5, 12)) else dormidos).append(c)

    lineas.append("## Leads abiertos\n\n")
    lineas.append("Entran los que tuvieron actividad en los últimos %d días, más todos los que tienen "
                  "presupuesto enviado o están derivados a mano (esos van sin importar la fecha).\n\n"
                  % VENTANA_DIAS)
    if not vivos:
        lineas.append("Ninguno hoy.\n\n")
    else:
        lineas.append("| Negocio | Contacto | Rubro | Zona | Canal | Frente (por gancho) | Etapa | Cotizado USD | Última actividad |\n")
        lineas.append("|---|---|---|---|---|---|---|---:|---|\n")
        for c in vivos:
            lineas.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |\n" % (
                c["nombre"] or "—", c["contacto"] or "—", c["rubro"] or "—", c["zona"] or "—",
                CANALES.get(c["canal"], "—"),
                GANCHO_A_FRENTE.get(c["gancho"], "— *sin gancho*"),
                ETAPAS.get(c["etapa"], "?"),
                plata(c["cotizado"]) if c["cotizado"] else "—", c["actividad"] or "—"))
        lineas.append("\n")

    if dormidos:
        por_etapa_d = defaultdict(int)
        for c in dormidos:
            por_etapa_d[ETAPAS.get(c["etapa"], "?")] += 1
        detalle = ", ".join("%d en %s" % (n, e) for e, n in sorted(por_etapa_d.items()))
        ultima = max(c["actividad"] for c in dormidos if c["actividad"])
        lineas.append("**Dormidos:** otros %d leads siguen en etapa abierta pero sin actividad en más de "
                      "%d días (%s; el más reciente movió el %s). No se listan uno por uno a propósito — "
                      "son decisión de reactivar o marcar fríos, no seguimiento. Para verlos: el CRM.\n"
                      % (len(dormidos), VENTANA_DIAS, detalle, ultima))
    escribir("pipeline.md", "".join(lineas), dry_run)


def n_fmt(n):
    return "{:,}".format(n).replace(",", ".")


def tasa(parte, total):
    return "%.1f%%" % (parte * 100.0 / total) if total else "—"


# ---------------------------------------------------------------------------- metricas
def gen_metricas(cx, man, dry_run):
    umbral = Decimal(str(man["umbral_ministerio_usd_mes"]))
    with cx.cursor() as cur:
        cur.execute("""SELECT DATE(FechaAlta) alta, TicketAnualUsd ticket, PrimerAnioGratis gratis,
                              Activo activo
                         FROM clientes WHERE DeletedAt IS NULL ORDER BY FechaAlta""")
        clientes = cur.fetchall()
        cur.execute("""SELECT DATE(Fecha) fecha, MontoUsd monto FROM upsells
                        WHERE DeletedAt IS NULL ORDER BY Fecha""")
        upsells = cur.fetchall()
        cur.execute("""SELECT DATE(FechaCompletado) fecha, COUNT(*) n FROM contactos
                        WHERE DeletedAt IS NULL AND EstadoEmbudo = 9 AND FechaCompletado IS NOT NULL
                        GROUP BY DATE(FechaCompletado)""")
        cierres = cur.fetchall()

    primero = min([c["alta"] for c in clientes if c["alta"]] or [datetime.date.today()])
    meses = []
    cursor_mes = datetime.date(primero.year, primero.month, 1)
    fin = datetime.date.today().replace(day=1)
    while cursor_mes <= fin:
        meses.append(cursor_mes)
        cursor_mes = (cursor_mes.replace(day=28) + datetime.timedelta(days=7)).replace(day=1)

    lineas = ["# Métricas reales contra el plan\n", AVISO % ("metricas", hoy()), "\n"]
    lineas.append("El plan financiero (`olvidata-ceo.md`) fija la decisión de salida del Ministerio en "
                  "**USD %s/mes de recurrente durante 6 meses seguidos**. Esta es la tabla donde ese "
                  "número se mide en vez de estimarse.\n\n" % plata(umbral))
    lineas.append("**Cómo leer la serie:** el CRM no fecha las bajas (solo marca `Activo=0`), así que un "
                  "cliente que se fue sigue contando desde su alta hasta hoy. El último mes de esta tabla "
                  "queda entonces por encima del total de `clientes.md`, que sí excluye a los inactivos. "
                  "La diferencia es exactamente el recurrente de las bajas.\n\n")
    lineas.append("| Mes | Clientes activos | Recurrente contratado USD/mes | Cobrable USD/mes | "
                  "Altas | No recurrente del mes USD | ¿Supera el umbral? |\n|---|---:|---:|---:|---:|---:|---|\n")

    seguidos, racha_max = 0, 0
    for mes in meses:
        sig = (mes.replace(day=28) + datetime.timedelta(days=7)).replace(day=1)
        vivos = [c for c in clientes if c["alta"] and c["alta"] < sig]
        # Una baja no tiene fecha en el CRM: `Activo=0` es el estado de hoy, asi que para los meses
        # pasados se cuenta al cliente como vivo desde su alta. Queda declarado para no leer la
        # serie como si las bajas estuvieran fechadas.
        contratado = sum((c["ticket"] or 0) for c in vivos) / 12
        cobrable = sum((c["ticket"] or 0) for c in vivos if not c["gratis"]) / 12
        altas = len([c for c in clientes if c["alta"] and mes <= c["alta"] < sig])
        ups = sum(u["monto"] for u in upsells if u["fecha"] and mes <= u["fecha"] < sig)
        supera = cobrable >= umbral
        seguidos = seguidos + 1 if supera else 0
        racha_max = max(racha_max, seguidos)
        lineas.append("| %s | %d | %s | %s | %s | %s | %s |\n" % (
            mes.strftime("%Y-%m"), len(vivos), plata(contratado), plata(cobrable),
            altas or "—", plata(ups) if ups else "—", "sí" if supera else "no"))

    total_nr = sum(u["monto"] for u in upsells)
    meses_con_nr = len({(u["fecha"].year, u["fecha"].month) for u in upsells if u["fecha"]})
    lineas.append("\n## Setup + recurrente: las dos mitades del ingreso\n\n")
    lineas.append("El plan tiene que mirar las dos (indicación de Joaquín, 2026-10-16: *\"tener en "
                  "cuenta el precio de setup + recurrente en todo el plan\"*). No se suman en una sola "
                  "línea porque no se comportan igual: el setup entra una vez por cliente y el "
                  "recurrente vuelve todos los años.\n\n")
    lineas.append("| Concepto | Valor |\n|---|---:|\n")
    lineas.append("| Ingreso no recurrente acumulado (setup, cuotas de implementación, trabajo adicional) | USD %s |\n" % plata(total_nr))
    lineas.append("| Promedio por mes con movimiento (%d meses) | USD %s |\n" % (
        meses_con_nr, plata(total_nr / meses_con_nr) if meses_con_nr else 0))
    lineas.append("| Recurrente anual contratado | USD %s |\n" % plata(
        sum((c["ticket"] or 0) for c in clientes if c["activo"])))
    lineas.append("\n**Por qué el semáforo de abajo usa solo el recurrente:** la decisión de dejar el "
                  "Ministerio es sostener un ingreso **sin vender nada nuevo ese mes**. El setup es "
                  "ingreso real y hoy es la mayor parte de la facturación, pero depende de cerrar un "
                  "cliente nuevo: si se cuenta en el umbral, el mes que no se cierra nada el sueldo "
                  "desaparece. Para medir capacidad de pago de un proyecto o la caja del año, sí van "
                  "los dos.\n")
    lineas.append("\n## Semáforo de la decisión del Ministerio\n\n")
    ultimo_cobrable = sum((c["ticket"] or 0) for c in clientes if c["activo"] and not c["gratis"]) / 12
    falta = umbral - ultimo_cobrable
    lineas.append("- Recurrente cobrable hoy: **USD %s/mes**. Umbral: USD %s/mes.\n" % (
        plata(ultimo_cobrable), plata(umbral)))
    lineas.append("- Faltan **USD %s/mes** (%.0f%% del umbral) para cruzarlo.\n" % (
        plata(falta), falta * 100 / umbral) if falta > 0 else
        "- **Umbral cruzado.** Meses consecutivos por encima: %d de los 6 que pide el plan.\n" % seguidos)
    lineas.append("- Meses consecutivos por encima del umbral, a hoy: **%d** (máximo histórico: %d). "
                  "El plan pide 6.\n\n" % (seguidos, racha_max))

    lineas.append("## Lo que todavía no se puede medir desde el CRM\n\n")
    lineas.append("- **Tasa demo → cierre:** el CRM registra presupuesto enviado, no la demo. Falta el "
                  "dato de origen, no el cálculo.\n")
    lineas.append("- **Conversión asistida de Instagram:** `CanalOrigen` distingue Instagram orgánico de "
                  "Ads, pero no hay forma de atribuir un cierre a una publicación.\n")
    lineas.append("- **Cierres por frente:** el frente vive hoy en `datos-manuales.yml` para clientes y "
                  "se infiere del gancho para leads; mientras `Contacto` no tenga `FrenteComercial`, el "
                  "corte por frente es aproximado.\n")
    lineas.append("- **Costos:** se descuentan en `costos.md`, que es a mano. Las cifras de arriba son "
                  "ingreso recurrente **bruto**, no neto.\n")
    if cierres:
        lineas.append("\n%d contacto(s) marcados Cerrado con fecha de completado en el CRM.\n" %
                      sum(c["n"] for c in cierres))
    escribir("metricas.md", "".join(lineas), dry_run)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("que", choices=["clientes", "pipeline", "metricas", "todo"])
    ap.add_argument("--dry-run", action="store_true", help="muestra el resultado sin escribir los .md")
    args = ap.parse_args()

    man = manuales()
    cx = conectar()
    try:
        if args.que in ("clientes", "todo"):
            gen_clientes(cx, man, args.dry_run)
        if args.que in ("pipeline", "todo"):
            gen_pipeline(cx, man, args.dry_run)
        if args.que in ("metricas", "todo"):
            gen_metricas(cx, man, args.dry_run)
    finally:
        cx.close()


if __name__ == "__main__":
    main()
