#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
evals.py - suite de evals del harness del estudio.

Responde una sola pregunta: cuando cambiamos una instruction, un .agent.md o la carga
de arranque de un rol, ¿el agente quedo mejor o peor? Hasta ahora eso se validaba por
intuicion. Un catalogo de 45 reglas que el agente no aplica es peor que 10 que si:
ocupa contexto y da falsa seguridad.

No evalua el modelo: evalua NUESTRA escritura. Si una regla esta mal ubicada, mal
redactada o enterrada en un archivo de 67 KB, el eval lo muestra.

Spec: `.github/instructions/40-evals-del-harness.instructions.md`
Casos: `docs/evals/casos.yml` (todos derivados de fallos reales)

ESTE SCRIPT NO GASTA UN TOKEN POR SI SOLO. Prepara los prompts y gradea las respuestas;
las corridas las dispara quien orquesta, despues de ver el costo.

Flujo:
    python scripts/evals.py validar                          # estructura de casos.yml
    python scripts/evals.py listar   --rol implementador-dotnet
    python scripts/evals.py costo    --rol implementador-dotnet   # <-- SIEMPRE antes de correr
    python scripts/evals.py preparar --rol implementador-dotnet   # escribe los .prompt.txt
    #   -> el orquestador corre cada prompt en un subagente limpio y guarda <id>-<n>.out.txt
    python scripts/evals.py gradear  --corrida 2026-09-25-implementador-dotnet

