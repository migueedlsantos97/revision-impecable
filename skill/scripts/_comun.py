"""Utilidades compartidas por medir.py, alcance.py, estado.py, presupuesto.py y promover.py (solo librería estándar)."""
import hashlib
import json
import re
import sys
import subprocess
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def git(raiz, *args, check=True):
    r = subprocess.run(["git", "-C", str(raiz), *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(args), r.stderr.strip()[:300]))
    return r.stdout


def raiz_repo(arg=None):
    if arg:
        return Path(arg).resolve()
    try:
        return Path(git(Path.cwd(), "rev-parse", "--show-toplevel").strip())
    except Exception:
        return Path.cwd()


def rev_dir(raiz):
    return Path(raiz) / ".claude" / "revision"


def _bytes_lf(ruta):
    return Path(ruta).read_bytes().replace(b"\r\n", b"\n")  # why: autocrlf cambia los bytes sin cambiar el contenido


def hash_config(cfg_path):
    """Huella de lo que define cómo se mide: proyecto.json (sin la lista de pantallas ni el nombre), medir.py y medidas.js.
    Si cambia, ninguna verificación anterior vale: se midió con otra vara."""
    h = hashlib.sha256()
    p = Path(cfg_path)
    if p.exists():
        cfg = json.loads(p.read_text(encoding="utf-8"))
        for k in ("pantallas", "nombre"):
            cfg.pop(k, None)
        h.update(json.dumps(cfg, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    for n in ("medir.py", "medidas.js"):
        h.update(_bytes_lf(AQUI / n))
    return h.hexdigest()[:16]


def glob_re(g):
    """Glob de repo (con ** y *) -> regex. 'dir/' equivale a 'dir/**'."""
    g = g.replace("\\", "/")
    if g.endswith("/"):
        g += "**"
    i, out = 0, ""
    while i < len(g):
        if g.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif g.startswith("**", i):
            out += ".*"
            i += 2
        elif g[i] == "*":
            out += "[^/]*"
            i += 1
        elif g[i] == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(g[i])
            i += 1
    return re.compile("^" + out + "$")


def coincide(ruta, globs):
    return any(glob_re(g).match(ruta.replace("\\", "/")) for g in globs)


def archivos_repo(raiz):
    """Archivos versionados o nuevos no ignorados, rutas con /."""
    return sorted(set(git(raiz, "ls-files", "-co", "--exclude-standard").splitlines()))


def hash_arbol(raiz, glob, archivos):
    rx = glob_re(glob)
    h = hashlib.sha256()
    n = 0
    for f in archivos:
        if rx.match(f) and (Path(raiz) / f).is_file():
            h.update(f.encode("utf-8"))
            h.update(hashlib.sha256(_bytes_lf(Path(raiz) / f)).digest())
            n += 1
    return h.hexdigest()[:16] if n else ""


def leer_json(ruta, defecto=None):
    try:
        return json.loads(Path(ruta).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return defecto
    except ValueError as ex:
        raise SystemExit("No puedo leer %s: %s" % (ruta, ex))


def escribir_json(ruta, datos):
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    Path(ruta).write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")


def utf8():
    """Salida en UTF-8 aunque la consola o la tubería sea cp1252 (Windows): los mensajes llevan tildes y «»."""
    for f in (sys.stdout, sys.stderr):
        try:
            f.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
