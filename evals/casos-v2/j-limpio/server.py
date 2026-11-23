"""Caso J (limpio): la misma forma que D, sin defectos sembrados. Uso: python server.py [puerto]"""
import json, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TAREAS = []
SIG = {"n": 1}

PAGINA = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Notas</title><meta name="description" content="Notas simples.">
<style>
:root{--ink:#1b1b1b;--bg:#fff;--brand:#0b5cad;--line:#767676}
@media (prefers-color-scheme:dark){:root{--ink:#eee;--bg:#161616;--brand:#7ab6ff;--line:#9a9a9a}}
body{font:16px system-ui;margin:0;background:var(--bg);color:var(--ink)}
main{max-width:520px;margin:0 auto;padding:20px 16px}
form{display:flex;gap:8px}
input[type=text]{flex:1;min-height:44px;padding:0 12px;font-size:16px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--ink)}
button{min-height:44px;padding:0 16px;font-size:16px;border-radius:8px;border:1px solid var(--brand);background:var(--brand);color:var(--bg)}
button:focus-visible,input:focus-visible{outline:3px solid var(--brand);outline-offset:2px}
li{display:flex;align-items:center;gap:8px;min-height:44px}
li span{flex:1;overflow-wrap:anywhere}
li button{background:transparent;color:var(--ink);border-color:var(--line)}
.vacio{color:var(--ink)}
</style></head><body><main>
<h1>Notas</h1>
<form id="f"><label for="t">Nueva nota</label>
<input type="text" id="t" autocomplete="off"><button type="submit" id="ok">Agregar</button></form>
<p id="estado" role="status"></p>
<ul id="lista"></ul>
<p class="vacio" id="vacio">Todavía no hay notas.</p></main>
<script>
const $=s=>document.querySelector(s);
const esc=s=>s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
async function cargar(){
  const n=await (await fetch('/api/notas')).json();
  $('#lista').innerHTML=n.map(x=>`<li><span>${esc(x.texto)}</span><button data-id="${x.id}">Borrar nota</button></li>`).join('');
  $('#vacio').hidden=n.length>0;
}
$('#f').onsubmit=async e=>{
  e.preventDefault();const texto=$('#t').value.trim();if(!texto)return;
  $('#ok').disabled=true;
  const r=await fetch('/api/notas',{method:'POST',body:JSON.stringify({texto})});
  $('#ok').disabled=false;
  if(r.ok){$('#t').value='';$('#estado').textContent='Nota guardada.';await cargar();}
  else $('#estado').textContent='No se pudo guardar. Probá de nuevo.';
};
$('#lista').onclick=async e=>{const b=e.target.closest('button');if(!b)return;
  await fetch('/api/notas/'+b.dataset.id,{method:'DELETE'});$('#estado').textContent='Nota borrada.';cargar();};
cargar();
</script></body></html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _s(self, code, b, t="application/json"):
        b = b if isinstance(b, bytes) else json.dumps(b).encode()
        self.send_response(code); self.send_header("Content-Type", t + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        if self.path == "/api/notas":
            return self._s(200, TAREAS)
        self._s(200, PAGINA.encode(), "text/html")

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        texto = json.loads(self.rfile.read(n) or b"{}").get("texto", "")[:500]
        TAREAS.append({"id": SIG["n"], "texto": texto}); SIG["n"] += 1   # id que nunca se reutiliza
        self._s(201, {"ok": True})

    def do_DELETE(self):
        i = int(self.path.rsplit("/", 1)[1])
        TAREAS[:] = [t for t in TAREAS if t["id"] != i]
        self._s(200, {"ok": True})


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", int(sys.argv[1]) if len(sys.argv) > 1 else 8110), H).serve_forever()
