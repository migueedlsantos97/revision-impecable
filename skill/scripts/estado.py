#!/usr/bin/env python3
"""Estado verificado de cada sistema (lo que alcance.py compara contra git).

  python estado.py escribir --sistema X --sha HEAD [--parcial] [--informe RUTA] [--funciones a,b] [--tests "texto"]
  python estado.py ver

`escribir` guarda .claude/revision/estado/<sistema>.json:
  {verificado_en, fecha, archivos:{glob: sha256 del árbol}, pantallas:{"id@ancho@tema": {fallas, hash_png}},
   funciones, tests, umbrales_hash, estado: verificado|parcial|vencido}
Solo escribe "verificado" si la última medición que incluyó ese sistema (informe.json) cubrió todas sus pantallas,
no se cortó por límites, usó la misma configuración de hoy y no dejó fallas MEDIDAS (certeza "medida") de ese sistema.
Con --parcial escribe igual, con estado "parcial" (alcance.py lo vuelve a revisar). `ver` imprime la tabla.
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

from _comun import archivos_repo, escribir_json, git, hash_arbol, hash_config, leer_json, raiz_repo, rev_dir, utf8


def _ultimo_informe(rev, sistema, explicito=None):
    if explicito:
        return Path(explicito), leer_json(explicito)
    dirs = sorted((d for d in (rev / "salida").glob("*") if (d / "informe.json").exists()), key=lambda d: d.stat().st_mtime, reverse=True)
    for d in dirs:
        inf = leer_json(d / "informe.json")
        if any(m.get("sistema") == sistema for m in inf.get("pantallas_medidas", [])):
            return d / "informe.json", inf
    return None, None


def escribir(a):
    raiz = raiz_repo(a.raiz)
    rev = rev_dir(raiz)
    cfg_path = Path(a.config) if a.config else rev / "proyecto.json"
    try:
        sha = git(raiz, "rev-parse", a.sha).strip()
    except Exception as ex:
        sys.exit("No puedo resolver --sha %s: %s" % (a.sha, ex))
    ruta, inf = _ultimo_informe(rev, a.sistema, a.informe)
    if not inf:
        sys.exit("Ninguna medición en %s incluyó pantallas del sistema %s: corré medir.py antes." % (rev / "salida", a.sistema))
    medidas = [m for m in inf["pantallas_medidas"] if m.get("sistema") == a.sistema]
    problemas = []
    if not inf.get("completo", True):
        problemas.append("la medición se cortó por %s" % inf.get("limite"))
    if inf.get("config_hash") != hash_config(cfg_path):
        problemas.append("la medición se hizo con otra configuración (proyecto.json/medir.py/medidas.js cambiaron): volvé a medir")
    deps = leer_json(rev / "dependencias.json") or {}
    cfg = leer_json(cfg_path) or {}
    esperadas = set((deps.get("pantallas") or {}).get(a.sistema) or [p["id"] for p in cfg.get("pantallas", []) if p.get("sistema") == a.sistema])
    faltan = sorted(esperadas - {m["id"] for m in medidas})
    if faltan:
        problemas.append("faltan pantallas sin medir: %s" % ", ".join(faltan[:8]))
    medidas_f = [f for f in inf["fallas"] if f.get("sistema") == a.sistema and f.get("certeza") == "medida"]
    if medidas_f:
        problemas.append("%d falla(s) medida(s): %s" % (len(medidas_f), ", ".join(sorted({f["tipo"] for f in medidas_f})[:6])))
    if problemas and not a.parcial:
        print("NO se escribe el estado de %s como verificado:" % a.sistema)
        for p in problemas:
            print("  - " + p)
        print("Arreglá y volvé a medir, o usá --parcial para dejarlo anotado como parcial.")
        return 1
    globs = []
    sdef = (deps.get("sistemas") or {}).get(a.sistema) or {}
    globs = list(sdef.get("propios") or []) + list(sdef.get("consume") or [])
    arch = archivos_repo(raiz) if globs else []
    estado = {"verificado_en": sha, "fecha": datetime.now().isoformat(timespec="seconds"),
              "archivos": {g: hash_arbol(raiz, g, arch) for g in globs},
              "pantallas": {"%s@%d@%s" % (m["id"], m["ancho"], m["tema"]): {"fallas": m["fallas"], "hash_png": m["hash_png"]} for m in medidas},
              "funciones": [x for x in (a.funciones or "").split(",") if x], "tests": a.tests or "",
              "umbrales_hash": hash_config(cfg_path), "estado": "parcial" if a.parcial else "verificado"}
    if problemas:
        estado["pendiente"] = problemas
    destino = rev / "estado" / ("%s.json" % a.sistema)
    escribir_json(destino, estado)
    print("%s: %s en %s (%d pantallas) -> %s" % (a.sistema, estado["estado"], sha[:10], len(medidas), destino))
    return 0


def ver(a):
    raiz = raiz_repo(a.raiz)
    rev = rev_dir(raiz)
    cfg_path = Path(a.config) if a.config else rev / "proyecto.json"
    hoy = hash_config(cfg_path)
    deps = leer_json(rev / "dependencias.json") or {}
    vig = deps.get("vigencia_dias", 90)
    filas = [("sistema", "estado", "sha", "fecha", "pantallas", "fallas")]
    for f in sorted((rev / "estado").glob("*.json")):
        e = leer_json(f)
        est = e.get("estado", "?")
        try:
            if (datetime.now() - datetime.fromisoformat(e["fecha"])).days > vig:
                est = "vencido (vigencia)"
        except Exception:
            est = "vencido (sin fecha)"
        if e.get("umbrales_hash") != hoy:
            est = "vencido (config)"
        filas.append((f.stem, est, str(e.get("verificado_en", ""))[:10], str(e.get("fecha", ""))[:10], str(len(e.get("pantallas", {}))),
                      str(sum(p.get("fallas", 0) for p in e.get("pantallas", {}).values()))))
    for s in (deps.get("sistemas") or {}):
        if not (rev / "estado" / ("%s.json" % s)).exists():
            filas.append((s, "sin estado", "", "", "", ""))
    ancho = [max(len(r[i]) for r in filas) for i in range(6)]
    for r in filas:
        print("  ".join(c.ljust(ancho[i]) for i, c in enumerate(r)))
    return 0


def main(argv=None):
    utf8()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for n in ("escribir", "ver"):
        p = sub.add_parser(n)
        p.add_argument("--raiz")
        p.add_argument("--config")
    e = sub.choices["escribir"]
    e.add_argument("--sistema", required=True)
    e.add_argument("--sha", required=True, help="commit verificado (p. ej. HEAD)")
    e.add_argument("--parcial", action="store_true")
    e.add_argument("--informe", help="informe.json a usar (por defecto, el último que midió ese sistema)")
    e.add_argument("--funciones", help="ids de funciones del mapa que se probaron, separados por coma")
    e.add_argument("--tests", help="resultado de los tests, en una línea")
    a = ap.parse_args(argv)
    return escribir(a) if a.cmd == "escribir" else ver(a)


if __name__ == "__main__":
    sys.exit(main())
