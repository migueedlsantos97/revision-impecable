#!/usr/bin/env python3
"""Mide una web o app andando: recorre cada pantalla del adaptador en varios anchos y temas, y entrega fallas con prueba.

Uso:
  python medir.py --config .claude/revision/proyecto.json [--url URL] [--sistema X] [--pantalla ID] [--rapido] [--salida DIR]
  python medir.py --descubrir --url http://127.0.0.1:8000 [--config proyecto.json] [--max-paginas 40] [--profundidad 2]

Mide lo que no necesita criterio: contraste, tamaño táctil, texto chico, desbordes, solapes, controles nativos,
glifos como íconos, imágenes rotas, errores de consola y de red, foco invisible, tema aplicado a medias, accesibilidad
básica (lang, viewport, alt, nombres, ids, ARIA, headings), tapados por overlays, CLS y la consistencia de componentes
entre pantallas y sistemas. Cada falla lleva `certeza`: "medida" (hecho) o "sospecha" (hay que mirarla con criterio).
Escribe informe.json, informe.md, capturas y una hoja de contacto por pantalla. Sale 1 si hay fallas.

Nunca apunta a producción: usa la URL de prueba del adaptador o levanta la instancia con su comando de arranque.
"""
import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict, deque
from datetime import datetime
from pathlib import Path
from urllib.parse import urldefrag, urlparse

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
    "alto_movil": 844, "alto_escritorio": 900, "ancho_movil": 600,        # viewport emulado (px)
    "timeout_carga": 20000, "timeout_paso": 6000, "timeout_esperar": 10000,  # ms
    "pausa_paso": 120, "pausa_medir": 350, "red_quieta": 5000,            # ms; red_quieta: tope de espera de red inactiva (no falla)
    "max_tab": 30,           # cuántos Tab recorre la prueba de foco
    "max_candidatos_solape": 700, "max_componentes": 1500, "max_muestra": 900,
    "tol_solape": 2, "tol_recorte": 4,                                   # px
    "texto_grande_px": 24, "texto_grande_negrita_px": 18.66, "saturacion": 0.35,
    "cls_max": 0.1,          # Cumulative Layout Shift tolerado (Google: <= 0.1 es "bueno")
    "heading_max_salto": 1,  # niveles que puede saltarse un heading respecto del anterior
    "ignorar_url": [],       # regex de URLs cuyos 4xx/5xx y fallas de red no cuentan
    "desactivar": [],        # tipos de falla a descartar, p. ej. ["img_sin_dimensiones"]
}
SOSPECHA = {"img_sin_dimensiones", "heading_h1", "heading_salto", "tapado", "texto_cortado_sin_title", "titulo_duplicado",
            "enlace_falso", "solape_truncado", "variantes", "casi_iguales", "escala", "distinto_por_sistema",
            "mismo_rotulo_distinta_forma", "tema_a_medias", "recortado"}


def _url(base, ruta):
    return ruta if "://" in ruta else base.rstrip("/") + "/" + ruta.lstrip("/")


_ABRIR = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # why: un proxy de la empresa rompe 127.0.0.1


def _responde(url, espera=0.0, proc=None):
    """True si el servidor contesta algo que no sea 5xx (un 401/404 en "/" también es "vivo")."""
    fin = time.time() + espera
    while True:
        try:
            with _ABRIR.open(url, timeout=3) as r:
                return r.status < 500
        except urllib.error.HTTPError as e:
            return e.code < 500
        except Exception:
            if proc is not None and proc.poll() is not None:
                return False  # why: el proceso murió (puerto ocupado, comando roto); no esperar el plazo entero
            if time.time() >= fin:
                return False
            time.sleep(0.5)


