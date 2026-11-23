#!/usr/bin/env python3
"""Pruebas de medir.py/medidas.js contra HTML mínimos con un defecto sembrado por chequeo.

  python skill/scripts/tests/run_tests.py

Levanta su propio servidor estático (se apaga por su PID), corre medir.py como lo correría un usuario y compara
informe.json con lo esperado. Sale 1 si algo falla. Necesita playwright + chromium (ver requirements.txt).
"""
import json
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MEDIR = AQUI.parent / "medir.py"
SITIO = AQUI / "sitio"
sys.path.insert(0, str(AQUI.parent))
import medir  # noqa: E402

ESPERADOS = {
    "defectos": {"sin_lang", "sin_viewport", "img_sin_alt", "img_sin_dimensiones", "campo_sin_nombre", "sin_nombre_accesible",
                 "id_duplicado", "aria_roto", "tabindex_positivo", "enlace_falso", "heading_h1", "heading_salto",
                 "texto_cortado_sin_title", "fuente_no_cargo", "tapado", "http_error", "cls_alto", "glifo"},
    "sin_titulo": {"sin_titulo"},
}
resultados = []
sys.stdout.reconfigure(errors="replace")


def check(nombre, ok, detalle=""):
    resultados.append(ok)
    print("%s  %s%s" % ("PASS" if ok else "FAIL", nombre, ("  -> " + detalle) if detalle and not ok else ""))


