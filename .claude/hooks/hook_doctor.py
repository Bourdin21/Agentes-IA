#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Puente entre los hooks de Claude Code y scripts/doctor.py.

Uso (desde .claude/settings.json):
    python .claude/hooks/hook_doctor.py post-edit    # PostToolUse Edit|Write
    python .claude/hooks/hook_doctor.py session      # SessionStart
    python .claude/hooks/hook_doctor.py stop         # Stop

Contrato de salida (ver https://code.claude.com/docs/en/hooks):
  - PostToolUse / Stop: el texto plano NO se muestra, asi que se devuelve JSON
    con hookSpecificOutput.systemMessage (visible al usuario).
  - SessionStart: el stdout plano SI entra como contexto que el modelo ve.
Siempre exit 0: es un aviso, nunca bloquea el trabajo.
"""
import json, os, subprocess, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCTOR = os.path.join(RAIZ, "scripts", "doctor.py")

# Rutas donde un cambio puede romper la consistencia documental
VIGILADAS = ("docs" + os.sep, "docs/", ".github" + os.sep, ".github/",
             "CLAUDE.md", ".claude" + os.sep + "agents", ".claude/agents",
             ".claude" + os.sep + "skills", ".claude/skills")

def evento():
    return sys.argv[1] if len(sys.argv) > 1 else "post-edit"

def entrada():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}

def correr_doctor(fast=True):
    cmd = [sys.executable, DOCTOR]
    if fast:
        cmd.append("--fast")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=RAIZ)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return 0, "doctor no pudo correr: %s" % e

def mensaje(texto, ev):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": ev, "systemMessage": texto}}))

def sin_commitear():
    try:
        r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True,
                           timeout=20, cwd=RAIZ)
        return len([l for l in r.stdout.split("\n") if l.strip()])
    except Exception:
        return 0

def main():
    ev = evento()

    if ev == "post-edit":
        data = entrada()
        ruta = (data.get("tool_input") or {}).get("file_path", "") or ""
        rel = os.path.relpath(ruta, RAIZ) if ruta else ""
        if not rel or rel.startswith(".."):
            return 0
        if not any(rel.startswith(v) or v in rel for v in VIGILADAS):
            return 0
        rc, salida = correr_doctor(fast=True)
        if rc != 0:
            errs = [l.strip() for l in salida.split("\n") if l.strip().startswith("ERROR")]
            mensaje("doctor: %d inconsistencia(s) tras editar %s\n%s\n(correr `python scripts/doctor.py` para el detalle)"
                    % (len(errs), rel, "\n".join(errs[:5])), "PostToolUse")
        return 0

    if ev == "session":
        partes = []
        rc, salida = correr_doctor(fast=True)
        if rc != 0:
            errs = [l.strip() for l in salida.split("\n") if l.strip().startswith("ERROR")]
            partes.append("Consistencia documental: %d ERROR(es) pendientes. Detalle con `python scripts/doctor.py`:\n%s"
                          % (len(errs), "\n".join("  " + e for e in errs[:6])))
        n = sin_commitear()
        if n > 20:
            partes.append("Hay %d archivos sin commitear en Agentes-IA - conviene cerrar un commit por etapa antes de seguir acumulando." % n)
        if partes:
            print("[estado del repo de memoria]\n" + "\n\n".join(partes))
        return 0

    if ev == "stop":
        n = sin_commitear()
        if n > 20:
            mensaje("Quedaron %d archivos sin commitear en Agentes-IA." % n, "Stop")
        return 0

    return 0

if __name__ == "__main__":
    sys.exit(main())