Salida: 0 = ok / suite verde | 1 = error de uso o casos fallados.
Origen: gap 2 del research de ingenieria de agentes, 2026-09-25.
"""
import io
import os
import re
import sys
import glob
import argparse
import datetime
import unicodedata

try:
    import yaml
except ImportError:
    print("ERROR: falta pyyaml.  pip install pyyaml")
    sys.exit(1)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)

CASOS = "docs/evals/casos.yml"
CORRIDAS = "docs/evals/corridas"

# Precio de lista API, fuente: 27-presupuesto-parametros.instructions.md (lineas 241-242).
# Si cambia alla, cambiarlo aca: este script no es la fuente de verdad del precio.
PRECIO = {
    "opus":   {"in": 5.00, "out": 25.00},    # claude-opus-5
    "sonnet": {"in": 3.00, "out": 15.00},    # claude-sonnet-5
}

# Arranque tipico de un caso: el .agent.md del rol + las instructions que carga completas
# + el enunciado. Medido grueso; sirve para dimensionar el gasto, no para facturar.
TOKENS_IN_POR_CORRIDA = 45000
TOKENS_OUT_POR_CORRIDA = 1200

OBLIGATORIOS = ("id", "rol", "titulo", "origen", "fuente", "entrada", "grader", "metrica")
FUENTES_VALIDAS = ("regresiones-manuales", "dataset-calibracion", "trazas")


def _norm(s):
    """minusculas sin acentos, para comparar sin depender de como se escribio."""
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.lower()


def cargar():
    if not os.path.exists(CASOS):
        print("ERROR: no existe %s" % CASOS)
        sys.exit(1)
    with io.open(CASOS, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    return d or {}


def _activos(d, rol=None, solo=None):
    out = []
    for c in d.get("casos", []):
        if c.get("estado", "activo") != "activo":
            continue
        if rol and c.get("rol") != rol:
            continue
        if solo and c.get("id") not in solo:
            continue
        out.append(c)
    return out


def _k(caso):
    """cuantas corridas pide la metrica del caso."""
    m = caso.get("metrica", "pass@2")
    n = re.search(r"(\d+)\s*$", m)
    return int(n.group(1)) if n else 2


# ---------------------------------------------------------------- validar

def validar(a):
    d = cargar()
    casos = d.get("casos", [])
    errores, avisos = [], []
    vistos = set()

    for c in casos:
        cid = c.get("id", "(sin id)")
        for campo in OBLIGATORIOS:
            if not c.get(campo):
                errores.append("%s: falta el campo obligatorio '%s'" % (cid, campo))
        if cid in vistos:
            errores.append("%s: id duplicado" % cid)
        vistos.add(cid)

        if c.get("fuente") not in FUENTES_VALIDAS:
            errores.append("%s: fuente '%s' no valida (los casos salen de fallos reales: %s)"
                           % (cid, c.get("fuente"), "|".join(FUENTES_VALIDAS)))

        g = c.get("grader") or {}
        if g.get("tipo") == "codigo":
            if not any(g.get(k) for k in ("debe_contener_alguno", "debe_contener_todos",
                                          "no_debe_contener_alguno", "debe_citar")):
                errores.append("%s: grader de codigo sin ninguna assertion" % cid)
        elif g.get("tipo") not in ("modelo", "humano"):
            errores.append("%s: grader.tipo desconocido: %r" % (cid, g.get("tipo")))

        if not c.get("criterio_pass"):
            avisos.append("%s: sin 'criterio_pass' legible (el grader mecanico no se explica solo)" % cid)

        # Regla de redaccion 1 de la instruccion 40: no gradear la secuencia de pasos.
        # Solo dispara sobre `debe_contener_todos`: exigir "primero" Y "despues" juntos es
        # exigir un camino. Ofrecerlos como alternativas (debe_contener_alguno) es legitimo.
        txt = _norm(" ".join(g.get("debe_contener_todos") or []))
        if "primero" in txt and "despues" in txt:
            avisos.append("%s: el grader parece exigir una secuencia de pasos; se grada el "
                          "resultado, no el camino (instruccion 40)" % cid)

    activos = len(_activos(d))
    print("Casos: %d totales, %d activos" % (len(casos), activos))
    for e in errores:
        print("  ERROR  %s" % e)
    for w in avisos:
        print("  aviso  %s" % w)
    if activos > 40:
        print("  aviso  la suite paso los 40 casos activos: podar por poder de "
              "discriminacion, no por antiguedad (instruccion 40)")
    if not errores:
        print("OK  estructura valida")
    return 1 if errores else 0


# ---------------------------------------------------------------- listar

def listar(a):
    d = cargar()
    casos = _activos(d, a.rol)
    if not casos:
        print("Sin casos activos%s." % ((" para el rol %s" % a.rol) if a.rol else ""))
        return 0
    print("%-12s %-22s %-9s %-7s %s" % ("id", "rol", "metrica", "plata", "titulo"))
    print("-" * 104)
    for c in casos:
        print("%-12s %-22s %-9s %-7s %s"
              % (c["id"], c["rol"], c.get("metrica", "pass@2"),
                 "si" if c.get("peso_plata") else "-", c["titulo"][:46]))
    print("\n%d casos | %d corridas si se ejecuta todo" % (len(casos), sum(_k(c) for c in casos)))
    return 0


# ---------------------------------------------------------------- costo

def costo(a):
    d = cargar()
    casos = _activos(d, a.rol)
    if not casos:
        print("Sin casos activos%s." % ((" para el rol %s" % a.rol) if a.rol else ""))
        return 0
    corridas = sum(_k(c) for c in casos)
    tin = corridas * TOKENS_IN_POR_CORRIDA
    tout = corridas * TOKENS_OUT_POR_CORRIDA

    print("Alcance: %d casos activos%s -> %d corridas"
          % (len(casos), (" (rol %s)" % a.rol) if a.rol else "", corridas))
    print("Tokens estimados: %.1fM input + %.0fk output\n" % (tin / 1e6, tout / 1e3))
    print("%-8s %10s %10s %10s" % ("modelo", "input", "output", "TOTAL"))
    for m in ("opus", "sonnet"):
        ci = tin / 1e6 * PRECIO[m]["in"]
        co = tout / 1e6 * PRECIO[m]["out"]
        print("%-8s %9.2f$ %9.2f$ %9.2f$" % (m, ci, co, ci + co))
    print("\nEstimacion gruesa (arranque tipico de %dk tokens por corrida), a precio de lista"
          % (TOKENS_IN_POR_CORRIDA // 1000))
    print("API. Con suscripcion no se factura por token, pero el gasto de ventana es real.")
    print("Fuente del precio: 27-presupuesto-parametros.instructions.md")
    return 0


# ---------------------------------------------------------------- preparar

def preparar(a):
    d = cargar()
    casos = _activos(d, a.rol, a.solo.split(",") if a.solo else None)
    if not casos:
        print("Sin casos activos para ese filtro.")
        return 1

    etiqueta = a.etiqueta or "%s-%s" % (datetime.date.today().isoformat(), a.rol or "todos")
    dest = os.path.join(CORRIDAS, etiqueta)
    if not os.path.isdir(dest):
        os.makedirs(dest)

    n = 0
    for c in casos:
        for i in range(1, _k(c) + 1):
            p = os.path.join(dest, "%s-%d.prompt.txt" % (c["id"], i))
            with io.open(p, "w", encoding="utf-8", newline="") as f:
                f.write(c["entrada"].rstrip() + "\n")
            n += 1

    with io.open(os.path.join(dest, "README.txt"), "w", encoding="utf-8", newline="") as f:
        f.write(
            "Corrida de evals: %s\n"
            "Casos: %d | Prompts: %d\n\n"
            "Cada prompt se corre en un SUBAGENTE LIMPIO del rol que indica el caso,\n"
            "sin contarle que es un eval y sin el contexto de los otros casos\n"
            "(entorno limpio entre corridas, instruccion 40).\n"
            "La respuesta se guarda al lado, con el mismo nombre y extension .out.txt\n\n"
            "Gradear:  python scripts/evals.py gradear --corrida %s\n"
            % (etiqueta, len(casos), n, etiqueta))

    print("OK  %d prompts en %s" % (n, dest))
    print("    correr cada uno en un subagente limpio del rol del caso,")
    print("    guardar la respuesta como <id>-<n>.out.txt en la misma carpeta,")
    print("    y despues: python scripts/evals.py gradear --corrida %s" % etiqueta)
    return 0


# ---------------------------------------------------------------- gradear

def _gradear_uno(caso, salida):
    """devuelve (score 0..1, [motivos])."""
    g = caso.get("grader") or {}
    if g.get("tipo") != "codigo":
        return (None, ["grader '%s': se revisa a mano" % g.get("tipo")])

    t = _norm(salida)
    motivos = []
    ok = True

    req = g.get("debe_contener_alguno") or []
    if req and not any(_norm(x) in t for x in req):
        ok = False
        motivos.append("no menciona ninguno de: %s" % ", ".join(req))

    for x in (g.get("debe_contener_todos") or []):
        if _norm(x) not in t:
            ok = False
            motivos.append("falta: %s" % x)

    for x in (g.get("no_debe_contener_alguno") or []):
        if _norm(x) in t:
            ok = False
            motivos.append("contiene lo que no debia: %s" % x)

    cit = g.get("debe_citar") or []
    if cit and not any(_norm(x) in t for x in cit):
        ok = False
        motivos.append("no cita: %s" % ", ".join(cit))

    if ok:
        return (1.0, [])

    for cp in (g.get("credito_parcial") or []):
        if _norm(cp.get("cuando_contiene", "")) in t:
            motivos.append("credito parcial %.1f" % cp.get("valor", 0.5))
            return (float(cp.get("valor", 0.5)), motivos)

    return (0.0, motivos)


def gradear(a):
    d = cargar()
    dest = os.path.join(CORRIDAS, a.corrida)
    if not os.path.isdir(dest):
        print("ERROR: no existe la corrida %s" % dest)
        return 1

    porcaso = {c["id"]: c for c in d.get("casos", [])}
    res = {}
    faltan = []

    for p in sorted(glob.glob(os.path.join(dest, "*.prompt.txt"))):
        base = os.path.basename(p)[:-len(".prompt.txt")]
        cid, _, i = base.rpartition("-")
        caso = porcaso.get(cid)
        if not caso:
            continue
        out = p.replace(".prompt.txt", ".out.txt")
        if not os.path.exists(out):
            faltan.append(base)
            continue
        with io.open(out, encoding="utf-8") as f:
            score, motivos = _gradear_uno(caso, f.read())
        res.setdefault(cid, []).append((int(i), score, motivos))

    if faltan:
        print("Sin respuesta todavia (%d): %s\n" % (len(faltan), ", ".join(faltan[:8])))

    if not res:
        print("No hay ninguna respuesta gradeable en %s." % dest)
        return 1

    fallados, manuales = [], []
    print("%-12s %-9s %-7s %s" % ("id", "metrica", "result", "detalle"))
    print("-" * 100)
    for cid in sorted(res):
        caso = porcaso[cid]
        met = caso.get("metrica", "pass@2")
        scores = [s for _, s, _ in res[cid]]
        if any(s is None for s in scores):
            manuales.append(cid)
            print("%-12s %-9s %-7s %s" % (cid, met, "manual", "grader no mecanico"))
            continue
        # pass^k exige TODAS las corridas; pass@k alcanza con una.
        paso = all(s >= 1.0 for s in scores) if met.startswith("pass^") else any(s >= 1.0 for s in scores)
        detalle = " ".join("%.1f" % s for s in scores)
        motivos = [m for _, _, ms in res[cid] for m in ms]
        if motivos:
            detalle += "  | " + "; ".join(dict.fromkeys(motivos))[:60]
        if not paso:
            fallados.append(cid)
        print("%-12s %-9s %-7s %s" % (cid, met, "PASS" if paso else "FAIL", detalle))

    total = len(res) - len(manuales)
    print("\n%d/%d casos mecanicos en PASS%s"
          % (total - len(fallados), total,
             ("  |  %d a revisar a mano" % len(manuales)) if manuales else ""))
    if fallados:
        print("FAIL: %s" % ", ".join(fallados))
    print("\nLeer los transcripts: los FAIL completos y 2 PASS al azar. Un caso que pasa por el")
    print("motivo equivocado contamina la metrica mas que uno que falla (instruccion 40).")
    return 1 if fallados else 0


def main():
    ap = argparse.ArgumentParser(description="Evals del harness (instruccion 40).")
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("validar", help="chequea la estructura de casos.yml")

    l = sub.add_parser("listar", help="casos activos")
    l.add_argument("--rol", default=None)

    c = sub.add_parser("costo", help="cuanto sale correr la suite ANTES de correrla")
    c.add_argument("--rol", default=None)

    p = sub.add_parser("preparar", help="escribe los prompts de la corrida (no ejecuta nada)")
    p.add_argument("--rol", default=None)
    p.add_argument("--solo", default=None, help="ids separados por coma")
    p.add_argument("--etiqueta", default=None)

    g = sub.add_parser("gradear", help="aplica los graders de codigo a las respuestas")
    g.add_argument("--corrida", required=True)

    a = ap.parse_args()
    if a.cmd == "validar":
        return validar(a)
    if a.cmd == "listar":
        return listar(a)
    if a.cmd == "costo":
        return costo(a)
    if a.cmd == "preparar":
        return preparar(a)
    if a.cmd == "gradear":
        return gradear(a)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
