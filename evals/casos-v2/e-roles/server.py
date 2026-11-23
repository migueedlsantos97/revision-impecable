"""Caso E: panel de pedidos con roles. Uso: python server.py [puerto]
Entrar: POST /api/login {"rol":"lector"|"admin","usuario":"ana"|"beto"}"""
import json, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PEDIDOS = {1: {"id": 1, "dueno": "ana", "cliente": "Ana Pérez", "total": 120},
           2: {"id": 2, "dueno": "beto", "cliente": "=HYPERLINK(\"http://x.test\",\"clic\")", "total": 80},
           3: {"id": 3, "dueno": "beto", "cliente": "Beto Gómez", "total": 45}}
USUARIOS = [{"usuario": "ana", "rol": "lector", "clave": "ana123"},
            {"usuario": "beto", "rol": "admin", "clave": "beto123"}]

PAGINA = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Pedidos</title>
<style>body{font:16px system-ui;margin:0 auto;max-width:560px;padding:16px}
button{min-height:44px;padding:0 16px;font-size:16px;border:0;border-radius:8px;background:#0b5cad;color:#fff;margin:4px 4px 4px 0}
li{padding:6px 0}</style></head><body>
<h1>Pedidos</h1>
<div><button id="ana">Entrar como Ana (lector)</button><button id="beto">Entrar como Beto (admin)</button></div>
<p id="quien" role="status">Sin sesión</p>
<ul id="lista"></ul>
<a id="export" href="/api/export.csv">Exportar CSV</a>
<button id="borrar" hidden>Borrar todos (solo admin)</button>
<script>
async function entrar(usuario,rol){
  await fetch('/api/login',{method:'POST',body:JSON.stringify({usuario,rol})});
  document.getElementById('quien').textContent='Sesión: '+usuario+' ('+rol+')';
  document.getElementById('borrar').hidden=rol!=='admin';
  const p=await (await fetch('/api/pedidos')).json();
  document.getElementById('lista').innerHTML=p.map(x=>'<li>#'+x.id+' '+x.cliente+' — '+x.total+'</li>').join('');
}
document.getElementById('ana').onclick=()=>entrar('ana','lector');
document.getElementById('beto').onclick=()=>entrar('beto','admin');
document.getElementById('borrar').onclick=()=>fetch('/api/admin/borrar',{method:'POST'});
</script></body></html>"""


def cookie(h):
    d = {}
    for p in (h.headers.get("Cookie") or "").split(";"):
        if "=" in p:
            k, v = p.strip().split("=", 1); d[k] = v
    return d


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _send(self, code, body, tipo="application/json", extra=()):
        b = body if isinstance(body, bytes) else (body if isinstance(body, str) else json.dumps(body)).encode()
        self.send_response(code); self.send_header("Content-Type", tipo + "; charset=utf-8")
        for k, v in extra: self.send_header(k, v)
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        c = cookie(self)
        if self.path == "/api/pedidos":                       # solo los del usuario: bien
            return self._send(200, [p for p in PEDIDOS.values() if p["dueno"] == c.get("usuario")])
        if self.path.startswith("/api/pedido/"):              # sin chequear de quién es
            p = PEDIDOS.get(int(self.path.rsplit("/", 1)[1]))
            return self._send(200 if p else 404, p or {})
        if self.path == "/api/usuarios":
            if c.get("rol") != "admin":
                return self._send(403, {"error": "solo admin"})
            return self._send(200, USUARIOS)                  # incluye la clave
        if self.path == "/api/export.csv":
            filas = ["id,cliente,total"] + [f'{p["id"]},{p["cliente"]},{p["total"]}' for p in PEDIDOS.values()]
            return self._send(200, "\n".join(filas), "text/csv")
        self._send(200, PAGINA, "text/html")

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        cuerpo = json.loads(self.rfile.read(n) or b"{}")
        if self.path == "/api/login":
            return self._send(200, {"ok": True}, extra=[("Set-Cookie", f"usuario={cuerpo['usuario']}; Path=/"),
                                                         ("Set-Cookie", f"rol={cuerpo['rol']}; Path=/")])
        if self.path == "/api/admin/borrar":                  # no mira el rol
            PEDIDOS.clear()
            return self._send(200, {"ok": True})
        self._send(404, {})


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", int(sys.argv[1]) if len(sys.argv) > 1 else 8105), H).serve_forever()
