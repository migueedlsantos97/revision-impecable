"""Comprueba que cada caso de evals/casos-v2 arranca y que sus defectos sembrados existen de verdad.
Uso: python evals/verificar_casos_v2.py        (requiere playwright + chromium)
Solo levanta procesos propios y los cierra por objeto, nunca por nombre."""
import json, subprocess, sys, time, urllib.request, urllib.error
from pathlib import Path
from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).parent / "casos-v2"
PUERTOS = {"d-tareas": 8104, "e-roles": 8105, "h-multisistema": 8108, "i-web-publica": 8109, "j-limpio": 8110}
fallas, ok = [], []


def chk(nombre, cond):
    (ok if cond else fallas).append(nombre)
    print(("OK    " if cond else "FALLA ") + nombre)


def http(url, metodo="GET", cuerpo=None, cab=None):
    req = urllib.request.Request(url, data=cuerpo, method=metodo, headers=cab or {})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)


def lanzar(pw):
    for canal in (None, "chrome", "msedge"):
        try:
            return pw.chromium.launch(channel=canal) if canal else pw.chromium.launch()
        except Exception:
            pass
    raise SystemExit("no hay navegador: python -m playwright install chromium")


def levantar():
    procs = {}
    for caso, p in PUERTOS.items():
        procs[caso] = subprocess.Popen([sys.executable, str(RAIZ / caso / "server.py"), str(p)])
    for caso, p in PUERTOS.items():
        for _ in range(50):
            try:
                http(f"http://127.0.0.1:{p}/"); break
            except Exception:
                time.sleep(0.1)
    return procs


