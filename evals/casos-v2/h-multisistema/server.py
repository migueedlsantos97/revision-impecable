"""Caso H: tres sistemas bajo un mismo shell (/a, /b, /c). Uso: python server.py [puerto]"""
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{t}</title>
<style>
:root{{--azul:{azul};--fondo:{fondo};--txt:{txt}}}
body{{margin:0;font:16px system-ui;background:var(--fondo);color:var(--txt)}}
header{{position:sticky;top:0;z-index:5;background:#102a43;color:#fff;padding:12px 16px}}
header a{{color:#fff;margin-right:14px;display:inline-block;min-height:44px;line-height:44px}}
main{{padding:16px;max-width:600px;margin:0 auto}}
.btn{{background:var(--azul);color:#fff;border:0;font-size:16px;{btn}}}
dialog{{border:0;border-radius:10px;padding:20px;z-index:99}}
{extra}
</style></head><body>
<header><a href="/a">Ventas</a><a href="/b">Stock</a><a href="/c">Compras</a></header>
<main><h1>{t}</h1><p>Resumen del sistema.</p>
<button class="btn" id="g">{guardar}</button>
<button class="btn" id="m" style="margin-left:8px;background:#fff;color:#102a43;border:1px solid #102a43">Más</button>
<dialog id="d"><p>Confirmar acción</p><button class="btn" onclick="d.close()">{ok}</button></dialog>
{pie}
<script>g.onclick=()=>d.showModal();</script></main></body></html>"""

SIS = {
    "a": dict(t="Ventas", azul="#0b5cad", fondo="#fff", txt="#1b1b1b", guardar="Guardar", ok="Aceptar",
              btn="min-height:44px;padding:0 16px;border-radius:8px;font-weight:600", extra="", pie=""),
    "b": dict(t="Stock", azul="#0b5cad", fondo="#fff", txt="#1b1b1b", guardar="Guardar cambios", ok="OK",
              btn="min-height:40px;padding:0 20px;border-radius:20px;font-weight:400",
              extra="", pie=""),
    "c": dict(t="Compras", azul="#0f6bd1", fondo="#111", txt="#eee", guardar="Grabar", ok="Aceptar",
              btn="min-height:44px;padding:0 16px;border-radius:2px;font-weight:600;outline:none",
              extra=".aviso{position:fixed;left:0;right:0;bottom:0;background:#333;color:#fff;padding:20px;z-index:50}",
              pie='<div class="aviso">Hay una nueva versión disponible</div>'),
}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        s = SIS.get(self.path.strip("/")[:1] or "a", SIS["a"])
        b = BASE.format(**s).encode()
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", int(sys.argv[1]) if len(sys.argv) > 1 else 8108), H).serve_forever()