class Instancia:
    """Levanta la instancia de prueba del adaptador si no está corriendo, y apaga solo lo que levantó."""

    def __init__(self, cfg, raiz):
        self.cfg, self.raiz, self.proc, self.log = cfg.get("arranque") or {}, raiz, None, None

    def __enter__(self):
        return self

    def levantar(self, url):
        cmd = self.cfg.get("comando")
        if _responde(url):
            if cmd:
                print("aviso: %s ya responde; se mide esa instancia sin arrancar otra. Si no es la de prueba, cortala y usá otro puerto." % url, file=sys.stderr)
            return
        if not cmd:
            sys.exit("La URL %s no responde y el adaptador no tiene arranque.comando." % url)
        ruta_log = self.raiz / ".claude" / "revision" / "instancia.log"
        ruta_log.parent.mkdir(parents=True, exist_ok=True)
        self.log = open(ruta_log, "wb")
        env = {**os.environ, **{k: str(v) for k, v in (self.cfg.get("env") or {}).items()}}
        extra = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
        self.proc = subprocess.Popen(cmd, shell=True, cwd=self.raiz / self.cfg.get("cwd", "."), stdout=self.log, stderr=self.log, env=env, **extra)
        espera = float(self.cfg.get("espera", 60))
        if not _responde(_url(url, self.cfg.get("listo", "/")), espera=espera, proc=self.proc):
            self.__exit__()
            sys.exit("La instancia no quedó lista (o el proceso murió). Mirá .claude/revision/instancia.log")
        marca = self.cfg.get("listo_log")
        if marca:  # why: una instancia con siembra responde antes de terminar de sembrar; medir ahí mide pantallas a medias
            fin = time.time() + espera
            while marca not in ruta_log.read_text(encoding="utf-8", errors="ignore")[-20000:]:
                if time.time() > fin or self.proc.poll() is not None:
                    self.__exit__()
                    sys.exit("La instancia no escribió «%s» en el log a tiempo." % marca)
                time.sleep(1)

    def __exit__(self, *a):
        p, self.proc = self.proc, None
        try:
            if p and p.poll() is None:
                # why: matar por nombre de proceso puede tumbar la sesión de otra persona; se mata solo el árbol propio, por PID
                if os.name == "nt":
                    subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
                else:
                    os.killpg(p.pid, signal.SIGTERM)
                    try:
                        p.wait(10)
                    except subprocess.TimeoutExpired:
                        os.killpg(p.pid, signal.SIGKILL)
                try:
                    p.wait(10)
                except subprocess.TimeoutExpired:
                    pass
        except Exception as ex:  # why: apagar mal no puede impedir que se escriba el informe
            print("aviso: no pude apagar la instancia (pid %s): %s" % (getattr(p, "pid", "?"), ex), file=sys.stderr)
        finally:
            if self.log:
                self.log.close()
                self.log = None


def _rellenar(texto, datos):
    for k, v in datos.items():  # why: str.format revienta con llaves de JS/JSON dentro del valor
        texto = texto.replace("{" + k + "}", str(v))
    return texto


def _pasos(pg, pasos, u=None):
    u = u or UMBRALES
    for p in pasos or []:
        a, sel, val = p.get("accion"), p.get("selector", ""), p.get("valor", "")
        if a == "click":
            pg.click(sel, timeout=u["timeout_paso"])
        elif a == "fill":
            pg.fill(sel, val, timeout=u["timeout_paso"])
        elif a == "ir":
            if pg.locator(sel).first.is_visible():
                pg.click(sel, timeout=u["timeout_paso"])
            else:
                for s in p.get("alt", []):
                    pg.click(s, timeout=u["timeout_paso"])
                    pg.wait_for_timeout(250)
        elif a == "esperar":
            pg.wait_for_selector(sel, timeout=u["timeout_esperar"])
        elif a == "presionar":
            if not val:
                raise ValueError("paso 'presionar' sin valor")
            pg.keyboard.press(val)
        elif a == "pausa":
            pg.wait_for_timeout(int(val or 300))
        elif a == "js":
            pg.evaluate(val)
        else:
            raise ValueError("acción desconocida en pasos: %r" % a)
        pg.wait_for_timeout(u["pausa_paso"])


def _sesiones(nav, cfg, base, carpeta, u):
    """Inicia sesión una vez por rol y guarda el estado (en una carpeta temporal, no en la salida: lleva cookies y tokens).
    Devuelve {rol: ruta | None}; None = el login falló y las pantallas de ese rol se saltan con falla sin_sesion."""
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
                pg.goto(_url(base, login.get("ruta", "/")), timeout=u["timeout_carga"])
                _pasos(pg, [{**p, "valor": _rellenar(p.get("valor", ""), datos), "selector": _rellenar(p.get("selector", ""), datos)}
                            for p in login.get("pasos", [])], u)
            ruta = carpeta / ("sesion-%s.json" % re.sub(r"\W", "_", str(rol)))
            ctx.storage_state(path=str(ruta))
            estados[rol] = str(ruta)
        except Exception as ex:
            print("aviso: no pude iniciar sesión como %s: %s" % (rol, ex), file=sys.stderr)
            estados[rol] = None
        finally:
            ctx.close()
    return estados


