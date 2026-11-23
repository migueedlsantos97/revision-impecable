#!/usr/bin/env python3
"""Presupuesto y punto de control de una corrida larga (para dejarla sola o retomarla tras un corte).

  python presupuesto.py iniciar   [--salida DIR]
  python presupuesto.py anotar    [--tokens N] [--minutos N] [--fase X] [--vuelta N] [--medidos N] [--abiertos id,id]
                                  [--commit SHA] [--ok] [--proximo "texto"] [--estado running|paused|done|aborted]
  python presupuesto.py decidir   -> imprime seguir | degradar | pivotar | parar (y el motivo)
  python presupuesto.py reanudar  [--json] -> dice por dónde seguir

El punto de control vive en .claude/revision/salida/<fecha>/checkpoint.json (la carpeta más reciente que lo tenga, o --salida):
  {fase, vuelta, abiertos:[ids], commits:[sha], ultimo_medir_ok, proximo_paso, tokens, minutos, estado, medidos_por_vuelta, pivotes, ...}
`--tokens` y `--minutos` de `anotar` SUMAN lo gastado desde la última anotación. El tope sale de "presupuesto" del adaptador
({tokens, minutos, vueltas}); `vueltas` también puede ir arriba en el adaptador (por defecto 5).
Reglas de `decidir` (exit 0 salvo parar = 10):
  - queda < 10 % de algún tope, o se pasó de vueltas, o estancamiento por segunda vez -> parar
  - dos vueltas seguidas sin que baje la cantidad de hallazgos medidos (--medidos) -> pivotar (una sola vez), después parar
  - queda < 25 % de algún tope -> degradar (solo lo concreto: sin revisores extra, anchos --rapido)
  - si no -> seguir
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

from _comun import escribir_json, leer_json, raiz_repo, rev_dir, utf8

ESTADOS = ("running", "paused", "done", "aborted")


def _carpeta(rev, explicita, crear=False):
    if explicita:
        return Path(explicita)
    base = rev / "salida"
    if crear:
        return base / datetime.now().strftime("%Y%m%d-%H%M%S")
    cands = sorted((d for d in base.glob("*") if (d / "checkpoint.json").exists()), key=lambda d: d.name, reverse=True)
    if not cands:
        sys.exit("No hay checkpoint.json en %s: empezá con `presupuesto.py iniciar`." % base)
    return cands[0]


def _tope(cfg):
    p = cfg.get("presupuesto") or {}
    return {"tokens": p.get("tokens"), "minutos": p.get("minutos"), "vueltas": p.get("vueltas") or cfg.get("vueltas") or 5}


def estancado(cp):
    """True si, desde el último pivote, dos vueltas seguidas no bajaron los hallazgos medidos."""
    serie = sorted((int(v), m) for v, m in cp.get("medidos_por_vuelta", {}).items() if int(v) >= cp.get("pivote_en", 0))
    vals = [m for _, m in serie]
    return len(vals) >= 3 and vals[-1] >= vals[-2] >= vals[-3]


def decidir(cp, tope):
    if cp["estado"] in ("done", "aborted"):
        return "parar", "la corrida ya está en estado %s" % cp["estado"], None
    restos = []
    if tope["tokens"]:
        restos.append(("tokens", 1 - cp["tokens"] / tope["tokens"]))
    if tope["minutos"]:
        restos.append(("minutos", 1 - cp["minutos"] / tope["minutos"]))
    if tope["vueltas"]:
        restos.append(("vueltas", 1 - (cp["vuelta"] - 1) / tope["vueltas"]))
    if cp["vuelta"] > tope["vueltas"]:
        return "parar", "se pasó del tope de %d vueltas" % tope["vueltas"], "paused"
    peor = min(restos, key=lambda r: r[1]) if restos else None
    if peor and peor[1] < 0.10:
        return "parar", "queda %.0f %% de %s (menos de 10 %%)" % (max(peor[1], 0) * 100, peor[0]), "paused"
    if estancado(cp):
        if cp.get("pivotes", 0) >= 1:
            return "parar", "estancado otra vez después de pivotar: dos vueltas sin bajar los hallazgos medidos", "aborted"
        return "pivotar", "dos vueltas seguidas sin bajar los hallazgos medidos: cambiá el enfoque (otra causa raíz, otro componente)", None
    if peor and peor[1] < 0.25:
        return "degradar", "queda %.0f %% de %s (menos de 25 %%)" % (peor[1] * 100, peor[0]), None
    return "seguir", "queda %s" % (", ".join("%.0f %% de %s" % (r[1] * 100, r[0]) for r in restos) or "sin topes configurados"), None


def main(argv=None):
    utf8()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raiz")
    ap.add_argument("--config")
    ap.add_argument("--salida", help="carpeta de la corrida (por defecto la más reciente con checkpoint.json)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("iniciar")
    an = sub.add_parser("anotar")
    an.add_argument("--tokens", type=float, default=0)
    an.add_argument("--minutos", type=float, default=0)
    an.add_argument("--fase")
    an.add_argument("--vuelta", type=int)
    an.add_argument("--medidos", type=int, help="hallazgos medidos que quedan al cerrar la vuelta (para detectar estancamiento)")
    an.add_argument("--abiertos", help="ids de hallazgos abiertos, separados por coma")
    an.add_argument("--commit", action="append")
    an.add_argument("--ok", action="store_true", help="el último medir.py corrió bien (sin romperse)")
    an.add_argument("--proximo")
    an.add_argument("--estado", choices=ESTADOS)
    sub.add_parser("decidir")
    re_ = sub.add_parser("reanudar")
    re_.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    raiz = raiz_repo(a.raiz)
    rev = rev_dir(raiz)
    cfg = leer_json(Path(a.config) if a.config else rev / "proyecto.json", {}) or {}
    tope = _tope(cfg)
    carpeta = _carpeta(rev, a.salida, crear=a.cmd == "iniciar")
    ruta = carpeta / "checkpoint.json"

    if a.cmd == "iniciar":
        if ruta.exists():
            sys.exit("Ya hay un checkpoint en %s; usá `reanudar` o pasá otra --salida." % carpeta)
        cp = {"fase": "medir", "vuelta": 1, "abiertos": [], "commits": [], "ultimo_medir_ok": None, "proximo_paso": "medir todas las pantallas",
              "tokens": 0, "minutos": 0, "estado": "running", "medidos_por_vuelta": {}, "pivotes": 0, "pivote_en": 0,
              "inicio": datetime.now().isoformat(timespec="seconds"), "tope": tope}
        escribir_json(ruta, cp)
        print("checkpoint creado: %s (tope: %s)" % (ruta, tope))
        return 0

    cp = leer_json(ruta)
    if cp is None:
        sys.exit("No existe %s" % ruta)
    if a.cmd == "anotar":
        cp["tokens"] += a.tokens
        cp["minutos"] += a.minutos
        for k, v in (("fase", a.fase), ("vuelta", a.vuelta), ("proximo_paso", a.proximo), ("estado", a.estado)):
            if v is not None:
                cp[k] = v
        if a.abiertos is not None:
            cp["abiertos"] = [x for x in a.abiertos.split(",") if x]
        cp["commits"] += a.commit or []
        if a.ok:
            cp["ultimo_medir_ok"] = datetime.now().isoformat(timespec="seconds")
        if a.medidos is not None:
            cp["medidos_por_vuelta"][str(cp["vuelta"])] = a.medidos
        cp["tope"] = tope
        escribir_json(ruta, cp)
        print("anotado: fase=%s vuelta=%s tokens=%g minutos=%g estado=%s" % (cp["fase"], cp["vuelta"], cp["tokens"], cp["minutos"], cp["estado"]))
        return 0
    if a.cmd == "decidir":
        d, motivo, nuevo_estado = decidir(cp, tope)
        if d == "pivotar":
            cp["pivotes"] = cp.get("pivotes", 0) + 1
            cp["pivote_en"] = cp["vuelta"]  # why: la cuenta de estancamiento arranca de nuevo desde esta vuelta
        if nuevo_estado:
            cp["estado"] = nuevo_estado
        escribir_json(ruta, cp)
        print(d)
        print(motivo)
        return 10 if d == "parar" else 0
    # reanudar
    ya_corria = cp["estado"] == "running"
    if cp["estado"] == "done":
        print("Nada que reanudar: la corrida %s terminó." % carpeta.name)
        return 0
    if cp["estado"] == "aborted":
        print("La corrida %s se abortó por estancamiento: revisá el enfoque antes de seguir." % carpeta.name)
    cp["estado"] = "running"
    escribir_json(ruta, cp)
    if a.json:
        import json
        print(json.dumps(cp, ensure_ascii=False, indent=1))
        return 0
    print("Corrida %s%s" % (carpeta.name, " (quedó en running: la sesión anterior se cortó sin cerrar)" if ya_corria else ""))
    print("fase: %s | vuelta: %s | gastado: %g tokens, %g min" % (cp["fase"], cp["vuelta"], cp["tokens"], cp["minutos"]))
    print("abiertos (%d): %s" % (len(cp["abiertos"]), ", ".join(cp["abiertos"][:20]) or "-"))
    print("commits: %s" % (", ".join(c[:10] for c in cp["commits"]) or "-"))
    print("último medir ok: %s" % (cp["ultimo_medir_ok"] or "nunca"))
    print("SEGUÍ POR: %s" % cp["proximo_paso"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