def puerto_libre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def servidor(puerto, directorio=SITIO):
    p = subprocess.Popen([sys.executable, "-m", "http.server", str(puerto), "--bind", "127.0.0.1", "--directory", str(directorio)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not medir._responde("http://127.0.0.1:%d/" % puerto, espera=10):
        p.kill()
        raise SystemExit("no levantó el servidor de prueba")
    return p


def proyecto(tmp, cfg):
    d = tmp / ".claude" / "revision"
    d.mkdir(parents=True, exist_ok=True)
    ruta = d / "proyecto.json"
    ruta.write_text(json.dumps(cfg), encoding="utf-8")
    return ruta


def correr(args, timeout=240):
    return subprocess.run([sys.executable, str(MEDIR)] + args, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")


def fallas_de(salida):
    return json.loads((Path(salida) / "informe.json").read_text(encoding="utf-8"))["fallas"]


def main():
    puerto = puerto_libre()
    url = "http://127.0.0.1:%d" % puerto
    srv = servidor(puerto)
    try:
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            pantallas = [{"id": n, "ruta": "/%s.html" % n} for n in ("limpio", "defectos", "defectos2", "sin_titulo")]
            cfg = proyecto(tmp, {"nombre": "prueba", "url": url, "pantallas": pantallas, "temas": ["claro"]})
            # 1. Caso A: servidor ya levantado, sin login, sin arranque
            r = correr(["--config", str(cfg), "--rapido", "--salida", str(tmp / "a")])
            check("caso A termina con informe", (tmp / "a" / "informe.json").exists(), r.stderr[-300:])
            f = fallas_de(tmp / "a")
            por = lambda p: {h["tipo"] for h in f if h["pantalla"] == p}  # noqa: E731
            check("limpio no dispara nada", not por("limpio"), str(sorted(por("limpio"))))
            for pan, tipos in ESPERADOS.items():
                faltan = tipos - por(pan)
                check("%s dispara todos sus defectos" % pan, not faltan, "no disparó: %s" % sorted(faltan))
            check("titulo_duplicado entre defectos y defectos2", any(h["tipo"] == "titulo_duplicado" for h in f))
            check("http_error trae la URL del recurso", any(h["tipo"] == "http_error" and "/nope.png" in h["selector"] for h in f))
            check("no cuenta el favicon", not any("favicon" in h["selector"] for h in f))
            check("falla tiene certeza", all(h.get("certeza") in ("medida", "sospecha") for h in f))
            check("sin sesiones en la salida", not list((tmp / "a").glob("sesion-*")))

            # 2. desactivar tipos desde el config
            cfg2 = proyecto(tmp, {"nombre": "p", "url": url, "pantallas": pantallas[:2], "temas": ["claro"], "umbrales": {"desactivar": ["cls_alto", "tapado"]}})
            correr(["--config", str(cfg2), "--rapido", "--salida", str(tmp / "d")])
            tp = {h["tipo"] for h in fallas_de(tmp / "d")}
            check("umbrales.desactivar apaga tipos", "cls_alto" not in tp and "tapado" not in tp and "sin_lang" in tp)

            # 3. login que falla -> sin_sesion y se salta la pantalla
            cfg3 = proyecto(tmp, {"nombre": "p", "url": url, "temas": ["claro"], "login": {"tipo": "api", "ruta": "/api/login", "roles": {"a/b": {"u": "x"}}},
                                  "pantallas": [{"id": "limpio", "ruta": "/limpio.html", "rol": "a/b"}]})
            correr(["--config", str(cfg3), "--rapido", "--salida", str(tmp / "s")])
            tp = {h["tipo"] for h in fallas_de(tmp / "s")}
            check("login fallido => sin_sesion (y no mide)", tp == {"sin_sesion"}, str(tp))

            # 4. Caso B: arranque.comando; se apaga solo y el informe se escribe
            p2 = puerto_libre()
            cfg4 = proyecto(tmp, {"nombre": "p", "url": "http://127.0.0.1:%d" % p2, "temas": ["claro"], "pantallas": pantallas[:1],
                                  "arranque": {"comando": "%s -m http.server %d --bind 127.0.0.1" % (Path(sys.executable).name if False else '"%s"' % sys.executable, p2), "cwd": str(SITIO), "espera": 20}})
            r = correr(["--config", str(cfg4), "--rapido", "--salida", str(tmp / "b")])
            check("caso B escribe informe (apagado sin error)", (tmp / "b" / "informe.json").exists() and "Traceback" not in r.stderr, r.stderr[-300:])
            time.sleep(1)
            check("caso B no deja el servidor vivo", not medir._responde("http://127.0.0.1:%d/" % p2))

            # 5. el proceso muere al arrancar: falla rápido, no espera el plazo
            cfg5 = proyecto(tmp, {"nombre": "p", "url": "http://127.0.0.1:%d" % puerto_libre(), "pantallas": pantallas[:1],
                                  "arranque": {"comando": '"%s" -c "raise SystemExit(1)"' % sys.executable, "espera": 60}})
            t0 = time.time()
            r = correr(["--config", str(cfg5), "--rapido", "--salida", str(tmp / "m")])
            check("proceso muerto => aborta rápido con mensaje", time.time() - t0 < 25 and r.returncode != 0 and "instancia" in (r.stderr + r.stdout).lower(), (r.stderr + r.stdout)[-200:])

            # 6. _responde: un 404 en "/" es una app viva
            check("_responde(404) es True", medir._responde(url + "/no-existe-nada"))

            # 7. descubrir
            cfg7 = tmp / "descubierto.json"
            r = correr(["--descubrir", "--url", url, "--config", str(cfg7), "--max-paginas", "20", "--profundidad", "2"])
            rutas = [p["ruta"] for p in json.loads(cfg7.read_text(encoding="utf-8"))["pantallas"]] if cfg7.exists() else []
            items = [x for x in rutas if x.startswith("/item/")]
            check("descubrir encuentra las pantallas", {"/", "/limpio.html", "/defectos.html"} <= set(rutas), str(rutas) + r.stderr[-200:])
            check("descubrir colapsa plantillas (max 2 ejemplos)", len(items) == 2, str(items))
            check("descubrir nunca visita salir/eliminar/archivos/externos", not any(k in x for x in rutas for k in ("salir", "eliminar", ".pdf", "example")), str(rutas))

            # 8. gobierno: validar, límites, chequeos del proyecto, baseline, silenciamientos, alcance, estado, presupuesto, promover
            import pruebas_gobierno
            pruebas_gobierno.ejecutar(sys.modules[__name__], url, tmp)
    finally:
        srv.terminate()
        try:
            srv.wait(10)
        except subprocess.TimeoutExpired:
            srv.kill()
    print("\n%d/%d pruebas pasan" % (sum(resultados), len(resultados)))
    return 0 if all(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
