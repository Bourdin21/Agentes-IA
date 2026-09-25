#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
contexto.py - presupuesto de contexto de los agentes del estudio.

Implementa las herramientas de `.github/instructions/39-presupuesto-contexto.instructions.md`:
un agente que arranca con media ventana de contexto gastada en historia ajena a la
tarea razona peor. Este script mide ese arranque y da los indices para no cargar
cuerpos completos.

Uso:
    python scripts/contexto.py presupuesto [proyecto]   # arranque de cada agente vs. su techo
    python scripts/contexto.py indice [alias|ruta]      # 1 linea por seccion de un archivo grande
    python scripts/contexto.py resumenes                # regenera los cat_resumen.txt (indices planos)

Salida: 0 = todos los agentes bajo su techo | 1 = alguno lo excede.
Origen: auditoria de degradacion de contexto 2026-09-25 (QA en marihogar arrancaba con ~510k tokens).
"""
import io, os, re, sys, glob

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)

# Techo de arranque por agente, en tokens. Fuente: instruccion 39, seccion 1.
# El numero sale de cuantos documentos de etapa previa necesita el rol para hacer su trabajo,
# no de una fraccion de la ventana: el arquitecto necesita analisis + diseño, el presupuestador
# necesita ademas arquitectura y el dataset, y los de modo Agent tienen que dejar la ventana
# libre para el codigo y la navegacion.
TECHOS = {
    "analista-funcional": 40000,        # arranca del pedido: su memoria vigente y poco mas
    "disenador-funcional": 40000,       # analisis del alcance + su memoria vigente
    "documentador": 40000,              # la seccion del sprint en 5 y 6
    "arquitecto-mvc": 50000,            # analisis + diseño + su memoria vigente
    "presupuesto-mvc": 60000,           # analisis + diseño + arquitectura + dataset + su memoria
    "implementador-dotnet": 60000,      # el resto de la ventana es para el codigo
    "implementador-astro-front": 60000,
    "qa-mvc": 60000,                    # el resto de la ventana es para navegar y probar
}

# Subagente de Claude Code que encarna a cada .agent.md (su prompt tambien es arranque).
SUBAGENTE = {
    "implementador-dotnet": ".claude/agents/agentes-ia-implementador.md",
    "implementador-astro-front": ".claude/agents/agentes-ia-implementador-astro-front.md",
    "qa-mvc": ".claude/agents/agentes-ia-qa.md",
}

# Marcas que significan "esto NO se carga entero" (instruccion 39, seccion 2): o se entra por
# indice, o se lee solo el bloque vigente / la seccion del alcance.
MARCAS_INDICE = ("indice", "índice", "grep", "sed -n", "solo la seccion", "solo las seccion",
                 "por demanda", "puntero", "cat_resumen", "no la leas entera", "no leer entera",
                 "solo el item", "solo la entrada", "solo el checklist", "bloque vigente",
                 "definiciones vigentes", "ultimo sprint", "solo lo del", "la seccion del",
                 "solo los criterios", "solo el bloque", "solo el alcance", "por seccion",
                 "ultimas entradas", "nunca por cuerpo", "no el archivo completo",
                 "no los archivos", "no el documento entero", "solo la maquina")

# Lineas que hablan de ESCRIBIR un archivo al cerrar, no de cargarlo al arrancar: no son contexto.
MARCAS_ESCRITURA = ("actualizar", "registrar entrada", "agregarlo", "agregar el cierre", "dejar evidencia",
                    "sincronizada", "mantenerla", "se agrega", "cargarlo en", "crear el item",
                    "antes de cerrar la etapa", "al cerrar")

BYTES_POR_TOKEN = 4.0          # aproximacion estable para markdown en castellano
COSTO_INDICE_MIN = 700         # un indice chico igual cuesta el grep y su salida

ALIAS = {
    "00": ".github/instructions/00-operativa-global.instructions.md",
    "25": ".github/instructions/25-frontend-design-system.instructions.md",
    "26": ".github/instructions/26-checklists.instructions.md",
    "27": ".github/instructions/27-presupuesto-parametros.instructions.md",
    "30": ".github/instructions/30-qa-regresiones.instructions.md",
    "32": ".github/instructions/32-estandares-qa-implementador.instructions.md",
    "33": ".github/instructions/33-verificacion-automatizada-qa.instructions.md",
    "34": ".github/instructions/34-integracion-afip-arca.instructions.md",
    "35": ".github/instructions/35-pantalla-control-stock.instructions.md",
    "37": ".github/instructions/37-servicios-externos-fiscales.instructions.md",
    "38": ".github/instructions/38-diseno-pantallas-portal.instructions.md",
    "39": ".github/instructions/39-presupuesto-contexto.instructions.md",
    "regresiones": "docs/qa/regresiones-manuales.yml",
    "catalogo": "docs/patrones/catalogo.yml",
    "dataset": "docs/calibracion/dataset.yml",
}


def leer(p):
    try:
        return io.open(p, encoding="utf-8").read()
    except Exception:
        return ""


def kb(n):
    return n / 1024.0


def tokens(n):
    return int(n / BYTES_POR_TOKEN)


def tam(p):
    try:
        return os.path.getsize(p)
    except OSError:
        return 0


def tam_indice(p):
    """Lo que cuesta un archivo cuando NO se carga entero.

    - memoria de proyecto (`definiciones/`): el bloque vigente, que es lo que el agente si
      lee de punta a punta, mas el indice del resto.
    - catalogo o instruction: solo su indice (headings / ids).
    """
    txt = leer(p)
    if p.endswith(".yml"):
        ls = re.findall(r"^\s*- id: .*$", txt, re.M)
        ls += re.findall(r"^\s*(?:titulo|nombre): .*$", txt, re.M)
        return max(COSTO_INDICE_MIN, sum(len(l) + 1 for l in ls))

    ls = re.findall(r"^#{1,3} .*$", txt, re.M)
    indice = sum(len(l) + 1 for l in ls)
    if "/definiciones/" in p.replace("\\", "/"):
        lineas = txt.split("\n")
        vigente = 0
        for i, l in enumerate(lineas):
            if re.match(r"^## (Definiciones vigentes|Version actual|Versión actual)", l):
                for j in range(i + 1, len(lineas)):
                    if lineas[j].startswith("## "):
                        break
                    vigente += len(lineas[j]) + 1
                break
        if vigente:
            return min(len(txt), vigente + indice)
    return max(COSTO_INDICE_MIN, indice)


# ─────────────────────────────────────────────────────────────────────────────
# presupuesto
# ─────────────────────────────────────────────────────────────────────────────
def _refs_de(texto, proyecto):
    """Archivos que un .agent.md declara cargar, con el modo (completo | indice).

    Se parsea el texto real del agente en vez de mantener la lista aparte: asi la
    medicion no se desincroniza del archivo que manda.
    """
    refs = {}
    seccion = "completo"     # los .agent.md agrupan la carga en bloques "Completas:" / "Por indice —"
    for linea in texto.split("\n"):
        baja = linea.lower()
        if not linea.startswith(("-", "*", " ")) and linea.strip():
            # cabecera de bloque: fija el modo de las referencias que vienen abajo
            if baja.startswith("completas"):
                seccion = "completo"
            elif any(m in baja for m in MARCAS_INDICE):
                seccion = "indice"
            elif baja.startswith(("carga de contexto", "instrucciones", "input esperado", "salida", "reglas")):
                seccion = "completo"
        if any(m in baja for m in MARCAS_ESCRITURA):
            continue        # habla de actualizar ese archivo al cerrar, no de cargarlo al arrancar
        modo = "indice" if (seccion == "indice" or any(m in baja for m in MARCAS_INDICE)) else "completo"
        encontrados = re.findall(r"[\w./<>-]*(?:instructions|docs)/[\w./<>-]+\.(?:md|yml|txt)", linea)
        encontrados += re.findall(r"\b\d\d-[\w-]+\.instructions\.md", linea)
        for ref in encontrados:
            ref = ref.lstrip("./").replace("C:/Sistemas/Agentes-IA/", "")
            if ref.endswith(".instructions.md") and not ref.startswith(".github"):
                ref = ".github/instructions/" + os.path.basename(ref)
            if ref.startswith("instructions/"):
                ref = ".github/" + ref
            ref = ref.replace("<proyecto>", proyecto).replace("<proyecto-origen>", proyecto)
            if "*" in ref or "{" in ref or "<" in ref:
                continue
            if not os.path.exists(ref):
                continue
            # el modo mas barato gana: si en algun lugar se aclara que va por indice, va por indice
            if refs.get(ref) != "indice":
                refs[ref] = modo
    return refs


def presupuesto(proyecto):
    filas, excede = [], False
    for ruta in sorted(glob.glob(".github/agents/*.agent.md")):
        nombre = os.path.basename(ruta).replace(".agent.md", "")
        techo = TECHOS.get(nombre)
        if techo is None:
            continue
        propios = [ruta] + ([SUBAGENTE[nombre]] if nombre in SUBAGENTE else [])
        total = sum(tam(p) for p in propios)
        texto = "\n".join(leer(p) for p in propios)
        detalle = []
        for ref, modo in sorted(_refs_de(texto, proyecto).items()):
            costo = tam_indice(ref) if modo == "indice" else tam(ref)
            total += costo
            if costo > 20 * 1024:
                detalle.append("%s (%.0f KB%s)" % (ref, kb(costo), "" if modo == "completo" else ", indice"))
        tk = tokens(total)
        estado = "OK" if tk <= techo else "EXCEDE"
        if tk > techo:
            excede = True
        filas.append((nombre, total, tk, techo, estado, detalle))

    print("\n[contexto] arranque por agente sobre el proyecto '%s'" % proyecto)
    print("   (carga declarada en .github/agents/*.agent.md + su subagente, antes de leer codigo)\n")
    for nombre, total, tk, techo, estado, detalle in filas:
        print("  %-26s %7.0f KB  ~%6dk tok  techo %3dk  %s"
              % (nombre, kb(total), tk // 1000, techo // 1000, estado))
        for d in detalle:
            print("      - %s" % d)
    if excede:
        culpa_memoria = any("/definiciones/" in d or "trazabilidad" in d
                            for _, _, _, _, e, ds in filas if e == "EXCEDE" for d in ds)
        print("\n  Alguno excede su techo (instruccion 39).")
        if culpa_memoria:
            print("  Lo que mas pesa es la memoria de este proyecto, no las instructions:")
            print("    1. python scripts/archivar_memoria.py --todos            (que hay para archivar)")
            print("    2. si ya esta archivado y sigue pesando, el bloque '## Definiciones vigentes'")
            print("       quedo inflado con modulos ya entregados: depurarlo a mano deja de nuevo")
            print("       un estado vigente que se lee de una sentada.")
        else:
            print("  Pasar a carga por indice lo que mas pesa (seccion 2 de la instruccion 39).")
    return 1 if excede else 0


# ─────────────────────────────────────────────────────────────────────────────
# indice
# ─────────────────────────────────────────────────────────────────────────────
def indice(destino):
    if not destino:
        print("\n[contexto] alias disponibles:\n")
        for a, p in sorted(ALIAS.items()):
            print("  %-12s %-62s %6.0f KB" % (a, p, kb(tam(p))))
        print("\n  Tambien acepta una ruta: python scripts/contexto.py indice docs/marihogar/definiciones/6-qa.md")
        return 0

    p = ALIAS.get(destino, destino)
    if not os.path.exists(p):
        print("[contexto] no existe: %s" % p)
        return 1

    txt = leer(p)
    print("\n[contexto] %s (%.0f KB) - leer SOLO las secciones que toca el trabajo:\n" % (p, kb(tam(p))))
    if p.endswith(".yml"):
        actual = None
        for i, l in enumerate(txt.split("\n"), 1):
            m = re.match(r"^\s*- id: (\S+)", l)
            if m:
                actual = (i, m.group(1))
                continue
            m2 = re.match(r'^\s*(?:titulo|nombre): "?([^"\n]+)', l)
            if m2 and actual:
                print("  %5d  %-10s %s" % (actual[0], actual[1], m2.group(1).strip().rstrip('"')))
                actual = None
    else:
        for i, l in enumerate(txt.split("\n"), 1):
            if re.match(r"^#{1,3} ", l):
                nivel = len(l) - len(l.lstrip("#"))
                print("  %5d  %s%s" % (i, "  " * (nivel - 1), l.lstrip("# ").strip()))
    print("\n  Leer una seccion:  sed -n '<desde>,<hasta>p' %s" % p)
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# resumenes
# ─────────────────────────────────────────────────────────────────────────────
def _items_yml(p, campos):
    """Items de un YAML plano de catalogo: lista de dicts con los campos pedidos."""
    items, actual = [], None
    for l in leer(p).split("\n"):
        m = re.match(r"^\s*- id: (\S+)", l)
        if m:
            if actual:
                items.append(actual)
            actual = {"id": m.group(1).strip('"')}
            continue
        if actual is None:
            continue
        m2 = re.match(r'^\s{2,}(\w+): *"?([^"\n]*)"?\s*$', l)
        if m2 and m2.group(1) in campos and m2.group(1) not in actual:
            actual[m2.group(1)] = m2.group(2).strip().rstrip('"')
    if actual:
        items.append(actual)
    return items


def resumenes():
    hechos = []

    # QA: 1 linea por regresion catalogada (reemplaza cargar los 428 KB del yml)
    src = "docs/qa/regresiones-manuales.yml"
    items = _items_yml(src, ("modulo", "titulo", "severidad", "tipo"))
    if items:
        out = ["# Indice plano de %s - generado por scripts/contexto.py resumenes" % src,
               "# id | severidad | modulo | titulo   (el item completo se lee del yml SOLO si aplica)"]
        for it in items:
            out.append("%-10s | %-9s | %-28s | %s" % (it.get("id", "?"), it.get("severidad", "?"),
                                                      it.get("modulo", "?")[:28], it.get("titulo", "")))
        io.open("docs/qa/cat_resumen.txt", "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
        hechos.append("docs/qa/cat_resumen.txt (%d regresiones)" % len(items))

    # Patrones: 1 linea por patron reutilizable (reemplaza escanear docs/*/definiciones/)
    src = "docs/patrones/catalogo.yml"
    items = _items_yml(src, ("nombre", "categoria", "proyecto_origen"))
    if items:
        out = ["# Indice plano de %s - generado por scripts/contexto.py resumenes" % src,
               "# id | categoria | origen | nombre   (primer lookup del escaneo de reutilizacion, instruccion 39)"]
        for it in items:
            out.append("%-9s | %-16s | %-26s | %s" % (it.get("id", "?"), it.get("categoria", "?"),
                                                      it.get("proyecto_origen", "?")[:26], it.get("nombre", "")))
        io.open("docs/patrones/cat_resumen.txt", "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
        hechos.append("docs/patrones/cat_resumen.txt (%d patrones)" % len(items))

    print("\n[contexto] regenerado: %s" % ("; ".join(hechos) if hechos else "nada"))
    return 0


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "presupuesto"
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    if cmd == "presupuesto":
        return presupuesto(arg or "marihogar")
    if cmd == "indice":
        return indice(arg)
    if cmd == "resumenes":
        return resumenes()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