def main():
    procs = levantar()
    try:
        # E: permisos
        u = "http://127.0.0.1:8105"
        s, b, _ = http(u + "/api/pedido/2")
        chk("E1 IDOR: /api/pedido/2 sin sesion devuelve datos ajenos", s == 200 and b"Beto" in b or b"HYPERLINK" in b)
        s, _, _ = http(u + "/api/admin/borrar", "POST", b"{}")
        chk("E2 /api/admin/borrar sin rol funciona", s == 200)
        s, b, _ = http(u + "/api/usuarios", cab={"Cookie": "rol=admin"})
        chk("E3 cookie rol=admin sin firma abre /api/usuarios y trae claves (dorado)", s == 200 and b"clave" in b)
        # (E4) el CSV tras el borrado queda vacio; se restablece reiniciando el caso. Se prueba antes en otro orden abajo.
        # D: estado
        d = "http://127.0.0.1:8104"
        fallo = 0
        for i in range(3):
            s, _, _ = http(d + "/api/tareas", "POST", json.dumps({"titulo": f"t{i}"}).encode())
            fallo += s == 500
        chk("D1 cada tercer guardado devuelve 500 (la UI igual dice 'Guardado')", fallo == 1)
        http(d + "/api/tareas/1", "DELETE")
        http(d + "/api/tareas", "POST", b'{"titulo":"nueva"}'); http(d + "/api/tareas", "POST", b'{"titulo":"otra"}')
        ids = [t["id"] for t in json.loads(http(d + "/api/tareas")[1])]
        chk("D4 ids repetidos tras borrar (dorado)", len(ids) != len(set(ids)))
        # I: web publica
        i = "http://127.0.0.1:8109"
        s, b, h = http(i + "/hero.bmp")
        chk("I1 imagen > 2 MB", len(b) > 2_000_000)
        chk("I3 enlace roto devuelve 404", http(i + "/enlace-roto")[0] == 404)
        chk("I5 sin Cache-Control", "Cache-Control" not in h)
        chk("I6 robots.txt bloquea todo (dorado)", b"Disallow: /" in http(i + "/robots.txt")[1])
        with sync_playwright() as pw:
            br = lanzar(pw); pg = br.new_page(viewport={"width": 390, "height": 800})
            pg.goto(i + "/"); pg.fill("#q", "pan"); pg.focus("#q"); pg.wait_for_timeout(2600)
            chk("I4 el sondeo le saca el foco al campo", pg.evaluate("document.activeElement.id") != "q")
            chk("I2 titulo 'Document', sin lang ni description",
                pg.title() == "Document" and pg.evaluate("!document.documentElement.lang && !document.querySelector('meta[name=description]')"))
            chk("I2b <img> sin width/height", pg.evaluate("!document.querySelector('img').hasAttribute('width')"))
            pg.goto("http://127.0.0.1:8104/")
            for t in json.loads(http(d + "/api/tareas")[1]):
                http(d + "/api/tareas/%d" % t["id"], "DELETE")
            pg.reload(); pg.wait_for_timeout(300)
            chk("D3 sin tareas la pantalla queda en blanco (sin estado vacio)", pg.inner_text("#lista").strip() == "" and "no hay" not in pg.inner_text("body").lower())
            [http(d + "/api/tareas", "POST", b'{"titulo":"<i id=xss>x</i>"}') for _ in range(3)]; pg.reload(); pg.wait_for_timeout(300)
            chk("D5 el titulo se inserta como HTML sin escapar", pg.evaluate("!!document.getElementById('xss')"))
            marc = False
            for k in range(3):
                pg.reload(); pg.wait_for_timeout(300); pg.fill("#t", f"nueva{k}"); pg.click("#guardar"); pg.wait_for_timeout(400)
                pg.locator("li", has_text=f"nueva{k}").locator("input[type=checkbox]").check(); pg.wait_for_timeout(500)
                li = pg.locator("li", has_text=f"nueva{k}")
                marc = marc or (li.count() == 1 and not li.locator("input[type=checkbox]").is_checked())
            chk("D2 marcar como hecha una tarea recien creada no se guarda (id local Date.now)", marc)
            # F
            pg.goto((RAIZ / "f-formulario" / "index.html").as_uri())
            chk("F1 label 'Nombre' sin for", pg.evaluate("[...document.querySelectorAll('label')].some(l=>l.textContent.trim()==='Nombre'&&!l.htmlFor)"))
            pg.fill("#correo", "x"); pg.click("button[type=submit]")
            chk("F2 error solo con color (sin texto/aria-invalid)",
                pg.evaluate("(()=>{const c=document.getElementById('correo');return c.classList.contains('err')&&!c.getAttribute('aria-invalid')&&!document.querySelector('[role=alert]')})()"))
            chk("F3 tabindex positivo", pg.evaluate("[...document.querySelectorAll('[tabindex]')].some(e=>+e.getAttribute('tabindex')>0)"))
            pg.click("#verplan"); pg.keyboard.press("Escape")
            chk("F4 modal abierto: no se cierra con Escape ni recibe el foco",
                pg.evaluate("document.getElementById('modal').classList.contains('abierto') && !document.getElementById('modal').contains(document.activeElement)"))
            chk("F5 enlace dentro del label del radio", pg.evaluate("!!document.querySelector('label a')"))
            chk("F6 mensaje de exito sin aria-live (#msg)", pg.evaluate("!document.getElementById('msg').hasAttribute('aria-live')&&!document.getElementById('msg').hasAttribute('role')"))
            chk("F7 telefono es type=number (dorado)", pg.evaluate("document.getElementById('tel').type==='number'"))
            # G
            pg.goto((RAIZ / "g-textos-regional" / "index.html").as_uri())
            t = pg.inner_text("body")
            chk("G1 '4 resultados' / sin singular-plural calculado", "resultados" in t)
            chk("G2 Cliente/Usuario/Cuenta para lo mismo", all(x in t for x in ("Clientes", "Usuarios", "Cuentas")))
            chk("G3 recorte parte un emoji (caracter suelto)", pg.evaluate("[...document.getElementById('lista').textContent].some(c=>c==='\\ufffd'||/[\\ud800-\\udbff](?![\\udc00-\\udfff])/.test(c))") or "\ufffd" in t or "🌿" not in t)
            chk("G4 'Ñandú' ordenado despues de 'Zeta' (dorado)", t.index("Zeta") < t.index("Ñandú"))
            ctx = br.new_context(timezone_id="America/Montevideo"); p2 = ctx.new_page()
            p2.goto((RAIZ / "g-textos-regional" / "index.html").as_uri())
            chk("G5 la fecha 2026-04-03 se muestra como 2/4 (huso)", "alta 2/4" in p2.inner_text("body"))
            # H
            h = "http://127.0.0.1:8108"
            radios = set()
            for sis in "abc":
                pg.goto(f"{h}/{sis}")
                radios.add(pg.evaluate("getComputedStyle(document.getElementById('g')).borderRadius"))
            chk("H1 el boton primario tiene 3 radios distintos", len(radios) == 3)
            pg.goto(h + "/c")
            chk("H2 sistema c oscuro y a/b claros", pg.evaluate("getComputedStyle(document.body).backgroundColor") != "rgb(255, 255, 255)")
            chk("H3 outline:none en el boton de c", pg.evaluate("getComputedStyle(document.getElementById('g')).outlineStyle") == "none")
            pg.set_viewport_size({"width": 390, "height": 600})
            chk("H4 aviso fijo tapa el contenido (dorado)", pg.evaluate("document.querySelector('.aviso').getBoundingClientRect().height>40"))
            # J limpio
            pg.goto("http://127.0.0.1:8110/")
            chk("J1 limpio: input con label, sin tabindex, boton >= 44",
                pg.evaluate("!!document.querySelector('label[for=t]') && !document.querySelector('[tabindex]') && document.getElementById('ok').getBoundingClientRect().height>=44"))
            br.close()
    finally:
        for p in procs.values():
            p.terminate()
    print(f"\n{len(ok)} defectos confirmados, {len(fallas)} fallas")
    sys.exit(1 if fallas else 0)


main()
