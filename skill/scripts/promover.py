#!/usr/bin/env python3
"""Valida que un aprendizaje de un proyecto se pueda subir como regla general sin filtrar nada del proyecto.

  python promover.py .claude/revision/candidatos/<id>.md [--lista-negra ARCHIVO] [--nombre X ...] [--permitir-cifra N ...]

El candidato es un .md con frontmatter y un caso mínimo:
  ---
  id: foco-en-contenedor            (minúsculas, números y guiones)
  regla_1_linea: una línea, hasta 200 caracteres
  causa_tecnica: por qué pasa, en términos del navegador/CSS/HTML, sin nombrar el proyecto
  proyectos_que_lo_vieron: 3        (cantidad de proyectos distintos; mejor un número que nombres)
  ---
  ## Caso mínimo
  ```html
  ...menos de 30 líneas...
  ```
Falla (exit 1) si falta algo del contrato, si el caso mínimo tiene 30 líneas o más, o si el texto filtra: nombres de la lista
negra (archivo con uno por línea, # comentarios) o pasados con --nombre, emails, rutas de usuario o de red, URLs (salvo
localhost/127.0.0.1/example.com) y cifras de más de 3 dígitos (--permitir-cifra deja pasar una, p. ej. 1366 de un viewport).
Si todo pasa, imprime el borrador de PR con los archivos a tocar.
"""
import argparse
import re
import sys
from pathlib import Path

from _comun import utf8

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
RUTA = re.compile(r"[A-Za-z]:[\\/]+(?:Users|Documents and Settings)[\\/]|/Users/\w|/home/\w|\\\\[\w.$-]+\\|[A-Za-z]:\\[\w .-]+\\")
URL = re.compile(r"https?://([^\s/:)>\]\"']+)[^\s)>\]\"']*")
URL_OK = re.compile(r"^(localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\]|(?:[\w-]+\.)?example\.(?:com|org|net))$", re.I)
CIFRA = re.compile(r"(?<![\w.])(\d{4,}|\d{1,3}(?:[.,]\d{3})+)(?![\w])")
REQUERIDOS = ("id", "regla_1_linea", "causa_tecnica", "proyectos_que_lo_vieron")


def frontmatter(texto):
    m = re.match(r"\A﻿?---\s*\n(.*?)\n---\s*\n?(.*)\Z", texto, re.S)
    if not m:
        return None, texto
    datos, clave = {}, None
    for linea in m.group(1).splitlines():
        kv = re.match(r"^([A-Za-z_][\w]*)\s*:\s*(.*)$", linea)
        if kv:
            clave = kv.group(1)
            datos[clave] = kv.group(2).strip().strip("\"'")
        elif clave and linea.strip().startswith("-"):
            datos[clave] = (datos[clave] + ", " if datos[clave] else "") + linea.strip()[1:].strip()
    return datos, m.group(2)


def caso_minimo(cuerpo):
    m = re.search(r"^#{1,6}\s*Caso\s+m[ií]nimo\s*$(.*?)(?=^#{1,6}\s|\Z)", cuerpo, re.S | re.M | re.I)
    if not m:
        return None
    f = re.search(r"^```[^\n]*\n(.*?)^```", m.group(1), re.S | re.M)
    return f.group(1).splitlines() if f else None


def revisar(texto, negra, permitidas):
    """-> lista de (linea, motivo)"""
    out = []
    for n, linea in enumerate(texto.splitlines(), 1):
        for t in negra:
            if re.search(r"(?<!\w)%s(?!\w)" % re.escape(t), linea, re.I):
                out.append((n, "nombre de la lista negra «%s»" % t))
        for m in EMAIL.finditer(linea):
            out.append((n, "email «%s»" % m.group(0)))
        for m in RUTA.finditer(linea):
            out.append((n, "ruta de usuario o de red «%s»" % m.group(0)[:40]))
        for m in URL.finditer(linea):
            if not URL_OK.match(m.group(1)):
                out.append((n, "URL «%s»" % m.group(0)[:60]))
        for m in CIFRA.finditer(linea):
            if m.group(1) not in permitidas:
                out.append((n, "cifra «%s» (más de 3 dígitos)" % m.group(1)))
    return out