CLS_JS = ("window.__cls=0;try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cls+=e.value})"
          ".observe({type:'layout-shift',buffered:true})}catch(e){}")


def _contexto(nav, ancho, tema, cfg, estado, u, motor="chromium"):
    movil = ancho < u["ancho_movil"]
    extra = {"has_touch": movil, "is_mobile": movil} if motor != "firefox" else {"has_touch": movil}  # why: Firefox no emula is_mobile
    ctx = nav.new_context(viewport={"width": ancho, "height": u["alto_movil"] if movil else u["alto_escritorio"]},
                          color_scheme="dark" if tema == "oscuro" else "light", storage_state=estado, reduced_motion="reduce", **extra)
    js = (cfg.get("tema") or {}).get("init_js")
    if js:
        ctx.add_init_script(js.replace("{tema}", "dark" if tema == "oscuro" else "light"))
    ctx.add_init_script(CLS_JS)
    return ctx, movil


FOCO_JS = """(n) => {
  const f1 = (e) => { if (!e) return ''; const s = getComputedStyle(e); return [s.outlineStyle, s.outlineWidth, s.outlineColor, s.boxShadow, s.backgroundColor, s.borderTopColor, s.borderBottomColor, s.color, s.textDecorationLine].join('|'); };
  // why: un input escondido delega el foco en su label o su caja (:has(:focus-visible)); se mira la familia cercana
  const firma = (e) => [e, e.parentElement, e.parentElement && e.parentElement.parentElement, e.nextElementSibling, e.closest('label')].map(f1).join('#');
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


def _foco(pg, umbrales):
    fallas, vistos = [], set()
    for _ in range(umbrales["max_tab"]):
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
    "boton_primario": ("alto", "radio", "fuente", "peso", "relleno"),
    "boton_secundario": ("alto", "radio", "fuente", "peso", "borde"),
    "navegacion": ("alto", "radio", "fuente", "peso"),
    "boton_tarjeta": ("radio", "borde", "sombra"),
    "boton_icono": ("alto", "radio"),
    "campo": ("alto", "radio", "fuente", "borde"),
    "h1": ("fuente", "peso", "tipografia"),
    "h2": ("fuente", "peso", "tipografia"),
    "h3": ("fuente", "peso", "tipografia"),
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
        # la misma clase CSS con varias formas: el componente no es uno
        por_familia = defaultdict(list)
        for c in lista:
            por_familia[c.get("familia", "")].append(c)
        for fam, fl in por_familia.items():
            ff = Counter(tuple(c[k] for k in claves) for c in fl)
            if len(ff) > 1 and "." in fam:
                fallas.append({"tipo": "variantes", "selector": "%s %s" % (clase, fam), "detalle": "la misma clase %s se ve de %d formas: %s" % (
                    fam, len(ff), "; ".join("%s (%d)" % (", ".join("%s %s" % kv for kv in zip(claves, f)), n) for f, n in ff.most_common(3)))})
            # dentro de un mismo componente, dos valores a 1-2 px son una decisión olvidada
            for k in claves:
                vals = sorted({v for v in (_num(c[k]) for c in fl) if v is not None})
                for a, b in zip(vals, vals[1:]):
                    if 0 < b - a <= 2 and k in ("alto", "radio", "fuente"):
                        fallas.append({"tipo": "casi_iguales", "selector": "%s %s" % (clase, fam), "detalle": "%s: %g y %g px conviven" % (k, a, b)})
        # más de 6 valores de un atributo en una clase de componente no es una escala
        for k in ("fuente", "radio", "alto"):
            if k in claves:
                vals = sorted({v for v in (_num(c[k]) for c in lista) if v is not None})
                if len(vals) > 6:
                    fallas.append({"tipo": "escala", "selector": clase, "detalle": "%d valores de %s: %s" % (len(vals), k, ", ".join("%g" % v for v in vals))})
        # la misma forma cambia según el sistema: cada sistema eligió la suya
        dom = defaultdict(Counter)
        for c in lista:
            dom[c.get("sistema") or "-"][tuple(c[k] for k in claves)] += 1
        principales = {s: cnt.most_common(1)[0][0] for s, cnt in dom.items() if sum(cnt.values()) >= 2}
        if len(set(principales.values())) > 1 and len(principales) > 1:
            fallas.append({"tipo": "distinto_por_sistema", "selector": clase, "detalle": "cada sistema usa otro %s: %s" % (clase, "; ".join(
                "%s → %s" % (s, ", ".join("%s %s" % kv for kv in zip(claves, f))) for s, f in sorted(principales.items())))})
        # el mismo rótulo con distinta forma: «Guardar» no puede verse de dos maneras
        if clase.startswith("boton") and clase != "boton_tarjeta":
            por_texto = defaultdict(set)
            for c in lista:
                if c["texto"] and len(c["texto"]) > 2:
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


def _ignora_url(u):
    pats = [re.compile(p) for p in u["ignorar_url"]]
    return lambda url: url.split("?")[0].endswith("/favicon.ico") or any(p.search(url) for p in pats)


def _vigilar(pg, base, u, errores, red):
    """Consola y red de la pantalla. Las 404 de recursos se leen de `response`: el texto de consola no trae la URL."""
    ignorar = _ignora_url(u)
    https = base.lower().startswith("https://")
    pg.on("console", lambda m: errores.append(m.text) if m.type == "error" and not m.text.startswith("Failed to load resource") else None)
    pg.on("pageerror", lambda e: errores.append(str(e)))
    pg.on("response", lambda r: red.append(("http_error", r.url, "HTTP %d %s" % (r.status, r.request.resource_type)))
          if r.status >= 400 and not ignorar(r.url) else None)
    pg.on("requestfailed", lambda r: red.append(("request_fallida", r.url, str(r.failure)))
          if "ERR_ABORTED" not in str(r.failure) and not ignorar(r.url) else None)
    pg.on("request", lambda r: red.append(("contenido_mixto", r.url, "pide http:// desde una página https://"))
          if https and r.url.lower().startswith("http://") and not ignorar(r.url) else None)


def _lanzar(pw, motor, headless):
    tipo = getattr(pw, motor)
    try:
        return tipo.launch(headless=headless)
    except Exception as ex:
        if motor == "chromium":  # why: si el Chromium de Playwright no está bajado, sirve el Chrome instalado
            try:
                return tipo.launch(headless=headless, channel="chrome")
            except Exception:
                pass
        sys.exit("No pude abrir %s: %s\nInstalá el navegador con:  python -m playwright install %s" % (motor, str(ex).splitlines()[0][:200], motor))


def _cargar(pg, url, u):
    pg.goto(url, wait_until="load", timeout=u["timeout_carga"])
    try:  # why: una app con polling o websocket nunca queda "idle"; esperar la red es best-effort, no una falla
        pg.wait_for_load_state("networkidle", timeout=u["red_quieta"])
    except Exception:
        pass


def medir(cfg, base, salida, anchos, temas, filtro_sistema=None, filtro_pantalla=None, headless=True, motores=("chromium",), acum=None):
    from playwright.sync_api import sync_playwright
    umbrales = {**UMBRALES, **cfg.get("umbrales", {})}
    acum = acum if acum is not None else {"fallas": [], "componentes": [], "titulos": {}}
    fallas, componentes, titulos = acum["fallas"], acum["componentes"], acum["titulos"]
    pantallas = [p for p in cfg["pantallas"] if (not filtro_sistema or p.get("sistema") in filtro_sistema)
                 and (not filtro_pantalla or p["id"] in filtro_pantalla)]
    capturas = salida / "capturas"
    capturas.mkdir(parents=True, exist_ok=True)
    privado = Path(tempfile.mkdtemp(prefix="revision-sesion-"))  # why: las sesiones llevan cookies y tokens; no van a la salida
    try:
        with sync_playwright() as pw:
            for k, motor in enumerate(motores):
                primero = k == 0
                nav = _lanzar(pw, motor, headless)
                try:
                    estados = _sesiones(nav, cfg, base, privado, umbrales)
                    for pan in pantallas:
                        _pantalla(nav, motor, primero, len(motores) > 1, pan, cfg, base, salida, capturas, anchos, temas, umbrales, estados, acum)
                finally:
                    nav.close()
    finally:
        shutil.rmtree(privado, ignore_errors=True)
    return acum



def _etiquetar(res, pan, ancho, tema, motor, varios):
    out = []
    for h in res:
        h = {"pantalla": pan["id"], "sistema": pan.get("sistema", ""), "ancho": ancho, "tema": tema, **h}
        if varios:
            h["motor"] = motor
        out.append(h)
    return out


def _pantalla(nav, motor, primero, varios, pan, cfg, base, salida, capturas, anchos, temas, umbrales, estados, acum):
    fallas, componentes, titulos = acum["fallas"], acum["componentes"], acum["titulos"]
    roles = (cfg.get("login") or {}).get("roles") or {}
    estado = None
    if pan.get("rol"):
        estado = estados.get(pan["rol"])
        if roles and estado is None:  # why: medir sin sesión mediría la pantalla de login haciéndola pasar por la pantalla
            fallas += _etiquetar([{"tipo": "sin_sesion", "selector": pan["ruta"], "detalle": "no se pudo iniciar sesión como «%s»; pantalla saltada" % pan["rol"]}], pan, 0, "", motor, varios)
            return
    caps, temas_medidos = [], {}
    validos = [x for x in anchos if pan.get("ancho_min", 0) <= x <= pan.get("ancho_max", 99999)]
    for tema in temas:
        for ancho in validos:
            ctx, movil = _contexto(nav, ancho, tema, cfg, estado, umbrales, motor)
            errores, red, res = [], [], []
            try:
                pg = ctx.new_page()
                _vigilar(pg, base, umbrales, errores, red)
                _cargar(pg, _url(base, pan["ruta"]), umbrales)
                if pan.get("esperar"):
                    pg.wait_for_selector(pan["esperar"], timeout=umbrales["timeout_esperar"])
                aplicar = (cfg.get("tema") or {}).get("aplicar_js")
                if aplicar:  # why: hay temas que se cambian con un botón y no siguen la preferencia del sistema
                    pg.evaluate(aplicar.replace("{tema}", "dark" if tema == "oscuro" else "light"))
                _pasos(pg, pan.get("pasos"), umbrales)
                pg.wait_for_timeout(umbrales["pausa_medir"])
                u = {**umbrales, "tactil": umbrales["tactil"] if movil else (umbrales["tactil_puntero"] or umbrales["tactil"])}
                r = pg.evaluate(MEDIDAS, u)
                res = list(r["fallas"]) + [{"tipo": "consola", "selector": "", "detalle": e[:240]} for e in errores]
                vistas = set()
                for tipo, url, det in red:
                    if (tipo, url) not in vistas:
                        vistas.add((tipo, url))
                        res.append({"tipo": tipo, "selector": url[:200], "detalle": det})
                try:
                    cls = float(pg.evaluate("window.__cls||0"))
                    if cls > umbrales["cls_max"]:
                        res.append({"tipo": "cls_alto", "selector": "", "detalle": "CLS %.3f; el máximo es %g (la página se corre al cargar)" % (cls, umbrales["cls_max"])})
                except Exception:
                    pass
                if ancho == max(validos):
                    if primero:
                        temas_medidos[tema] = r["tema"]
                    if tema == temas[0] and primero:
                        componentes += [{**c, "pantalla": pan["id"], "sistema": pan.get("sistema", "")} for c in r["componentes"]]
                        titulos[pan["id"]] = r.get("titulo", "")
                        res += _foco(pg, umbrales)
                png = capturas / ("%s-%d-%s%s.png" % (pan["id"], ancho, tema, "" if primero else "-" + motor))
                try:
                    pg.screenshot(path=str(png), full_page=True)
                except Exception:  # why: una página de más de 16384 px no admite full_page; sin captura completa igual se conservan las fallas
                    try:
                        pg.screenshot(path=str(png))
                    except Exception as ex2:
                        res.append({"tipo": "captura_fallida", "selector": "", "detalle": str(ex2).splitlines()[0][:200]})
                if png.exists() and primero:
                    caps.append(png)
            except Exception as ex:  # why: una pantalla que no carga es una falla, no el fin del recorrido
                res = [{"tipo": "no_carga", "selector": pan["ruta"], "detalle": str(ex).splitlines()[0][:240]}]
            finally:
                ctx.close()
            fallas += _etiquetar(res, pan, ancho, tema, motor, varios)
    if len(temas_medidos) == 2:
        fallas += _etiquetar([{**h} for h in _tema_a_medias(temas_medidos.get("claro"), temas_medidos.get("oscuro"))], pan, 0, "ambos", motor, varios)
    if primero:
        montaje(caps, salida / ("montaje-%s.png" % pan["id"]))


def finalizar(acum, umbrales):
    """Fallas que solo se ven con todas las pantallas juntas, filtro de tipos apagados y certeza. -> resumen de consistencia"""
    f2, resumen = consistencia(acum["componentes"], umbrales)
    por_titulo = defaultdict(list)
    for pid, t in acum["titulos"].items():
        if t.strip():
            por_titulo[t.strip()].append(pid)
    for t, ids in por_titulo.items():
        if len(ids) > 1:
            f2.append({"tipo": "titulo_duplicado", "selector": "title", "detalle": "«%s» en %d pantallas: %s" % (t[:60], len(ids), ", ".join(ids[:6]))})
    acum["fallas"] += [{"pantalla": "(todas)", "sistema": "", "ancho": 0, "tema": "", **h} for h in f2]
    apagados = set(umbrales["desactivar"])
    acum["fallas"][:] = [h for h in acum["fallas"] if h["tipo"] not in apagados]
    for h in acum["fallas"]:
        h.setdefault("certeza", "sospecha" if h["tipo"] in SOSPECHA else "medida")
    return resumen


def informe(fallas, resumen, salida, cfg):
    por_tipo = Counter(f["tipo"] for f in fallas)
    por_certeza = Counter(f.get("certeza", "medida") for f in fallas)
    datos = {"proyecto": cfg.get("nombre", ""), "fecha": datetime.now().isoformat(timespec="minutes"), "total": len(fallas),
             "por_tipo": dict(por_tipo), "por_certeza": dict(por_certeza), "fallas": fallas, "consistencia": resumen}
    (salida / "informe.json").write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    md = ["# Medición — %s (%s)" % (datos["proyecto"], datos["fecha"]), "", "Total: **%d** (%d medidas, %d sospechas: mirarlas con criterio)" % (
        len(fallas), por_certeza.get("medida", 0), por_certeza.get("sospecha", 0)), ""]
    md += ["| tipo | cantidad |", "|---|---|"] + ["| %s | %d |" % kv for kv in por_tipo.most_common()] + [""]
    agrupadas = defaultdict(list)
    for f in fallas:
        agrupadas[(f["tipo"], f["selector"], f["detalle"].split(",")[0])].append(f)
    md += ["## Fallas (agrupadas: una línea por defecto, con dónde aparece)", ""]
    for (tipo, sel, _), fs in sorted(agrupadas.items(), key=lambda kv: (kv[0][0], -len(kv[1])))[:400]:
        donde = sorted({"%s@%s/%s%s" % (f["pantalla"], f["ancho"], f["tema"], "/" + f["motor"] if f.get("motor") else "") for f in fs})
        md.append("- **%s**%s `%s` — %s · %s" % (tipo, " (sospecha)" if fs[0].get("certeza") == "sospecha" else "", sel, fs[0]["detalle"],
                                               ", ".join(donde[:6]) + (" y %d más" % (len(donde) - 6) if len(donde) > 6 else "")))
    md += ["", "## Formas de cada componente (de la más usada a la menos)", ""]
    for clase, formas in resumen.items():
        md.append("### %s (%d formas)" % (clase, len(formas)))
        for f in formas[:8]:
            md.append("- %d× %s — sistemas: %s — ej.: %s" % (f["veces"], ", ".join("%s %s" % kv for kv in f["forma"].items()), ", ".join(f["sistemas"]), f["ejemplo"]))
        md.append("")
    (salida / "informe.md").write_text("\n".join(md), encoding="utf-8")
    return datos


# --- descubrimiento: crawl BFS de enlaces del mismo origen, solo lectura (nunca clic en botones, nunca rutas de salir/borrar) ---
PELIGROSA = re.compile(r"(logout|log-out|signout|sign-out|salir|cerrar[-_ ]?sesi|desconect|delete|eliminar|borrar|remove|destroy|reset|unsubscribe)", re.I)
ARCHIVO = re.compile(r"\.(pdf|zip|rar|7z|exe|msi|dmg|png|jpe?g|gif|svg|webp|ico|mp4|mp3|csv|xlsx?|docx?|css|js|json|xml|txt|map)$", re.I)
ID_EN_RUTA = re.compile(r"/(?:\d+|[0-9a-fA-F]{8}-[0-9a-fA-F-]{27}|[0-9a-fA-F]{12,})(?=/|$)")


def _ruta_normal(href, origen):
    """href absoluto -> '/ruta' (o '/ruta#/hash' si la app enruta por hash) | None si no es una pantalla"""
    p = urlparse(href)
    if p.scheme not in ("http", "https") or p.netloc != origen:
        return None
    ruta, frag = p.path or "/", p.fragment
    if ARCHIVO.search(ruta) or PELIGROSA.search(ruta + " " + frag):
        return None
    return ruta + ("#" + frag if frag.startswith(("/", "!/")) else "")


def _plantilla(ruta):
    return ID_EN_RUTA.sub("/:n", ruta)


def _slug(ruta, usados):
    s = re.sub(r"[^a-z0-9]+", "-", ruta.lower()).strip("-") or "inicio"
    base, n = s, 2
    while s in usados:
        s, n = "%s-%d" % (base, n), n + 1
    usados.add(s)
    return s


def descubrir(cfg, base, rol, max_paginas, profundidad, headless):
    from playwright.sync_api import sync_playwright
    u = {**UMBRALES, **cfg.get("umbrales", {})}
    origen = urlparse(base).netloc
    cola, vistas, ejemplos, pantallas, usados = deque([("/", 0)]), set(), Counter(), [], set()
    try:  # semillas del sitemap, si lo hay
        with _ABRIR.open(base.rstrip("/") + "/sitemap.xml", timeout=3) as r:
            for loc in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", r.read(500000).decode("utf-8", "ignore")):
                rn = _ruta_normal(loc, origen)
                if rn:
                    cola.append((rn, 1))
    except Exception:
        pass
    with sync_playwright() as pw:
        nav = _lanzar(pw, "chromium", headless)
        privado = Path(tempfile.mkdtemp(prefix="revision-sesion-"))
        try:
            estado = _sesiones(nav, cfg, base, privado, u).get(rol) if rol else None
            if rol and not estado:
                sys.exit("No pude iniciar sesión como %s; no se descubre sin sesión una app con login." % rol)
            ctx = nav.new_context(storage_state=estado, viewport={"width": 1366, "height": 900})
            pg = ctx.new_page()
            while cola and len(pantallas) < max_paginas:
                ruta, prof = cola.popleft()
                tpl = _plantilla(ruta)
                if ruta in vistas or ejemplos[tpl] >= 2:  # why: /item/1 y /item/2 son la misma pantalla; 2 ejemplos por plantilla
                    continue
                vistas.add(ruta)
                try:
                    _cargar(pg, _url(base, ruta), u)
                except Exception as ex:
                    print("aviso: %s no carga: %s" % (ruta, str(ex).splitlines()[0][:100]), file=sys.stderr)
                    continue
                final = _ruta_normal(pg.url, origen) or ruta
                if final != ruta and final in vistas:
                    continue  # why: redirige a una pantalla ya vista (típico: /admin -> /login)
                vistas.add(final)
                ejemplos[tpl] += 1
                p = {"id": _slug(final, usados), "ruta": final}
                if rol:
                    p["rol"] = rol
                pantallas.append(p)
                if prof >= profundidad:
                    continue
                try:
                    hrefs = pg.eval_on_selector_all("a[href]", "els => els.filter(e => e.target !== '_blank' && !e.hasAttribute('download')).map(e => e.href)")
                except Exception:
                    hrefs = []
                for h in hrefs:
                    rn = _ruta_normal(h, origen)
                    if rn and rn not in vistas:
                        cola.append((rn, prof + 1))
            ctx.close()
        finally:
            nav.close()
            shutil.rmtree(privado, ignore_errors=True)
    return pantallas


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
    ap.add_argument("--motores", help="p. ej. chromium,firefox,webkit (el primero da capturas y consistencia; los otros suman fallas)")
    ap.add_argument("--descubrir", action="store_true", help="recorre los enlaces desde la URL y escribe un proyecto.json candidato")
    ap.add_argument("--rol", help="con --descubrir: rol del login del adaptador con el que recorrer")
    ap.add_argument("--max-paginas", type=int, default=40)
    ap.add_argument("--profundidad", type=int, default=2)
    a = ap.parse_args(argv)

    try:
        import playwright.sync_api  # noqa: F401
    except ImportError:
        sys.exit("Falta playwright. Instalalo con:\n  python -m pip install -r %s\n  python -m playwright install chromium" % (AQUI / "requirements.txt"))

    cfg_path = Path(a.config).resolve()
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    elif a.descubrir and a.url:
        cfg = {"nombre": urlparse(a.url).netloc, "url": a.url}
    else:
        sys.exit("No encuentro el adaptador %s. Crealo (ver references/adaptador.md) o probá --descubrir --url URL." % cfg_path)
    raiz = cfg_path.parent.parent.parent if cfg_path.parent.name == "revision" else Path.cwd()
    base = a.url or cfg.get("url")
    if not base:
        sys.exit("Falta la URL: ponela en el adaptador (\"url\") o pasá --url.")
    motores = tuple(m.strip() for m in a.motores.split(",")) if a.motores else ("chromium",)
    if any(m not in ("chromium", "firefox", "webkit") for m in motores):
        sys.exit("--motores admite chromium, firefox y webkit.")

    if a.descubrir:
        with Instancia(cfg, raiz) as inst:
            if not a.url:
                inst.levantar(base)
            pantallas = descubrir(cfg, base, a.rol, a.max_paginas, a.profundidad, not a.ver)
        cand = {**cfg, "url": base, "pantallas": pantallas, "_descubierto": "candidato: revisar ids, roles y sumar estados (diálogos, listas vacías, errores)"}
        destino = cfg_path if not cfg_path.exists() else cfg_path.with_name(cfg_path.stem + ".candidato.json")
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(cand, ensure_ascii=False, indent=1), encoding="utf-8")
        print("%d pantallas descubiertas -> %s" % (len(pantallas), destino))
        return 0

    if not cfg.get("pantallas"):
        sys.exit("El adaptador no tiene \"pantallas\". Armalas a mano o corré con --descubrir.")
    anchos = tuple(int(x) for x in a.anchos.split(",")) if a.anchos else (RAPIDO if a.rapido else tuple(cfg.get("anchos", ANCHOS)))
    temas = tuple(cfg.get("temas", TEMAS))
    salida = Path(a.salida) if a.salida else raiz / ".claude" / "revision" / "salida" / datetime.now().strftime("%Y%m%d-%H%M%S")
    salida.mkdir(parents=True, exist_ok=True)
    (raiz / ".claude" / "revision").mkdir(parents=True, exist_ok=True)
    acum = {"fallas": [], "componentes": [], "titulos": {}}
    umbrales = {**UMBRALES, **cfg.get("umbrales", {})}
    resumen, empezo = {}, False
    try:  # why: pase lo que pase al apagar o a mitad del recorrido, lo medido hasta ahí queda escrito
        with Instancia(cfg, raiz) as inst:
            if not a.url:
                inst.levantar(base)
            empezo = True
            medir(cfg, base, salida, anchos, temas, a.sistema, a.pantalla, headless=not a.ver, motores=motores, acum=acum)
    finally:
        if empezo:
            resumen = finalizar(acum, umbrales)
            datos = informe(acum["fallas"], resumen, salida, cfg)
            print("%d fallas %s\n-> %s" % (datos["total"], dict(Counter(f["tipo"] for f in acum["fallas"]).most_common()), salida / "informe.md"))
    return 1 if acum["fallas"] else 0


if __name__ == "__main__":
    sys.exit(main())
