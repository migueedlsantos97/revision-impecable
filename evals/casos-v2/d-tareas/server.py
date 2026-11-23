"""Caso D: lista de tareas con estado en el servidor. Uso: python server.py [puerto]"""
import json, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TAREAS = [{"id": 1, "titulo": "Llamar al proveedor", "hecha": False},
          {"id": 2, "titulo": "Enviar presupuesto", "hecha": False},
          {"id": 3, "titulo": "Revisar factura", "hecha": True}]
POSTS = {"n": 0}

PAGINA = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Tareas</title>
<style>
body{font:16px system-ui;margin:0;background:#fff;color:#1b1b1b}
main{max-width:560px;margin:0 auto;padding:20px 16px}
form{display:flex;gap:8px}
input[type=text]{flex:1;min-height:44px;padding:0 12px;font-size:16px;border:1px solid #767676;border-radius:8px}
button{min-height:44px;padding:0 16px;font-size:16px;border:0;border-radius:8px;background:#0b5cad;color:#fff}
li{display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid #ddd}
li span{flex:1} li.hecha span{text-decoration:line-through;color:#555}
li button{background:#fff;color:#a40000;border:1px solid #a40000}
#estado{min-height:24px;color:#0a5c2f;margin:8px 0}
</style></head><body><main>
<h1>Tareas</h1>
<form id="f"><label for="t" style="position:absolute;left:-9999px">Nueva tarea</label>
<input type="text" id="t" placeholder="Nueva tarea"><button id="guardar">Agregar</button></form>
<p id="estado" role="status"></p>
<ul id="lista"></ul></main>
<script>
let tareas=[];
const $=s=>document.querySelector(s);
function pintar(){
  $('#lista').innerHTML=tareas.map(t=>`<li class="${t.hecha?'hecha':''}"><input type="checkbox" aria-label="Hecha: ${t.titulo}" ${t.hecha?'checked':''} onchange="marcar(${t.id})"><span>${t.titulo}</span><button onclick="borrar(${t.id})">Borrar</button></li>`).join('');
}
async function cargar(){tareas=await (await fetch('/api/tareas')).json();pintar();}
$('#f').onsubmit=async e=>{
  e.preventDefault();const titulo=$('#t').value.trim();if(!titulo)return;
  tareas.push({id:Date.now(),titulo,hecha:false});pintar();
  $('#estado').textContent='Guardado';
  fetch('/api/tareas',{method:'POST',body:JSON.stringify({titulo})});
  $('#t').value='';
};
async function marcar(id){await fetch('/api/tareas/'+id+'/marcar',{method:'POST'});cargar();}
async function borrar(id){await fetch('/api/tareas/'+id,{method:'DELETE'});cargar();}
cargar();
</script></body></html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _json(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        if self.path == "/api/tareas":
            return self._json(200, TAREAS)
        b = PAGINA.encode()
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        cuerpo = self.rfile.read(n)
        if self.path == "/api/tareas":
            POSTS["n"] += 1
            if POSTS["n"] % 3 == 0:                      # cada tercer guardado falla
                return self._json(500, {"error": "no se pudo guardar"})
            titulo = json.loads(cuerpo or b"{}").get("titulo", "")
            TAREAS.append({"id": len(TAREAS) + 1, "titulo": titulo, "hecha": False})
            return self._json(201, {"ok": True})
        if self.path.endswith("/marcar"):
            i = int(self.path.split("/")[3])
            for t in TAREAS:
                if t["id"] == i:
                    t["hecha"] = not t["hecha"]; break
            return self._json(200, {"ok": True})
        self._json(404, {})

    def do_DELETE(self):
        i = int(self.path.rsplit("/", 1)[1])
        TAREAS[:] = [t for t in TAREAS if t["id"] != i]
        self._json(200, {"ok": True})


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", int(sys.argv[1]) if len(sys.argv) > 1 else 8104), H).serve_forever()
