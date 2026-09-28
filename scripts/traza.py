#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
traza.py - observabilidad del *durante* de una corrida de agente.

`contexto.py presupuesto` mide lo que un agente carga ANTES de empezar. Este script
mide lo que pasa DESPUES: cuantos reintentos hubo, que criterio fallo, y -- el dato
mas valioso -- que regla hubo que releer en el medio del trabajo porque no estaba
en la carga de arranque. Una regla que se relee siempre es una regla mal ubicada.

Sin este dato, cada ajuste a una instruction es intuicion: no se puede saber si
mejoro o empeoro al agente. Con el, las debilidades del harness salen de trazas
reales, y los casos de eval (instruccion 40) salen de fallos que pasaron de verdad.

Implementa `.github/instructions/39-presupuesto-contexto.instructions.md`, seccion 8.

Uso:
    python scripts/traza.py registrar --proyecto marihogar --etapa qa --lote 2 \\
        --reintentos 1 --criterios-fallados "MH-014,REG-004" \\
        --reglas-releidas "32#combos,30" --arranque-kb 180 --nota "..."

    python scripts/traza.py resumen [--proyecto X] [--desde AAAA-MM-DD]
    python scripts/traza.py listar  [--proyecto X] [--n 20]

Salida: 0 = ok | 1 = error de uso o proyecto inexistente.
Origen: gap 3 del research de ingenieria de agentes, 2026-09-25.
"""
import io
import os
import sys
import argparse
import datetime
import collections

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)

TSV = "docs/trazas/trazas.tsv"
CABECERA_TSV = (
    "fecha\tproyecto\tetapa\tlote\treintentos\t"
    "criterios_fallados\treglas_releidas\tarranque_kb\tnota\n"
)

# Etapas del flujo Discovery -> Cierre, mas las corridas sueltas de los agentes de negocio.
ETAPAS = ("discovery", "analisis", "diseno", "arquitectura", "presupuesto",
          "implementacion", "qa", "documentacion", "calibracion", "otro")

MARCA = "### Traza de corrida"


def _hoy():
    return datetime.date.today().isoformat()


def _leer(p):
    try:
        return io.open(p, encoding="utf-8").read()
    except Exception:
        return ""


def _lista(s):
    """'a, b ,,c' -> ['a','b','c'] (vacio -> [])."""
    if not s:
        return []
    return [x.strip() for x in s.replace(";", ",").split(",") if x.strip()]


def _campo(xs):
    return " ".join(xs) if xs else "-"


def registrar(a):
    proyecto_dir = os.path.join("docs", a.proyecto)
    if not os.path.isdir(proyecto_dir):
        print("ERROR: no existe docs/%s/ -- proyecto mal escrito?" % a.proyecto)
        return 1
    if a.etapa not in ETAPAS:
        print("ERROR: etapa '%s' no valida. Opciones: %s" % (a.etapa, ", ".join(ETAPAS)))
        return 1

    fecha = a.fecha or _hoy()
    criterios = _lista(a.criterios_fallados)
    reglas = _lista(a.reglas_releidas)
    lote = str(a.lote) if a.lote else "-"

    # --- 1. bloque legible en la trazabilidad del proyecto (<= 5 lineas) ---
    lineas = [
        "",
        "%s -- %s / etapa %s%s" % (MARCA, fecha, a.etapa,
                                   (" / lote %s" % lote) if lote != "-" else ""),
        "- Reintentos: %d" % a.reintentos,
        "- Criterios fallados: %s" % (", ".join(criterios) if criterios else "ninguno"),
        "- Reglas releidas: %s" % (", ".join(reglas) if reglas else "ninguna"),
    ]
    if a.arranque_kb:
        lineas.append("- Arranque real: %s KB (~%dk tokens)"
                      % (a.arranque_kb, int(a.arranque_kb * 1024 / 4000)))
    if a.nota:
        lineas.append("- Nota: %s" % a.nota)
    lineas.append("")

    traz = os.path.join(proyecto_dir, "trazabilidad.md")
    previo = _leer(traz)
    if not previo:
        previo = "# Trazabilidad -- %s\n" % a.proyecto
    if previo and not previo.endswith("\n"):
        previo += "\n"
    with io.open(traz, "w", encoding="utf-8", newline="") as f:
        f.write(previo + "\n".join(lineas) + "\n")

    # --- 2. linea en el indice consultable, para agregar despues ---
    if not os.path.isdir("docs/trazas"):
        os.makedirs("docs/trazas")
    nuevo = not os.path.exists(TSV)
    with io.open(TSV, "a", encoding="utf-8", newline="") as f:
        if nuevo:
            f.write(CABECERA_TSV)
        f.write("\t".join([
            fecha, a.proyecto, a.etapa, lote, str(a.reintentos),
            _campo(criterios), _campo(reglas),
            str(a.arranque_kb or "-"),
            (a.nota or "-").replace("\t", " "),
        ]) + "\n")

    print("OK  traza registrada en %s y %s" % (traz, TSV))
    if reglas:
        print("    reglas releidas: %s  <- revisar si deberian estar en el arranque del rol"
              % ", ".join(reglas))
    return 0


def _filas(proyecto=None, desde=None):
    txt = _leer(TSV)
    if not txt:
        return []
    out = []
    for ln in txt.splitlines()[1:]:
        c = ln.split("\t")
        if len(c) < 9:
            continue
        if proyecto and c[1] != proyecto:
            continue
        if desde and c[0] < desde:
            continue
        out.append(c)
    return out


def listar(a):
    filas = _filas(a.proyecto, a.desde)
    if not filas:
        print("Sin trazas registradas todavia (%s)." % TSV)
        return 0
    print("fecha       proyecto              etapa           lote re criterios / reglas releidas")
    print("-" * 100)
    for c in filas[-a.n:]:
        print("%-11s %-21s %-15s %-4s %-2s %s | %s"
              % (c[0], c[1][:21], c[2][:15], c[3], c[4], c[5][:28], c[6][:28]))
    return 0


def resumen(a):
    filas = _filas(a.proyecto, a.desde)
    if not filas:
        print("Sin trazas registradas todavia (%s)." % TSV)
        print("Se registran al cerrar cada etapa: python scripts/traza.py registrar --help")
        return 0

    reglas = collections.Counter()
    criterios = collections.Counter()
    reint = collections.defaultdict(list)
    for c in filas:
        for r in c[6].split():
            if r != "-":
                reglas[r] += 1
        for k in c[5].split():
            if k != "-":
                criterios[k] += 1
        try:
            reint[c[2]].append(int(c[4]))
        except ValueError:
            pass

    print("Trazas analizadas: %d%s\n" % (len(filas),
          (" (proyecto %s)" % a.proyecto) if a.proyecto else ""))

    print("Reglas releidas con mas frecuencia  -- candidatas a subir al arranque del rol")
    if reglas:
        for r, n in reglas.most_common(10):
            marca = "  <-- mal ubicada" if n >= 3 else ""
            print("  %3d x  %s%s" % (n, r, marca))
    else:
        print("  (ninguna)")

    print("\nCriterios/items que fallan en mas de un proyecto  -- candidatos a regla del 32 o item del catalogo")
    repetidos = [(k, n) for k, n in criterios.most_common() if n > 1]
    if repetidos:
        for k, n in repetidos[:10]:
            print("  %3d x  %s" % (n, k))
    else:
        print("  (ninguno)")

    print("\nReintentos promedio por etapa  -- promedio alto = brief de hand-off flojo (instruccion 39 seccion 4)")
    for etapa, vals in sorted(reint.items(), key=lambda kv: -(sum(kv[1]) / float(len(kv[1])))):
        prom = sum(vals) / float(len(vals))
        marca = "  <-- revisar el brief" if prom >= 1.5 else ""
        print("  %-15s %.1f  (%d corridas)%s" % (etapa, prom, len(vals), marca))
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="Traza de corrida de los agentes del estudio (instruccion 39, seccion 8).")
    sub = ap.add_subparsers(dest="cmd")

    r = sub.add_parser("registrar", help="registra la traza al cerrar una etapa")
    r.add_argument("--proyecto", required=True)
    r.add_argument("--etapa", required=True, help="|".join(ETAPAS))
    r.add_argument("--lote", default=None, help="numero de lote si la corrida fue por lotes")
    r.add_argument("--reintentos", type=int, default=0,
                   help="veces que hubo que rehacer algo (build fallido, criterio mal interpretado)")
    r.add_argument("--criterios-fallados", default="",
                   help="ids separados por coma, aunque despues se hayan cerrado")
    r.add_argument("--reglas-releidas", default="",
                   help="instructions/secciones que hubo que reabrir en el medio, ej. '32#combos,30'")
    r.add_argument("--arranque-kb", type=int, default=0)
    r.add_argument("--nota", default="")
    r.add_argument("--fecha", default=None, help="AAAA-MM-DD (default: hoy)")

    s = sub.add_parser("resumen", help="agrega las trazas y marca lo que conviene corregir")
    s.add_argument("--proyecto", default=None)
    s.add_argument("--desde", default=None, help="AAAA-MM-DD")

    l = sub.add_parser("listar", help="ultimas trazas registradas")
    l.add_argument("--proyecto", default=None)
    l.add_argument("--desde", default=None)
    l.add_argument("--n", type=int, default=20)

    a = ap.parse_args()
    if a.cmd == "registrar":
        return registrar(a)
    if a.cmd == "resumen":
        return resumen(a)
    if a.cmd == "listar":
        return listar(a)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
