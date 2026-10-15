#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
plan_olvidata.py - modelo de recurrente por frente de Olvidata Soft.

Reproduce las tablas de docs/olvidata-soft/plan.md. Cambiar los supuestos aca y
volver a correr; despues actualizar plan.md con el resultado.

Uso:
    python scripts/plan_olvidata.py
"""
META = 1173  # sueldo del Ministerio, USD/mes neto

# Recurrente neto por cliente nuevo (USD/mes), ingreso de entrada (USD) y bajas por año.
REC = {"Build": 426 / 12, "Landing": 32, "AI Agents": 105, "Chatbots": 40}
ENTRADA = {"Build": 1500, "Landing": 600, "AI Agents": 2500, "Chatbots": 900}
BAJAS = {"Build": 0.10, "Landing": 0.10, "AI Agents": 0.10, "Chatbots": 0.15}
SUBA_2027 = {"AI Agents": 1.2, "Chatbots": 1.2}  # lista 2027 = promo x 1,20

# Punto de partida: fin de 2026.
CLIENTES_2026 = {"Build": 17, "Landing": 2, "AI Agents": 1, "Chatbots": 0}
REC_2026 = {"Build": 17 * 426 / 12, "Landing": 700 / 12, "AI Agents": 150, "Chatbots": 0}

# Cierres nuevos por año, escenario base.
CIERRES = {
    2027: {"Build": 8, "Landing": 6, "AI Agents": 3, "Chatbots": 2},
    2028: {"Build": 8, "Landing": 8, "AI Agents": 5, "Chatbots": 4},
    2029: {"Build": 8, "Landing": 8, "AI Agents": 7, "Chatbots": 5},
    2030: {"Build": 8, "Landing": 8, "AI Agents": 9, "Chatbots": 6},
}
ESCENARIOS = (("base", 1.0), ("conservador", 0.5))


def proyectar(factor):
    clientes, rec = dict(CLIENTES_2026), dict(REC_2026)
    filas = []
    for anio in sorted(CIERRES):
        inicio, entrada = sum(rec.values()), 0
        for frente in clientes:
            nuevos = round(CIERRES[anio][frente] * factor)
            m = SUBA_2027.get(frente, 1)
            rec[frente] = rec[frente] * (1 - BAJAS[frente]) + nuevos * REC[frente] * m
            clientes[frente] = clientes[frente] * (1 - BAJAS[frente]) + nuevos
            entrada += nuevos * ENTRADA[frente] * m
        fin = sum(rec.values())
        filas.append((anio, sum(clientes.values()), fin, entrada + (inicio + fin) / 2 * 12, dict(rec)))
    return filas


if __name__ == "__main__":
    print("Punto de partida 2026: %d clientes, recurrente neto %.0f/mes (meta %d)"
          % (sum(CLIENTES_2026.values()), sum(REC_2026.values()), META))
    for nombre, factor in ESCENARIOS:
        print("\n== %s" % nombre)
        for anio, n, fin, bruto, por_frente in proyectar(factor):
            marca = "  <- cubre la meta" if fin >= META else ""
            detalle = ", ".join("%s %.0f" % (k, v) for k, v in por_frente.items())
            print("%d  clientes %3.0f  recurrente %5.0f/mes  bruto %7.0f  (%s)%s"
                  % (anio, n, fin, bruto, detalle, marca))
