#!/usr/bin/env python3
"""Mide una web o app andando: recorre cada pantalla del adaptador en varios anchos y temas, y entrega fallas con prueba.

Uso:
  python medir.py --config .claude/revision/proyecto.json [--url URL] [--sistema X] [--pantalla ID] [--rapido] [--salida DIR]

Mide lo que no necesita criterio: contraste, tamaño táctil, texto chico, desbordes, solapes, controles nativos,
glifos como íconos, imágenes rotas, errores de consola, foco invisible, tema aplicado a medias y la consistencia
de componentes entre pantallas y sistemas. Escribe informe.json, informe.md, capturas y una hoja de contacto por
pantalla. Sale 1 si hay fallas.

Nunca apunta a producción: usa la URL de prueba del adaptador o levanta la instancia con su comando de arranque.
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MEDIDAS = (AQUI / "medidas.js").read_text(encoding="utf-8")
ANCHOS = (390, 768, 1366, 1920)
RAPIDO = (390, 1366)
TEMAS = ("claro", "oscuro")
UMBRALES = {
    "tactil": 44,            # Apple HIG: 44x44 pt para todo lo que se toca
    "tactil_puntero": 0,     # 0 = igual que tactil; en apps solo de escritorio puede bajar (HIG macOS)
    "texto": 12,             # HIG: 11 pt es el mínimo absoluto; 12 px en web; el proyecto puede subirlo
    "contraste": "AA",
    "icono_sin_nombre": True,
    "scroll_propio": False,  # True si el proyecto prohíbe la barra de fábrica
    "foco_propio": False,    # True si el proyecto pide foco propio: el anillo de fábrica cuenta como falla
    "max_variantes": 3,      # cuántas formas distintas de un mismo componente se toleran
}


def _url(base, ruta):
    return ruta if "://" in ruta else base.rstrip("/") + "/" + ruta.lstrip("/")


def _responde(url, espera=0.0):
    fin = time.time() + espera
    while True:
        try:
            with urllib.request.urlopen(url, timeout=3) as r:
                return r.status < 500
        except Exception:
            if time.time() >= fin:
                return False
            time.sleep(0.5)


class Instancia:
    """Levanta la instancia de prueba del adaptador si no está corriendo, y apaga solo lo que levantó."""

    def __init__(self, cfg, raiz):
        self.cfg, self.raiz, self.proc = cfg.get("arranque") or {}, raiz, None

    def __enter__(self):
        return self

    def levantar(self, url):
        if _responde(url):
            return
        cmd = self.cfg.get("comando")
        if not cmd:
            sys.exit("La URL %s no responde y el adaptador no tiene arranque.comando." % url)
        log = open(self.raiz / ".claude" / "revision" / "instancia.log", "ab")
        self.proc = subprocess.Popen(cmd, shell=True, cwd=self.raiz / self.cfg.get("cwd", "."), stdout=log, stderr=log,
                                     start_new_session=True, env={**os.environ, **self.cfg.get("env", {})})
        if not _responde(_url(url, self.cfg.get("listo", "/")), espera=float(self.cfg.get("espera", 60))):
            self.__exit__()
            sys.exit("La instancia no quedó lista. Mirá .claude/revision/instancia.log")

    def __exit__(self, *a):
        if self.proc and self.proc.poll() is None:
            # why: matar por nombre de proceso puede tumbar la sesión de otra persona; se mata solo el grupo propio
            os.killpg(self.proc.pid, signal.SIGTERM)
            try:
                self.proc.wait(10)
            except subprocess.TimeoutExpired:
                os.killpg(self.proc.pid, signal.SIGKILL)


def _pasos(pg, pasos):
    for p in pasos or []:
        a, sel, val = p.get("accion"), p.get("selector", ""), p.get("valor", "")
        if a == "click":
            pg.click(sel, timeout=6000)
        elif a == "fill":
            pg.fill(sel, val, timeout=6000)
        elif a == "ir":
            if pg.locator(sel).first.is_visible():
                pg.click(sel, timeout=6000)
            else:
                for s in p.get("alt", []):
                    pg.click(s, timeout=6000)
                    pg.wait_for_timeout(250)
        elif a == "esperar":
            pg.wait_for_selector(sel, timeout=10000)
        elif a == "presionar":
            pg.keyboard.press(val)
        elif a == "pausa":
            pg.wait_for_timeout(int(val or 300))
        elif a == "js":
            pg.evaluate(val)
        else:
            raise ValueError("acción desconocida en pasos: %r" % a)
        pg.wait_for_timeout(120)


def _sesiones(nav, cfg, base, carpeta):
    """Inicia sesión una vez por rol y guarda el estado; cada pantalla arranca de ahí."""
    estados = {}
    login = cfg.get("login") or {}
    for rol, datos in (login.get("roles") or {}).items():
        ctx = nav.new_context()
        try:
            if login.get("tipo") == "api":
                r = ctx.request.post(_url(base, login["ruta"]), data=json.dumps(datos),
                                     headers={"Content-Type": "application/json", **login.get("encabezados", {})})
                if not r.ok:
                    raise RuntimeError("HTTP %s" % r.status)
            else:
                pg = ctx.new_page()
                pg.goto(_url(base, login.get("ruta", "/")))
                _pasos(pg, [{**p, "valor": p.get("valor", "").format(**datos)} for p in login.get("pasos", [])])
            ruta = carpeta / ("sesion-%s.json" % rol)
            ctx.storage_state(path=str(ruta))
            estados[rol] = str(ruta)
        except Exception as ex:
            print("aviso: no pude iniciar sesión como %s: %s" % (rol, ex), file=sys.stderr)
        finally:
            ctx.close()
    return estados


def _contexto(nav, ancho, tema, cfg, estado):
    movil = ancho < 600
    ctx = nav.new_context(viewport={"width": ancho, "height": 844 if movil else 900}, color_scheme="dark" if tema == "oscuro" else "light",
                          has_touch=movil, is_mobile=movil, storage_state=estado, reduced_motion="reduce")
    js = (cfg.get("tema") or {}).get("init_js")
    if js:
        ctx.add_init_script(js.replace("{tema}", "dark" if tema == "oscuro" else "light"))
    return ctx, movil


FOCO_JS = """(n) => {
  const firma = (e) => { const s = getComputedStyle(e); return [s.outlineStyle, s.outlineWidth, s.outlineColor, s.boxShadow, s.backgroundColor, s.borderTopColor, s.borderBottomColor, s.color, s.textDecorationLine].join('|'); };
  const sel = (e) => { const p = []; for (let x = e, d = 0; x && x.nodeType === 1 && d < 4; x = x.parentElement, d++) { let t = x.tagName.toLowerCase(); if (x.id) { p.unshift(t + '#' + x.id); break; } const c = [...x.classList].slice(0, 2).join('.'); if (c) t += '.' + c; p.unshift(t); } return p.join(' > '); };
  const e = document.activeElement;
  if (!e || e === document.body) return null;
  const con = firma(e);
  const s = getComputedStyle(e);
  e.blur();
  const sin = firma(e);
  e.focus({ preventScroll: true });
  return { selector: sel(e), visible: con !== sin, fabrica: s.outlineStyle === 'auto' };
}"""


def _foco(pg, umbrales, maximo=30):
    fallas, vistos = [], set()
    for _ in range(maximo):
        pg.keyboard.press("Tab")
        r = pg.evaluate(FOCO_JS)
        if not r or r["selector"] in vistos:
            continue
        vistos.add(r["selector"])
        if not r["visible"]:
            fallas.append({"tipo": "foco_invisible", "selector": r["selector"], "detalle": "al recibir el foco no cambia nada a la vista"})
        elif r["fabrica"] and umbrales["foco_propio"]:
            fallas.append({"tipo": "foco_de_fabrica", "selector": r["selector"], "detalle": "el foco lo marca el anillo del navegador"})
    return fallas


def _tema_a_medias(claro, oscuro):
    """Lo que no cambia al cambiar de tema, cuando la página sí cambió."""
    if not claro or not oscuro or claro["fondoPagina"] == oscuro["fondoPagina"]:
        return []
    out = []
    for sel, a in claro["muestra"].items():
        b = oscuro["muestra"].get(sel)
        if not b or a.get("ok"):
            continue
        if a["fondo"] and a["fondo"] == b["fondo"] and a["fondo"] not in ("#000000",):
            out.append({"tipo": "tema_a_medias", "selector": sel, "detalle": "el fondo %s queda igual en claro y oscuro" % a["fondo"]})
        elif a["color"] and a["color"] == b["color"] and not a["fondo"]:
            out.append({"tipo": "tema_a_medias", "selector": sel, "detalle": "el texto %s queda igual en claro y oscuro" % a["color"]})
    return out[:20]


CLAVES = {
    "boton": ("alto", "radio", "fuente", "peso", "relleno"),
    "boton_icono": ("alto", "radio"),
    "campo": ("alto", "radio", "fuente", "borde"),
    "h1": ("fuente", "peso", "familia"),
    "h2": ("fuente", "peso", "familia"),
    "h3": ("fuente", "peso", "familia"),
    "encabezado_tabla": ("fuente", "peso", "color", "fondo"),
    "pestana": ("alto", "radio", "fuente", "peso"),
    "tarjeta": ("radio", "borde", "sombra"),
    "dialogo": ("radio", "sombra"),
}


def _num(v):
    try:
        return float(str(v).replace("px", "").split()[0])
    except (ValueError, IndexError):
        return None


def consistencia(componentes, umbrales):
    """componentes: [{...firma, pantalla, sistema}] -> (fallas, resumen). Una forma = una decisión; varias = descuido."""
    fallas, resumen = [], {}
    por_clase = defaultdict(list)
    for c in componentes:
        por_clase[c["clase"]].append(c)
    for clase, lista in por_clase.items():
        claves = CLAVES.get(clase)
        if not claves:
            continue
        formas = Counter(tuple(c[k] for k in claves) for c in lista)
        ejemplos = {}
        sistemas = defaultdict(set)
        for c in lista:
            f = tuple(c[k] for k in claves)
            ejemplos.setdefault(f, "%s · %s · «%s»" % (c["pantalla"], c["selector"], c["texto"]))
            sistemas[f].add(c.get("sistema") or "-")
        resumen[clase] = [{"forma": dict(zip(claves, f)), "veces": n, "sistemas": sorted(sistemas[f]), "ejemplo": ejemplos[f]}
                          for f, n in formas.most_common()]
        if len(formas) > umbrales["max_variantes"]:
            fallas.append({"tipo": "variantes", "selector": clase,
                           "detalle": "%d formas distintas de %s; las más usadas: %s" % (len(formas), clase, "; ".join(
                               "%s (%d)" % (", ".join("%s %s" % kv for kv in zip(claves, f)), n) for f, n in formas.most_common(3)))})
        # valores casi iguales: dos decisiones a 1-2 px son una decisión olvidada
        for k in claves:
            vals = sorted({v for v in (_num(c[k]) for c in lista) if v is not None})
            for a, b in zip(vals, vals[1:]):
                if 0 < b - a <= 2 and k in ("alto", "radio", "fuente"):
                    fallas.append({"tipo": "casi_iguales", "selector": clase, "detalle": "%s de %s: %g y %g px conviven" % (k, clase, a, b)})
        # la misma forma cambia según el sistema: cada sistema eligió la suya
        dom = defaultdict(Counter)
        for c in lista:
            dom[c.get("sistema") or "-"][tuple(c[k] for k in claves)] += 1
        principales = {s: cnt.most_common(1)[0][0] for s, cnt in dom.items() if sum(cnt.values()) >= 2}
        if len(set(principales.values())) > 1 and len(principales) > 1:
            fallas.append({"tipo": "distinto_por_sistema", "selector": clase, "detalle": "cada sistema usa otro %s: %s" % (clase, "; ".join(
                "%s → %s" % (s, ", ".join("%s %s" % kv for kv in zip(claves, f))) for s, f in sorted(principales.items())))})
        # el mismo rótulo con distinta forma: «Guardar» no puede verse de dos maneras
        if clase == "boton":
            por_texto = defaultdict(set)
            for c in lista:
                if c["texto"]:
                    por_texto[c["texto"].lower()].add(tuple(c[k] for k in claves))
            for t, fs in por_texto.items():
                if len(fs) > 1:
                    fallas.append({"tipo": "mismo_rotulo_distinta_forma", "selector": "boton «%s»" % t, "detalle": "%d formas para el mismo botón" % len(fs)})
    return fallas, resumen


def montaje(rutas, destino):
    try:
        from PIL import Image
    except ImportError:
        return
    ims = [Image.open(p) for p in rutas if Path(p).exists()]
    if not ims:
        return
    alto = 360
    ims = [i.crop((0, 0, i.width, min(i.height, int(i.width * 2.2)))) for i in ims]
    ims = [i.resize((max(1, int(i.width * alto / i.height)), alto)) for i in ims]
    lienzo = Image.new("RGB", (sum(i.width for i in ims) + 8 * (len(ims) - 1), alto), (70, 70, 70))
    x = 0
    for i in ims:
        lienzo.paste(i, (x, 0))
        x += i.width + 8
    lienzo.save(destino)


def medir(cfg, base, salida, anchos, temas, filtro_sistema=None, filtro_pantalla=None, headless=True):
    from playwright.sync_api import sync_playwright
    umbrales = {**UMBRALES, **cfg.get("umbrales", {})}
    pantallas = [p for p in cfg["pantallas"] if (not filtro_sistema or p.get("sistema") in filtro_sistema)
                 and (not filtro_pantalla or p["id"] in filtro_pantalla)]
    fallas, componentes = [], []
    capturas = salida / "capturas"
    capturas.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        try:
            nav = pw.chromium.launch(headless=headless)
        except Exception:  # why: si el Chromium de Playwright no está bajado, sirve el Chrome instalado
            nav = pw.chromium.launch(headless=headless, channel="chrome")
        estados = _sesiones(nav, cfg, base, salida)
        try:
            for pan in pantallas:
                caps, temas_medidos = [], {}
                for tema in temas:
                    for ancho in anchos:
                        if ancho < pan.get("ancho_min", 0):
                            continue
                        estado = estados.get(pan.get("rol")) if pan.get("rol") else None
                        ctx, movil = _contexto(nav, ancho, tema, cfg, estado)
                        errores, res = [], []
                        try:
                            pg = ctx.new_page()
                            pg.on("console", lambda m: errores.append(m.text) if m.type == "error" and "favicon" not in m.text else None)
                            pg.on("pageerror", lambda e: errores.append(str(e)))
                            pg.goto(_url(base, pan["ruta"]), wait_until="networkidle", timeout=20000)
                            if pan.get("esperar"):
                                pg.wait_for_selector(pan["esperar"], timeout=10000)
                            aplicar = (cfg.get("tema") or {}).get("aplicar_js")
                            if aplicar:  # why: hay temas que se cambian con un botón y no siguen la preferencia del sistema
                                pg.evaluate(aplicar.replace("{tema}", "dark" if tema == "oscuro" else "light"))
                            _pasos(pg, pan.get("pasos"))
                            pg.wait_for_timeout(350)
                            u = {**umbrales, "tactil": umbrales["tactil"] if movil else (umbrales["tactil_puntero"] or umbrales["tactil"])}
                            r = pg.evaluate(MEDIDAS, u)
                            res = r["fallas"] + [{"tipo": "consola", "selector": "", "detalle": e[:240]} for e in errores]
                            if ancho == max(a for a in anchos if a >= pan.get("ancho_min", 0)):
                                temas_medidos[tema] = r["tema"]
                                if tema == temas[0]:
                                    componentes += [{**c, "pantalla": pan["id"], "sistema": pan.get("sistema", "")} for c in r["componentes"]]
                                    res += _foco(pg, umbrales)
                            png = capturas / ("%s-%d-%s.png" % (pan["id"], ancho, tema))
                            pg.screenshot(path=str(png), full_page=True)
                            caps.append(png)
                        except Exception as ex:  # why: una pantalla que no carga es una falla, no el fin del recorrido
                            res = [{"tipo": "no_carga", "selector": pan["ruta"], "detalle": str(ex).splitlines()[0][:240]}]
                        finally:
                            ctx.close()
                        fallas += [{"pantalla": pan["id"], "sistema": pan.get("sistema", ""), "ancho": ancho, "tema": tema, **h} for h in res]
                if len(temas_medidos) == 2:
                    fallas += [{"pantalla": pan["id"], "sistema": pan.get("sistema", ""), "ancho": 0, "tema": "ambos", **h}
                               for h in _tema_a_medias(temas_medidos.get("claro"), temas_medidos.get("oscuro"))]
                montaje(caps, salida / ("montaje-%s.png" % pan["id"]))
        finally:
            nav.close()
    f2, resumen = consistencia(componentes, umbrales)
    fallas += [{"pantalla": "(todas)", "sistema": "", "ancho": 0, "tema": "", **h} for h in f2]
    return fallas, resumen, componentes


def informe(fallas, resumen, salida, cfg):
    por_tipo = Counter(f["tipo"] for f in fallas)
    datos = {"proyecto": cfg.get("nombre", ""), "fecha": datetime.now().isoformat(timespec="minutes"), "total": len(fallas),
             "por_tipo": dict(por_tipo), "fallas": fallas, "consistencia": resumen}
    (salida / "informe.json").write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    md = ["# Medición — %s (%s)" % (datos["proyecto"], datos["fecha"]), "", "Total: **%d**" % len(fallas), ""]
    md += ["| tipo | cantidad |", "|---|---|"] + ["| %s | %d |" % kv for kv in por_tipo.most_common()] + [""]
    agrupadas = defaultdict(list)
    for f in fallas:
        agrupadas[(f["tipo"], f["selector"], f["detalle"].split(",")[0])].append(f)
    md += ["## Fallas (agrupadas: una línea por defecto, con dónde aparece)", ""]
    for (tipo, sel, _), fs in sorted(agrupadas.items(), key=lambda kv: (kv[0][0], -len(kv[1])))[:400]:
        donde = sorted({"%s@%s/%s" % (f["pantalla"], f["ancho"], f["tema"]) for f in fs})
        md.append("- **%s** `%s` — %s · %s" % (tipo, sel, fs[0]["detalle"], ", ".join(donde[:6]) + (" y %d más" % (len(donde) - 6) if len(donde) > 6 else "")))
    md += ["", "## Formas de cada componente (de la más usada a la menos)", ""]
    for clase, formas in resumen.items():
        md.append("### %s (%d formas)" % (clase, len(formas)))
        for f in formas[:8]:
            md.append("- %d× %s — sistemas: %s — ej.: %s" % (f["veces"], ", ".join("%s %s" % kv for kv in f["forma"].items()), ", ".join(f["sistemas"]), f["ejemplo"]))
        md.append("")
    (salida / "informe.md").write_text("\n".join(md), encoding="utf-8")
    return datos


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", default=".claude/revision/proyecto.json")
    ap.add_argument("--url", help="instancia de PRUEBA ya levantada; pisa la del adaptador")
    ap.add_argument("--sistema", action="append")
    ap.add_argument("--pantalla", action="append")
    ap.add_argument("--anchos", help="p. ej. 390,1366")
    ap.add_argument("--rapido", action="store_true", help="solo 390 y 1366")
    ap.add_argument("--salida")
    ap.add_argument("--ver", action="store_true", help="con ventana (para depurar pasos)")
    a = ap.parse_args(argv)

    cfg_path = Path(a.config).resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    raiz = cfg_path.parent.parent.parent if cfg_path.parent.name == "revision" else Path.cwd()
    base = a.url or cfg["url"]
    anchos = tuple(int(x) for x in a.anchos.split(",")) if a.anchos else (RAPIDO if a.rapido else tuple(cfg.get("anchos", ANCHOS)))
    temas = tuple(cfg.get("temas", TEMAS))
    salida = Path(a.salida) if a.salida else raiz / ".claude" / "revision" / "salida" / datetime.now().strftime("%Y%m%d-%H%M")
    salida.mkdir(parents=True, exist_ok=True)
    (raiz / ".claude" / "revision").mkdir(parents=True, exist_ok=True)
    with Instancia(cfg, raiz) as inst:
        if not a.url:
            inst.levantar(base)
        fallas, resumen, _ = medir(cfg, base, salida, anchos, temas, a.sistema, a.pantalla, headless=not a.ver)
    datos = informe(fallas, resumen, salida, cfg)
    print("%d fallas %s\n-> %s" % (datos["total"], dict(Counter(f["tipo"] for f in fallas).most_common()), salida / "informe.md"))
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
