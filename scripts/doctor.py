#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
doctor.py - chequeo de consistencia de la memoria documental del estudio.

Detecta, sin IA y en segundos, las fallas que ya costaron plata o retrabajo:
un numero de precio escrito en 2 lugares que se desincronizan, un estado de
proyecto declarado dos veces, un ID de regla duplicado, un cierre real que
quedo en la prosa y no en el dataset.

Uso:
    python scripts/doctor.py            # reporte completo
    python scripts/doctor.py --fast     # solo chequeos baratos (para hooks)
    python scripts/doctor.py --quiet    # no imprime nada si todo esta OK

Salida: 0 = sin errores (puede haber avisos) | 1 = hay errores.
Origen: auditoria documental 2026-09-15 (5 hallazgos, 4 de ellos de precio).
"""
import io, os, re, sys, glob

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)

FAST = "--fast" in sys.argv
QUIET = "--quiet" in sys.argv

errores, avisos = [], []

def err(msg): errores.append(msg)
def avi(msg): avisos.append(msg)

def leer(p):
    try:
        return io.open(p, encoding="utf-8").read()
    except Exception:
        return ""

def lineas(p):
    return leer(p).split("\n")

def donde(p, texto):
    """Devuelve 'archivo:linea' de la primera aparicion de texto."""
    for i, l in enumerate(lineas(p), 1):
        if texto in l:
            return "%s:%d" % (p, i)
    return p

def _archivos():
    # os.walk y NO glob: glob de Python no matchea carpetas que empiezan con punto,
    # asi que .github/ y .claude/ (justo donde viven las reglas) quedaban sin escanear.
    salida = []
    for raiz, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "memorias", "__pycache__")]
        for f in files:
            if f.endswith((".md", ".yml")):
                salida.append(os.path.relpath(os.path.join(raiz, f), "."))
    return salida

MD_YML = _archivos()

# ─────────────────────────────────────────────────────────────────────────────
# 1. Precio: una sola fuente. El factor de Build es 4.0 (M x $10.50) desde
#    2026-09-08; Merge / post-entrega / Extras siguen en 2.5 (M x $16.80).
# ─────────────────────────────────────────────────────────────────────────────
CTX_MERGE = ("merge", "extras", "post-entrega", "postentrega", "anterior", "antes",
             "historic", "2.5", "fork", "modulo nuevo", "ya no aplica", "reemplaza")

def chequear_factor():
    ds = "docs/calibracion/dataset.yml"
    d = leer(ds)
    if "factor_eficiencia_ia_build: 4.0" not in d:
        err("%s: falta 'factor_eficiencia_ia_build: 4.0' - el dataset es la fuente de numeros y quedo con el factor viejo" % ds)
    if "M x 10.50" not in d:
        err("%s: la formula de Build (M x 10.50) no aparece" % ds)

    for p in MD_YML:
        if p.startswith("docs" + os.sep) and "calibracion" not in p:
            continue  # las memorias de proyecto citan el precio que se uso ese dia: es historico
        ls = lineas(p)
        for i, l in enumerate(ls, 1):
            if "16.80" in l or "16,80" in l:
                # El contexto que aclara "esto es Merge" o "esto es la formula anterior"
                # suele estar en la linea de arriba, no en la misma.
                ctx = " ".join(ls[max(0, i - 3):i + 2]).lower()
                if not any(c in ctx for c in CTX_MERGE):
                    err("%s:%d: cita M x $16.80 sin aclarar que es Merge/Extras (Build es M x $10.50 desde 2026-09-08)" % (p, i))
            if re.search(r"tasa vigente \(USD 30", l):
                err("%s:%d: usa USD 30/h como tarifa - es el PISO de negociacion, la tasa es USD 35/h" % (p, i))

# ─────────────────────────────────────────────────────────────────────────────
# 2. Tokens IA: se distribuye dentro del precio de cada modulo (x1.25).
#    Nunca como linea separada al cliente (regla invertida 2026-08-20).
# ─────────────────────────────────────────────────────────────────────────────
def chequear_tokens_ia():
    for p in MD_YML:
        if p.startswith("docs" + os.sep) and "templates" not in p:
            continue
        txt = leer(p)
        for m in re.finditer(r"[Tt]okens IA[^.\n]{0,200}", txt):
            # Ventana amplia: la negacion ("nunca se muestra", "va distribuido") suele estar
            # antes o despues de la mencion, no dentro de ella.
            frag = txt[max(0, m.start() - 250):m.end() + 250]
            low = frag.lower()
            if ("linea separada" in low or "linea individual" in low or "explicito" in low) \
               and "nunca" not in low and "no se muestra" not in low and "distribu" not in low:
                n = txt[:m.start()].count("\n") + 1
                err("%s:%d: dice que Tokens IA va como linea separada/explicita al cliente - la regla vigente es distribuido x1.25" % (p, n))

# ─────────────────────────────────────────────────────────────────────────────
# 3. Estado de proyecto: fuente unica docs/indice.md.
# ─────────────────────────────────────────────────────────────────────────────
def chequear_estado_proyectos():
    sospechosos = ["CLAUDE.md", ".github/copilot-instructions.md", ".claude/README.md",
                   ".github/agents", ".claude/agents"]
    archivos = []
    for s in sospechosos:
        if os.path.isdir(s):
            archivos += glob.glob(os.path.join(s, "*.md"))
        elif os.path.isfile(s):
            archivos.append(s)
    for p in archivos:
        for i, l in enumerate(lineas(p), 1):
            # fila de tabla con nombre de proyecto + estado tipico
            if l.startswith("|") and re.search(r"\|\s*(activo|cerrado|abierto|QA pendiente|en produccion)\s*\|", l, re.I):
                err("%s:%d: tabla con estado de proyecto fuera de docs/indice.md (fuente unica)" % (p, i))

# ─────────────────────────────────────────────────────────────────────────────
# 4. IDs de reglas: sin duplicados entre headings, y los citados deben existir.
# ─────────────────────────────────────────────────────────────────────────────
RE_ID = re.compile(r"\b([A-Z]{2,4}-(?:B?\d{2,3}))\b")
# Frases que convierten un ID en referencia cruzada, no en titulo propio
CRUCE = ("misma familia", "variante nueva", "ver tambien", "familia que", "mismo patron que")

def ids_del_titulo(linea):
    """IDs que ese heading TITULA (lo que sigue a una frase de cruce no cuenta)."""
    low = linea.lower()
    corte = len(linea)
    for frase in CRUCE:
        i = low.find(frase)
        if i != -1:
            corte = min(corte, i)
    return set(RE_ID.findall(linea[:corte]))

def chequear_ids_reglas():
    f32 = ".github/instructions/32-estandares-qa-implementador.instructions.md"
    vistos = {}
    for i, l in enumerate(lineas(f32), 1):
        if not l.startswith("## "):
            continue
        ids = ids_del_titulo(l)
        if not ids and "Mantenimiento de este catalogo" not in l:
            avi("%s:%d: seccion sin ID citable - QA ejecuta por ID: %s" % (f32, i, l[3:60].strip()))
        for _id in ids:
            if _id in vistos:
                err("%s:%d: el ID %s ya titula otra seccion (linea %d) - un ID, una regla" % (f32, i, _id, vistos[_id]))
            else:
                vistos[_id] = i

    yml = leer("docs/qa/regresiones-manuales.yml")
    # Solo los IDs DECLARADOS como item del catalogo: el yml cita en prosa muchos
    # identificadores que no son reglas (CR-50 = pedido de cambio, por ejemplo).
    declarados = set(re.findall(r"^\s*- id: ([A-Z]{2,4}-B?\d{2,3})", yml, re.M))
    conocidos = declarados | set(vistos)
    # Solo prefijos que son catalogos de reglas: un CA-01 (criterio de aceptacion)
    # o un HU-03 (historia de usuario) no son reglas y no se controlan aca.
    prefijos = set(x.split("-")[0] for x in conocidos)
    huerfanos = {}
    for p in glob.glob("docs/*/definiciones/6-qa.md"):
        for i, l in enumerate(lineas(p), 1):
            for _id in RE_ID.findall(l):
                if _id.split("-")[0] in prefijos and _id not in conocidos:
                    huerfanos.setdefault(_id, "%s:%d" % (p, i))
    if huerfanos:
        avi("IDs de regla citados en memorias de QA que no existen en ningun catalogo: %s"
            % ", ".join("%s (%s)" % (k, v) for k, v in sorted(huerfanos.items())[:8]))

def chequear_catalogo_patrones():
    p = "docs/patrones/catalogo.yml"
    ids = re.findall(r"^  - id: (PAT-\d+)", leer(p), re.M)
    nums = [int(x.split("-")[1]) for x in ids]
    if nums != sorted(nums):
        avi("%s: los PAT no estan en orden ascendente (revisar el que quedo fuera de lugar)" % p)
    faltan = [n for n in range(1, max(nums) + 1) if n not in nums]
    txt = leer(p)
    sin_explicar = [n for n in faltan if txt.count("PAT-%03d" % n) == 0]
    if sin_explicar:
        avi("%s: huecos de ID sin explicar: %s (dejar escrito en el archivo si se retiraron)" %
            (p, ", ".join("PAT-%03d" % n for n in sin_explicar)))
    dup = set(x for x in ids if ids.count(x) > 1)
    if dup:
        err("%s: IDs duplicados: %s" % (p, ", ".join(sorted(dup))))
    pend = leer(p).count("pendiente_verificar: true")
    if pend:
        avi("%s: %d patrones con 'pendiente_verificar: true' sin confirmar" % (p, pend))

# ─────────────────────────────────────────────────────────────────────────────
# 5. Cierres reales: si la memoria del presupuestador declara un cierre real,
#    tiene que estar en dataset.yml (la regla lo exige y ya se incumplio).
# ─────────────────────────────────────────────────────────────────────────────
def chequear_cierres():
    """Proyectos con cierre real MEDIDO que no estan en el dataset.

    No alcanza con que el archivo diga "cierre real": casi todas las propuestas citan
    el cierre de OTRO proyecto como ancla. Se busca la seccion de cierre propia y se
    exige que tenga horas adentro y que no sea el placeholder del template.
    """
    ds = leer("docs/calibracion/dataset.yml")
    bloque = ds.split("cierres_reales:")[-1].split("# Rangos de referencia")[0]
    cargados = " ".join(re.findall(r'^\s*- proyecto: "?([^"\n]+)', bloque, re.M)).lower()

    VACIA = ("si disponible", "pendiente", "no disponible", "no aplica", "sin cierre",
             "todavia no", "<", "n/a")
    faltan = []
    for ruta in sorted(glob.glob("docs/*/definiciones/4-presupuestador.md")):
        proyecto = ruta.split(os.sep)[1]
        ls = lineas(ruta)
        medido = False
        for i, l in enumerate(ls):
            if not l.startswith("#"):
                continue
            titulo = l.lower()
            if "cierre" not in titulo or "numerico" in titulo or "dos pasos" in titulo:
                continue
            if not re.search(r"cierre.*(estimado vs\.? real|real|calibracion)", titulo):
                continue
            nivel = len(l) - len(l.lstrip("#"))
            cuerpo = []
            for l2 in ls[i + 1:]:
                if l2.startswith("#") and (len(l2) - len(l2.lstrip("#"))) <= nivel:
                    break
                cuerpo.append(l2)
            texto = " ".join(cuerpo).lower()
            if any(v in texto for v in VACIA):
                continue
            if re.search(r"\d[\d.,]*\s*(h\b|hs\b|horas)", texto):
                medido = True
                break
        if medido and proyecto.lower() not in cargados:
            faltan.append(proyecto)
    if faltan:
        avi("%d proyecto(s) con cierre real medido y sin entrada en cierres_reales de dataset.yml: %s"
            % (len(faltan), ", ".join(faltan)))

# ─────────────────────────────────────────────────────────────────────────────
# 6. Higiene de archivos
# ─────────────────────────────────────────────────────────────────────────────
def chequear_archivos():
    grandes = sorted(((os.path.getsize(p) / 1024.0, p) for p in MD_YML
                      if os.path.getsize(p) > 300 * 1024 and "historial" not in p), reverse=True)
    if grandes:
        top = ", ".join("%s (%.0f KB)" % (p, kb) for kb, p in grandes[:4])
        avi("%d archivo(s) de mas de 300 KB - archivar lo viejo o partir por tema. Los mayores: %s"
            % (len(grandes), top))
    todo = "\n".join(leer(p) for p in MD_YML)
    sueltos = [p for p in sorted(glob.glob("docs/*.md"))
               if os.path.basename(p) not in ("indice.md", "README.md", "manual-de-uso.md")
               and todo.count(os.path.basename(p)) <= 1]
    if sueltos:
        avi("%d archivo(s) sueltos en docs/ sin referencias cruzadas: %s"
            % (len(sueltos), ", ".join(sueltos)))

# ─────────────────────────────────────────────────────────────────────────────
# 7. Presupuesto de contexto (instruccion 39). Un agente que arranca con media
#    ventana gastada en historia razona peor: el techo de los archivos de memoria
#    es lo que mantiene ese arranque acotado sprint tras sprint.
# ─────────────────────────────────────────────────────────────────────────────
TECHO_MEMORIA = 150 * 1024      # techo objetivo por archivo de memoria
TECHO_MEMORIA_ERR = 250 * 1024  # a partir de aca ya degrada el arranque de los agentes

def chequear_techo_memoria():
    memorias = [p for p in sorted(glob.glob("docs/*/definiciones/*.md") + glob.glob("docs/*/trazabilidad.md"))
                if "historial" not in p]
    pasados = sorted(((os.path.getsize(p), p) for p in memorias
                      if os.path.getsize(p) > TECHO_MEMORIA), reverse=True)
    graves = [(t, p) for t, p in pasados if t > TECHO_MEMORIA_ERR]
    if graves:
        err("%d archivo(s) de memoria muy por encima del techo de %d KB (instruccion 39): %s. "
            "Correr: python scripts/archivar_memoria.py --todos --aplicar"
            % (len(graves), TECHO_MEMORIA / 1024,
               ", ".join("%s (%.0f KB)" % (p, t / 1024.0) for t, p in graves[:4])))
    leves = [(t, p) for t, p in pasados if t <= TECHO_MEMORIA_ERR]
    if leves:
        avi("%d archivo(s) de memoria apenas sobre el techo de %d KB: %s. Archivar al cerrar la etapa "
            "(python scripts/archivar_memoria.py <archivo> --aplicar)"
            % (len(leves), TECHO_MEMORIA / 1024,
               ", ".join("%s (%.0f KB)" % (p, t / 1024.0) for t, p in leves[:4])))

def chequear_resumenes_al_dia():
    """Los cat_resumen.txt son el indice por el que entran los agentes: si quedan viejos,
    el agente decide sobre un catalogo desactualizado (o vuelve a cargar el YAML entero)."""
    for fuente, resumen, marca in (("docs/qa/regresiones-manuales.yml", "docs/qa/cat_resumen.txt", "- id:"),
                                   ("docs/patrones/catalogo.yml", "docs/patrones/cat_resumen.txt", "- id:")):
        if not os.path.exists(resumen):
            err("falta %s (indice plano de %s, instruccion 39). Correr: python scripts/contexto.py resumenes"
                % (resumen, fuente))
            continue
        en_fuente = leer(fuente).count(marca)
        en_resumen = len([l for l in lineas(resumen) if l.strip() and not l.startswith("#")])
        if en_fuente != en_resumen:
            err("%s tiene %d items y %s %d: el indice quedo viejo. Correr: python scripts/contexto.py resumenes"
                % (fuente, en_fuente, resumen, en_resumen))

def chequear_instrucciones_listadas():
    claude = leer("CLAUDE.md")
    for p in sorted(glob.glob(".github/instructions/*.instructions.md")):
        nombre = os.path.basename(p).replace(".instructions.md", "")
        if nombre not in claude:
            err("CLAUDE.md: no lista la instruccion %s (existe en .github/instructions/)" % nombre)

def chequear_trazabilidad():
    for p in glob.glob("docs/*/trazabilidad.md"):
        txt = leer(p)
        if not txt.strip():
            continue
        if "### " not in txt:
            avi("%s: sin entradas '### <fecha> - <agente>' (formato canonico del template)" % p)
        if re.search(r"^\| *Fecha *\|", txt, re.M):
            avi("%s: usa formato de tabla en vez del canonico" % p)
        if txt.startswith("﻿"):
            err("%s: tiene BOM UTF-8 al inicio" % p)

# ─────────────────────────────────────────────────────────────────────────────
def main():
    chequear_factor()
    chequear_tokens_ia()
    chequear_estado_proyectos()
    chequear_ids_reglas()
    chequear_techo_memoria()
    if not FAST:
        chequear_catalogo_patrones()
        chequear_cierres()
        chequear_archivos()
        chequear_resumenes_al_dia()
        chequear_instrucciones_listadas()
        chequear_trazabilidad()

    if QUIET and not errores and not avisos:
        return 0

    if errores:
        print("\n[doctor] %d ERROR(es) de consistencia:" % len(errores))
        for e in errores:
            print("  ERROR  " + e)
    if avisos and not QUIET:
        print("\n[doctor] %d aviso(s):" % len(avisos))
        for a in avisos:
            print("  aviso  " + a)
    if not errores and not avisos:
        print("[doctor] OK - sin inconsistencias detectadas.")
    elif not errores:
        print("\n[doctor] sin errores (solo avisos).")
    return 1 if errores else 0

if __name__ == "__main__":
    sys.exit(main())
