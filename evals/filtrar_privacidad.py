"""Filtro de privacidad para candidatos a check, informes o cualquier texto que vaya a un repo publico.
Falla (codigo 1) si un archivo contiene emails, rutas de usuario (C:\\Users, /home, /Users), IPs privadas,
dominios internos o terminos de la lista negra.

Uso:
  python filtrar_privacidad.py archivo_o_carpeta [...] [--negra termino ...] [--negra-archivo no-publicar.txt]
                               [--permitir-dominio ejemplo.com ...]
Solo stdlib. Texto sin dominio propio: example.com/example.org/test/localhost/127.0.0.1 se permiten."""
import argparse, re, sys
from pathlib import Path

EXT = {".md", ".txt", ".html", ".css", ".js", ".json", ".py", ".yml", ".yaml", ".csv"}
PERMITIDOS = {"example.com", "example.org", "example.net", "localhost", "127.0.0.1", "test", "w3.org", "github.com", "claude.ai"}
PATRONES = [
    ("email", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    ("ruta de usuario Windows", re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s]+", re.I)),
    ("ruta de usuario Unix", re.compile(r"(?:^|[\s\"'(=])/(?:home|Users)/[^/\s]+")),
    ("IP privada", re.compile(r"\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b")),
    ("dominio interno", re.compile(r"\b[\w-]+(?:\.[\w-]+)*\.(?:local|internal|corp|lan|intranet)\b", re.I)),
    ("token/clave", re.compile(r"\b(?:sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{12,}|xox[bp]-[\w-]{10,})")),
    ("telefono", re.compile(r"(?<!\d)\+?\d{2,3}[\s-]?\d{2,3}[\s-]\d{3}[\s-]\d{3,4}(?!\d)")),
]
URL = re.compile(r"https?://([\w.-]+)", re.I)


def archivos(rutas):
    for r in rutas:
        p = Path(r)
        if p.is_dir():
            for f in p.rglob("*"):
                if f.is_file() and f.suffix.lower() in EXT and not {".git", "node_modules", "__pycache__"} & set(f.parts):
                    yield f
        elif p.is_file():
            yield p


def revisar(f, negra, dominios_ok):
    try:
        texto = f.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return [(0, "ilegible", str(e))]
    hallazgos = []
    for n, linea in enumerate(texto.splitlines(), 1):
        for nombre, rx in PATRONES:
            for m in rx.finditer(linea):
                hallazgos.append((n, nombre, m.group(0).strip()))
        for m in URL.finditer(linea):
            d = m.group(1).lower()
            if not any(d == o or d.endswith("." + o) for o in dominios_ok):
                hallazgos.append((n, "dominio no permitido", d))
        bajo = linea.lower()
        for t in negra:
            if t.lower() in bajo:
                hallazgos.append((n, "lista negra", t))
    return hallazgos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rutas", nargs="+")
    ap.add_argument("--negra", nargs="*", default=[], help="terminos que no pueden aparecer (cliente, proyecto, personas)")
    ap.add_argument("--negra-archivo", help="un termino por linea; este archivo NO se versiona")
    ap.add_argument("--permitir-dominio", nargs="*", default=[])
    a = ap.parse_args()
    negra = list(a.negra)
    if a.negra_archivo:
        negra += [l.strip() for l in Path(a.negra_archivo).read_text(encoding="utf-8").splitlines() if l.strip()]
    dominios_ok = PERMITIDOS | {d.lower() for d in a.permitir_dominio}
    total = 0
    for f in archivos(a.rutas):
        for n, tipo, dato in revisar(f, negra, dominios_ok):
            print(f"{f}:{n}: {tipo}: {dato}")
            total += 1
    print(f"{total} hallazgo(s)" if total else "limpio")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
