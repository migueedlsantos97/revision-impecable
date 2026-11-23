"""Caso I: sitio publico de una panaderia. Uso: python server.py [puerto]"""
import struct, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PAGINA = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Document</title>
<style>body{font:16px system-ui;margin:0 auto;max-width:560px;padding:16px;color:#1b1b1b;background:#fff}
input{min-height:44px;font-size:16px;padding:0 12px;border:1px solid #767676;border-radius:8px;width:100%;box-sizing:border-box}
a{color:#0b5cad}</style></head><body>
<h1>Panadería La Espiga</h1>
<img src="/hero.bmp" alt="Panes recién horneados">
<p>Pan artesanal todos los días. <a href="/enlace-roto">Ver la carta completa</a></p>
<label for="q">Buscar en la carta</label><input id="q" type="search">
<p id="promo"></p>
<script>
let n=0;
setInterval(()=>{
  n++;const q=document.getElementById('q').value;
  document.body.querySelector('#q').outerHTML='<input id="q" type="search" value="'+q+'">';
  document.getElementById('promo').textContent='Promo del día #'+n;
},2000);
</script></body></html>"""


def bmp(w=1000, h=1000):
    fila = (b"\xd8\xa0\x4a" * w)
    datos = fila * h
    cab = b"BM" + struct.pack("<IHHI", 54 + len(datos), 0, 0, 54)
    dib = struct.pack("<IiiHHIIiiII", 40, w, h, 1, 24, 0, len(datos), 2835, 2835, 0, 0)
    return cab + dib + datos


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        if self.path == "/hero.bmp":
            b, t = bmp(), "image/bmp"
        elif self.path == "/robots.txt":
            b, t = b"User-agent: *\nDisallow: /\n", "text/plain"
        elif self.path == "/":
            b, t = PAGINA.encode(), "text/html; charset=utf-8"
        else:
            self.send_response(404); self.send_header("Content-Length", "0"); self.end_headers(); return
        self.send_response(200); self.send_header("Content-Type", t)
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", int(sys.argv[1]) if len(sys.argv) > 1 else 8109), H).serve_forever()
