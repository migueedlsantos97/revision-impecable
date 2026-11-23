#!/usr/bin/env python3
"""Qué hay que volver a mirar: cruza el estado verificado de cada sistema con lo que cambió en git.

  python alcance.py [--raiz DIR] [--config .claude/revision/proyecto.json] [--salida .claude/revision/alcance.json]

Lee .claude/revision/dependencias.json:
  {"sistemas": {id: {"propios": [globs], "consume": [globs]}},
   "compartido": {glob: {"afecta": "*" | [ids]}},
   "pantallas": {sistema: [ids]},  "vigencia_dias": 90}
y .claude/revision/estado/<sistema>.json (lo escribe estado.py). Un sistema VENCE (se revisa completo) si:
  - no tiene estado, o su estado es parcial/vencido;
  - cambió el hash de proyecto.json (sin pantallas), medir.py o medidas.js desde que se verificó (vencen todos);
  - pasaron más de vigencia_dias desde la verificación;
  - `git diff <verificado_en>` (commits + árbol de trabajo + archivos nuevos) toca un archivo suyo (propios),
    uno que consume, o un archivo compartido cuyo "afecta" lo incluye ("*" = todos).
Lo demás queda vigente. Escribe alcance.json: {revisar, vigentes, motivo, sondas, sistemas_revisar}; las sondas son
UNA pantalla de cada sistema vigente (para detectar si un sistema "verificado" ya divergió del resto).
Se usa con: python medir.py --alcance alcance.json
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

from _comun import coincide, escribir_json, git, hash_config, leer_json, raiz_repo, rev_dir, utf8


def calcular(raiz, cfg_path, ahora=None):
    rev = rev_dir(raiz)
    deps = leer_json(rev / "dependencias.json")
    if not deps or not deps.get("sistemas"):
        sys.exit("Falta %s con {\"sistemas\": {...}} (formato en el encabezado de alcance.py)." % (rev / "dependencias.json"))
    compartido, pantallas, vigencia = deps.get("compartido") or {}, deps.get("pantallas") or {}, deps.get("vigencia_dias", 90)
    hash_actual = hash_config(cfg_path)
    ahora = ahora or datetime.now()
    nuevos = set(git(raiz, "ls-files", "-o", "--exclude-standard", check=False).splitlines())
    motivo, vigentes, revisar_sis = {}, [], []
    for sid, sdef in deps["sistemas"].items():
        est = leer_json(rev / "estado" / ("%s.json" % sid))
        razones = []
        if est is None:
            razones.append("sin estado")
        else:
            if est.get("umbrales_hash") != hash_actual:
                razones.append("cambió proyecto.json/medir.py/medidas.js desde la verificación")
            if est.get("estado") != "verificado":
                razones.append("estado %s" % est.get("estado"))
            try:
                dias = (ahora - datetime.fromisoformat(est["fecha"])).days
                if dias > vigencia:
                    razones.append("verificado hace %d días (vigencia %d)" % (dias, vigencia))
            except Exception:
                razones.append("estado sin fecha válida")
            try:
                tocados = set(git(raiz, "diff", "--name-only", est["verificado_en"]).splitlines()) | nuevos
            except Exception:
                tocados = set()
                razones.append("el commit verificado_en (%s) no existe en este repo" % str(est.get("verificado_en"))[:10])
            for f in sorted(tocados):
                if coincide(f, sdef.get("propios") or []):
                    razones.append("propio: " + f)
                elif coincide(f, sdef.get("consume") or []):
                    razones.append("consume: " + f)
                else:
                    for g, d in compartido.items():
                        afecta = (d or {}).get("afecta", "*")
                        if coincide(f, [g]) and (afecta == "*" or sid in afecta):
                            razones.append("compartido: " + f)
                            break
        if razones:
            motivo[sid] = razones
            revisar_sis.append(sid)
        else:
            vigentes.append({"sistema": sid, "sha": est["verificado_en"]})
    revisar = [p for sid in revisar_sis for p in pantallas.get(sid, [])]
    sondas = [pantallas[v["sistema"]][0] for v in vigentes if pantallas.get(v["sistema"])]
    sin_pantallas = [s for s in revisar_sis + [v["sistema"] for v in vigentes] if not pantallas.get(s)]
    if sin_pantallas:
        print("aviso: dependencias.json no lista pantallas de: %s" % ", ".join(sin_pantallas), file=sys.stderr)
    return {"revisar": list(dict.fromkeys(revisar)), "vigentes": vigentes, "motivo": motivo, "sondas": sondas, "sistemas_revisar": revisar_sis}


def main(argv=None):
    utf8()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raiz")
    ap.add_argument("--config")
    ap.add_argument("--salida")
    a = ap.parse_args(argv)
    raiz = raiz_repo(a.raiz)
    cfg = Path(a.config) if a.config else rev_dir(raiz) / "proyecto.json"
    res = calcular(raiz, cfg)
    salida = Path(a.salida) if a.salida else rev_dir(raiz) / "alcance.json"
    escribir_json(salida, res)
    print("revisar %d sistema(s) (%d pantallas), %d vigente(s), %d sonda(s) -> %s" % (len(res["sistemas_revisar"]), len(res["revisar"]), len(res["vigentes"]), len(res["sondas"]), salida))
    for sid, razones in res["motivo"].items():
        print("  %s: %s" % (sid, "; ".join(razones[:4]) + (" (+%d)" % (len(razones) - 4) if len(razones) > 4 else "")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