def main(argv=None):
    utf8()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("candidato")
    ap.add_argument("--lista-negra", help="archivo con un nombre por línea (clientes, personas, sistemas, dominios)")
    ap.add_argument("--nombre", action="append", default=[], help="nombre a prohibir (repetible)")
    ap.add_argument("--permitir-cifra", action="append", default=[])
    a = ap.parse_args(argv)
    ruta = Path(a.candidato)
    if not ruta.is_file():
        sys.exit("No existe el candidato %s" % ruta)
    texto = ruta.read_text(encoding="utf-8")
    negra = list(a.nombre)
    if a.lista_negra:
        negra += [l.strip() for l in Path(a.lista_negra).read_text(encoding="utf-8").splitlines() if l.strip() and not l.strip().startswith("#")]
    problemas = []
    datos, cuerpo = frontmatter(texto)
    if datos is None:
        problemas.append("falta el frontmatter (--- ... ---) con " + ", ".join(REQUERIDOS))
        datos = {}
    for k in REQUERIDOS:
        if not str(datos.get(k, "")).strip():
            problemas.append("falta o está vacío «%s» en el frontmatter" % k)
    if datos.get("id") and not re.fullmatch(r"[a-z0-9][a-z0-9-]*", datos["id"]):
        problemas.append("id debe ser minúsculas, números y guiones (vale «%s»)" % datos["id"])
    if len(datos.get("regla_1_linea", "")) > 200:
        problemas.append("regla_1_linea pasa de 200 caracteres: tiene que ser una línea")
    if datos.get("causa_tecnica") and len(datos["causa_tecnica"]) < 20:
        problemas.append("causa_tecnica es demasiado corta para explicar la causa")
    pv = datos.get("proyectos_que_lo_vieron", "").strip()
    if pv and pv.isdigit() and int(pv) < 2:
        problemas.append("proyectos_que_lo_vieron = %s: una regla general pide haberse visto en al menos 2 proyectos" % pv)
    caso = caso_minimo(cuerpo)
    if caso is None:
        problemas.append("falta la sección «## Caso mínimo» con un bloque de código ```")
    elif len(caso) >= 30:
        problemas.append("el caso mínimo tiene %d líneas; el máximo son 29" % len(caso))
    elif not any(l.strip() for l in caso):
        problemas.append("el caso mínimo está vacío")
    for n, motivo in revisar(texto, negra, set(a.permitir_cifra)):
        problemas.append("línea %d: %s" % (n, motivo))
    if problemas:
        print("NO se puede promover %s:" % ruta.name)
        for p in problemas:
            print("  - " + p)
        return 1
    print("OK %s: sin filtraciones, caso mínimo de %d líneas.\n" % (ruta.name, len(caso)))
    print("BORRADOR DE PR")
    print("titulo: regla: %s" % datos["regla_1_linea"])
    print("rama:   regla/%s" % datos["id"])
    print("archivos a tocar (sugeridos):")
    print("  - skill/references/reglas-generales.md  (una fila: %s | %s | %s)" % (datos["id"], datos["regla_1_linea"], datos["causa_tecnica"][:80]))
    print("  - skill/scripts/tests/sitio/%s.html  (el caso mínimo: %d líneas, sin datos del proyecto)" % (datos["id"], len(caso)))
    print("  - skill/scripts/tests/run_tests.py  (una aserción: dispara con ese caso y no con limpio.html)")
    print("cuerpo:\n  Regla: %s\n  Causa: %s\n  Visto en %s proyecto(s). Caso mínimo adjunto; sin nombres, rutas, URLs ni cifras de producción." % (datos["regla_1_linea"], datos["causa_tecnica"], pv))
    return 0


if __name__ == "__main__":
    sys.exit(main())
