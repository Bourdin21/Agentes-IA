#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
archivar_memoria.py - mantiene los archivos de memoria bajo el techo de 150 KB.

La memoria por agente es append-only por diseño (un sprint/CR nuevo por corrida).
Sin poda, `6-qa.md` de un proyecto maduro llega a 686 KB: el agente que lo lee al
arrancar gasta ~170k tokens en historia antes de empezar a trabajar. Este script
mueve los bloques ya cerrados a `historial/`, agrupados por mes, y deja en el
archivo vigente una linea con puntero por grupo.

No reescribe texto: corta y pega bloques enteros, y verifica byte a byte que lo
movido este completo en el destino antes de tocar el archivo de origen.

Uso:
    python scripts/archivar_memoria.py                      # dry-run: que archivos pasan el techo y que se moveria
    python scripts/archivar_memoria.py <archivo>            # dry-run de uno
    python scripts/archivar_memoria.py <archivo> --aplicar  # lo hace
    python scripts/archivar_memoria.py --todos --aplicar    # todos los que pasan el techo
    python scripts/archivar_memoria.py <archivo> --techo 70 # techo distinto, en KB (poda mas agresiva
                                                            # cuando el bloque vigente acumulo modulos
                                                            # ya entregados de sprints viejos)

Respaldo: git. Correrlo con el archivo commiteado.
Ver `.github/instructions/39-presupuesto-contexto.instructions.md` seccion 6.
"""
import io, os, re, sys, glob, datetime

# la consola de Windows viene en cp1252 y los titulos tienen acentos
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)

TECHO = 150 * 1024          # bytes; instruccion 39 seccion 6
MIN_GRUPOS_VIGENTES = 1     # el grupo mas reciente siempre queda en el archivo vigente

# Titulos que son estructura del documento y nunca se archivan como bloque.
ESTRUCTURALES = ("proyecto:", "ultima actualizacion", "última actualizacion",
                 "ultima actualizacion previa", "definiciones vigentes", "version actual",
                 "versión actual", "historial de ajustes", "contexto", "pendientes",
                 "estado", "indice", "índice", "memoria", "objetivo", "alcance vigente",
                 "convenciones", "notas", "bloques archivados")

# Titulos de unidad de trabajo cerrada: SOLO estos son candidatos a archivar. El
# criterio es deliberadamente estricto: una seccion tematica ("Cobertura de criterios",
# "Contexto del negocio") es parte del estado vigente y no se archiva nunca, aunque el
# archivo este pesado. Antes que fragmentar mal un documento, el script avisa y para.
RE_TRABAJO = re.compile(
    r"^(sprint\b|cr[-_ ]?\d|cr[-_ ]?[a-z]\b|m\d+\b|modulo \d|módulo \d|etapa \d|fase \d"
    r"|auditoria\b|auditoría\b|qa\b|iteracion \d|iteración \d|ronda \d|sesion \d|sesión \d"
    r"|entrega \d|\d{4}-\d{2}-\d{2})",
    re.I)
RE_FECHA = re.compile(r"(20\d\d)-(\d\d)-(\d\d)")
# Varios proyectos identifican la unidad de trabajo por modulo en el titulo, con el numero
# adelante (`# M21 - ojos`) o como sufijo (`### Casos de uso M8`). Ahi el grupo natural del
# historial es el modulo, no el mes: agrupar por fecha partiria un modulo en dos archivos.
RE_MODULO = re.compile(r"\bM(\d{1,3})[a-z]?\b")

APLICAR = "--aplicar" in sys.argv
TODOS = "--todos" in sys.argv
if "--techo" in sys.argv:
    TECHO = int(sys.argv[sys.argv.index("--techo") + 1]) * 1024


def leer(p):
    return io.open(p, encoding="utf-8").read()


def escribir(p, txt):
    d = os.path.dirname(p)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    io.open(p, "w", encoding="utf-8", newline="\n").write(txt)


def bloques(lineas, nivel):
    """Corta las lineas en bloques por heading del nivel dado: [(titulo, desde, hasta)]."""
    marca = "#" * nivel + " "
    cortes = [i for i, l in enumerate(lineas) if l.startswith(marca)]
    out = []
    for j, i in enumerate(cortes):
        fin = cortes[j + 1] if j + 1 < len(cortes) else len(lineas)
        out.append((lineas[i][len(marca):].strip(), i, fin))
    return out


def modulo(titulo):
    """Numero de modulo del titulo (`M21`, `Casos de uso M8`), o None."""
    m = RE_MODULO.search(titulo or "")
    return int(m.group(1)) if m else None


def es_trabajo(titulo):
    t = (titulo or "").strip().lower().lstrip("*_ ")
    if not t or any(t.startswith(e) for e in ESTRUCTURALES):
        return False
    return bool(RE_TRABAJO.match(t)) or modulo(titulo) is not None


def periodo(titulo, cuerpo):
    """Clave de grupo del historial: el modulo si el titulo lo declara, si no el mes."""
    n = modulo(titulo)
    if n is not None:
        return "M%02d" % n
    m = RE_FECHA.search(titulo) or RE_FECHA.search(cuerpo[:4000])
    return "%s-%s" % (m.group(1), m.group(2)) if m else None


def _candidatos_nivel(lineas, nivel):
    """Bloques archivables cortando por ese nivel, o [] si el nivel esta mal anidado.

    Algunos archivos del repo usan `# M20` (nivel 1) para el modulo y `## ...` para sus
    secciones, todo adentro de `## Definiciones vigentes`. Cortando por nivel 2 ahi, un
    bloque se tragaria los modulos siguientes: si un candidato contiene un heading de
    nivel mas alto que el del corte, ese nivel no sirve.
    """
    total = max(1, sum(len(l) + 1 for l in lineas))
    out = []
    for titulo, desde, hasta in bloques(lineas, nivel):
        if not es_trabajo(titulo):
            continue
        cuerpo = "\n".join(lineas[desde:hasta])
        if len(cuerpo) > 0.4 * total:
            return []      # un bloque que abarca casi todo el archivo: el nivel esta mal anidado
        out.append((titulo, desde, hasta, cuerpo))
    return out


def _mas_reciente_primero(cands):
    """Ordena los bloques del mas nuevo al mas viejo.

    Los archivos del repo no coinciden en la convencion: marihogar apila los sprints
    nuevos al final, koi los pone arriba. Se decide por las fechas reales cuando estan,
    y solo se cae a la posicion cuando no hay ninguna.
    """
    # cuando la unidad de trabajo es el modulo, el mas nuevo es el de numero mas alto
    mods = [(modulo(b[0]), i, b) for i, b in enumerate(cands)]
    if len([m for m, _, _ in mods if m is not None]) >= max(2, len(cands) // 2):
        return [b for _, _, b in sorted(mods, key=lambda x: (x[0] if x[0] is not None else -1, -x[1]),
                                        reverse=True)]

    con_fecha = [(periodo(b[0], b[3]), i, b) for i, b in enumerate(cands)]
    fechados = [x for x in con_fecha if x[0]]
    if len(fechados) >= max(2, len(cands) // 2):
        # clave: (periodo, posicion) descendente -> mas nuevo primero; los sin fecha quedan al final
        return [b for _, _, b in sorted(con_fecha, key=lambda x: (x[0] or "0000-00", -x[1]), reverse=True)]
    primera, ultima = con_fecha[0][0], con_fecha[-1][0]
    if primera and ultima and primera > ultima:
        return [b for _, _, b in con_fecha]          # el archivo ya viene con lo nuevo arriba
    return [b for _, _, b in reversed(con_fecha)]    # convencion append: lo nuevo al final


def plan(ruta):
    """(nivel, grupos, aviso). grupos = [(clave, [bloques])] a mover, mas nuevo primero.

    Niveles en orden de preferencia: 2 (el normal), 1 (proyectos que numeran los modulos
    con `# M18 ...` adentro de "Definiciones vigentes") y 3 (entradas de trazabilidad,
    etapas dentro de un unico heading). Gana el primero que deje el archivo bajo el techo.
    """
    lineas = leer(ruta).split("\n")
    total = os.path.getsize(ruta)
    intentos = []
    for nivel in (2, 1, 3):
        cands = _candidatos_nivel(lineas, nivel)
        if len(cands) < 3:
            continue
        base = total - sum(len(b[3]) + 1 for b in cands)   # cabecera + vigente + secciones tematicas
        conservados, a_mover, acum = [], [], base
        for b in _mas_reciente_primero(cands):
            peso = len(b[3]) + 1
            if not conservados or acum + peso <= TECHO:
                conservados.append(b)
                acum += peso
            else:
                a_mover.append(b)

        # agrupar lo que se mueve por mes, para no crear un archivo por bloque
        grupos = {}
        for b in a_mover:
            grupos.setdefault(periodo(b[0], b[3]) or "historico", []).append(b)
        claves = (sorted((k for k in grupos if k.startswith("M") and k[1:].isdigit()), reverse=True) +
                  sorted((k for k in grupos if k[0].isdigit()), reverse=True) +
                  [k for k in grupos if k == "historico"])
        intentos.append((acum, base, nivel, [(k, grupos[k]) for k in claves]))
        if acum <= TECHO:
            return (nivel, [(k, grupos[k]) for k in claves], "")

    if not intentos:
        return (None, [], "")
    acum, base, nivel, grupos = min(intentos, key=lambda x: x[0])
    aviso = ""
    if base > TECHO:
        # archivar igual todo lo archivable (es ganancia real) y decir que el resto necesita mano
        aviso = ("PARCIAL: lo que NO es sprint/CR/modulo pesa %.0f KB por si solo, asi que archivar "
                 "no alcanza para llegar al techo — el bloque vigente necesita curaduria a mano"
                 % (base / 1024.0))
    return (nivel, grupos, aviso)


def archivar(ruta):
    tam0 = os.path.getsize(ruta)
    if tam0 <= TECHO:
        return "OK (%.0f KB)" % (tam0 / 1024.0)

    nivel, grupos, aviso = plan(ruta)
    if aviso and not grupos:
        return "NO SE PUDO (%.0f KB): %s" % (tam0 / 1024.0, aviso)
    if not grupos:
        return ("NO SE PUDO: no encontre bloques de sprint/CR/entrada archivables (%.0f KB) "
                "- revisar a mano la estructura de headings" % (tam0 / 1024.0))

    lineas = leer(ruta).split("\n")
    base = os.path.basename(ruta).replace(".md", "")
    dir_hist = os.path.join(os.path.dirname(ruta), "historial").replace("\\", "/")
    hoy = datetime.date.today().isoformat()
    movido_bytes = sum(len(b[3]) + 1 for _, bs in grupos for b in bs)

    if not APLICAR:
        detalle = ", ".join("%s (%d bloques)" % (k, len(bs)) for k, bs in grupos[:6])
        return ("DRY-RUN: %d grupo(s) de nivel %d, %d bloques, %.0f KB -> %s ; quedaria en %.0f KB. %s"
                % (len(grupos), nivel, sum(len(bs) for _, bs in grupos), movido_bytes / 1024.0,
                   dir_hist, (tam0 - movido_bytes) / 1024.0, detalle))

    # 1. escribir cada grupo en historial/ y verificar byte a byte
    punteros = []
    for clave, bs in grupos:
        destino = "%s/%s-%s.md" % (dir_hist, base, clave)
        # nunca pisar un historial ya escrito: una segunda pasada sobre el mismo archivo (por
        # ejemplo con --techo mas bajo) puede caer en la misma clave de grupo, y sobreescribir
        # ahi borraria bloques ya archivados que solo viven en este directorio.
        n = 2
        while os.path.exists(destino):
            destino = "%s/%s-%s-%d.md" % (dir_hist, base, clave, n)
            n += 1
        indice = "\n".join("- %s" % b[0] for b in bs)
        cuerpos = "\n".join(b[3].rstrip() for b in bs)
        txt = ("<!-- Archivado de %s el %s por scripts/archivar_memoria.py. Bloques cerrados: "
               "no editar aca, el estado vigente vive en el archivo de origen. -->\n\n"
               "# %s - %s (%d bloques archivados)\n\n%s\n\n---\n\n%s\n"
               % (ruta.replace("\\", "/"), hoy, base, clave, len(bs), indice, cuerpos))
        escribir(destino, txt)
        guardado = leer(destino)
        for b in bs:
            if b[3].strip() not in guardado:
                return "ABORTADO: el bloque '%s' no quedo completo en %s (no se toco el original)" % (b[0], destino)
        fechas = sorted(f.group(0) for f in (RE_FECHA.search(b[0] + b[3][:2000]) for b in bs) if f)
        rango = (" (%s a %s)" % (fechas[0], fechas[-1])) if fechas else ""
        punteros.append("- **%s** — %d bloques%s → [`%s`](%s)"
                        % (clave, len(bs), rango, os.path.basename(destino),
                           "historial/" + os.path.basename(destino)))

    # 2. sacar los bloques del archivo vigente, de atras hacia adelante
    quedan = list(lineas)
    for _, desde, hasta in sorted([(b[0], b[1], b[2]) for _, bs in grupos for b in bs],
                                  key=lambda x: -x[1]):
        del quedan[desde:hasta]
    txt = "\n".join(quedan)

    # 3. dejar los punteros bajo Historial de ajustes
    nota = ("### Bloques archivados (%s)\n\n"
            "Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB "
            "(`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.\n\n%s\n"
            % (hoy, "\n".join(punteros)))
    m = re.search(r"^## Historial de ajustes.*$", txt, re.M)
    if m:
        txt = txt[:m.end()] + "\n\n" + nota + txt[m.end():]
    else:
        txt = txt.rstrip() + "\n\n## Historial de ajustes\n\n" + nota

    txt = re.sub(r"\n{4,}", "\n\n\n", txt)
    escribir(ruta, txt)
    tam1 = os.path.getsize(ruta)
    if tam1 <= TECHO:
        cola = ""
    elif aviso:
        cola = "\n      " + aviso
    else:
        cola = "  (sigue sobre el techo: volver a correr o revisar a mano)"
    return ("LISTO: %d grupo(s) / %d bloques -> %s | %.0f KB -> %.0f KB%s"
            % (len(grupos), sum(len(bs) for _, bs in grupos), dir_hist, tam0 / 1024.0, tam1 / 1024.0, cola))


def candidatos():
    rutas = sorted(glob.glob("docs/*/definiciones/*.md") + glob.glob("docs/*/trazabilidad.md"))
    return [p for p in rutas if os.path.getsize(p) > TECHO and "historial" not in p]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        objetivos = args
    else:
        objetivos = candidatos()
        if not objetivos:
            print("\n[archivar] ningun archivo de memoria pasa el techo de %d KB." % (TECHO / 1024))
            return 0
        if APLICAR and not TODOS:
            print("\n[archivar] con --aplicar sobre varios archivos hace falta --todos (o pasar el archivo).")
            return 1
        print("\n[archivar] %d archivo(s) sobre el techo de %d KB:" % (len(objetivos), TECHO / 1024))

    print("")
    salida = 0
    for p in objetivos:
        if not os.path.exists(p):
            print("  %-58s NO EXISTE" % p)
            salida = 1
            continue
        r = archivar(p)
        print("  %s\n      %s\n" % (p.replace("\\", "/"), r))
        if r.startswith(("ABORTADO", "NO SE PUDO")):
            salida = 1
    if not APLICAR:
        print("  (dry-run: agregar --aplicar para hacerlo. El respaldo es git.)")
    return salida


if __name__ == "__main__":
    sys.exit(main())
