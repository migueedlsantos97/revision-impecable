"""Pruebas de validar, límites, chequeos del proyecto, baseline, silenciamientos, métricas, alcance, estado, presupuesto y promover.
Las llama run_tests.py (comparten check/correr/servidor)."""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent


def scr(nombre, args, cwd=None, timeout=300):
    return subprocess.run([sys.executable, str(SCRIPTS / nombre)] + [str(x) for x in args], capture_output=True, text=True,
                          timeout=timeout, encoding="utf-8", errors="replace", cwd=cwd)


def salida(r):
    return r.stdout + r.stderr


def informe(d):
    return json.loads((Path(d) / "informe.json").read_text(encoding="utf-8"))


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise RuntimeError("git %s: %s" % (args, r.stderr))
    return r.stdout.strip()


def escribir(ruta, texto):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto, encoding="utf-8", newline="\n")


def ejecutar(h, url, tmp):
    check, correr, proyecto = h.check, h.correr, h.proyecto
    py = '"%s"' % sys.executable
    clima = {"temas": ["claro"], "anchos": [1366]}
    limpio = [{"id": "limpio", "ruta": "/limpio.html"}]

    # --- 1. validar ---
    cfg = proyecto(tmp, {"nombre": "v", "url": url, "doctor": py + ' -c "pass"', "autonomia": "acompanado", "vueltas": 3,
                         "presupuesto": {"tokens": 1000, "minutos": 30, "vueltas": 3}, "limites": {"max_minutos": 10, "max_capturas": 50},
                         "pantallas": limpio, **clima})
    r = correr(["--config", str(cfg), "--validar"])
    check("validar: adaptador sano => exit 0", r.returncode == 0 and "El adaptador sirve" in r.stdout and "OK     doctor" in r.stdout, salida(r)[-300:])
    check("validar muestra autonomia, presupuesto y limites", "autonomia=acompanado" in r.stdout and "'tokens': 1000" in r.stdout and "max_capturas" in r.stdout)
    cfg = proyecto(tmp, {"nombre": "v", "url": url, "autonomia": "x", "limites": {"max_minutos": "5"}, "presupuesto": {"tokens": -1}, "vueltas": 0,
                         "umbrales": {"tactil": "grande"}, "pantallas": limpio})
    r = correr(["--config", str(cfg), "--validar"])
    o = salida(r)
    check("validar: tipos mal => exit 2 con cada error", r.returncode == 2 and all(k in o for k in ("autonomia", "limites.max_minutos", "presupuesto.tokens", "vueltas", "umbrales.tactil")), o[-300:])
    check("medir con adaptador inválido no corre", correr(["--config", str(cfg), "--rapido"]).returncode != 0)
    cfg = proyecto(tmp, {"nombre": "v", "url": url, "doctor": py + ' -c "raise SystemExit(3)"', "pantallas": limpio})
    r = correr(["--config", str(cfg), "--validar"])
    check("validar: doctor que falla => exit 1 accionable", r.returncode == 1 and "FALLA  doctor (exit 3)" in r.stdout, salida(r)[-300:])
    cfg = proyecto(tmp, {"nombre": "v", "url": url, "login": {"tipo": "api", "ruta": "/api/login", "roles": {"admin": {"u": "x"}}},
                         "pantallas": [{"id": "limpio", "ruta": "/limpio.html", "rol": "admin"}]})
    r = correr(["--config", str(cfg), "--validar"])
    check("validar: login que falla => exit 1", r.returncode == 1 and "FALLA  login como admin" in r.stdout, salida(r)[-300:])

    # --- 2. limites ---
    paginas = [{"id": "l%d" % i, "ruta": "/limpio.html"} for i in range(4)]
    cfg = proyecto(tmp, {"nombre": "l", "url": url, "pantallas": paginas, "limites": {"max_capturas": 2}, **clima})
    correr(["--config", str(cfg), "--salida", str(tmp / "lim1")])
    inf = informe(tmp / "lim1")
    check("limites.max_capturas corta y lo dice", inf["completo"] is False and inf["capturas"] == 2 and any(f["tipo"] == "limite_alcanzado" for f in inf["fallas"]),
          str(inf["capturas"]) + str(inf["por_tipo"]))
    cfg = proyecto(tmp, {"nombre": "l", "url": url, "pantallas": paginas, "limites": {"max_minutos": 0.0001}, **clima})
    correr(["--config", str(cfg), "--salida", str(tmp / "lim2")])
    check("limites.max_minutos corta", informe(tmp / "lim2")["completo"] is False)

    # --- 3. chequeos del proyecto ---
    chq = tmp / "chequeos"
    escribir(chq / "h1-limpio.js", "module.exports = { id: 'h1-limpio', certeza: 'medida', chequear() { const h = document.querySelector('h1'); return h && /limpia/.test(h.textContent) ? [{ selector: 'h1', detalle: 'dice limpia' }] : []; } };\n")
    escribir(chq / "roto.js", "module.exports = { id: 'roto', chequear() { throw new Error('boom'); } };\n")
    escribir(chq / "sincontrato.js", "module.exports = { chequear() { return []; } };\n")
    escribir(chq / "sintaxis.js", "esto no es javascript (\n")
    escribir(chq / "pyok.py", "def chequear(page, pantalla):\n    return [{'tipo': 'py_tipo', 'certeza': 'sospecha', 'selector': 'body', 'detalle': 'titulo ' + page.title() + ' en ' + pantalla['id']}]\n")
    escribir(chq / "pyroto.py", "def chequear(page, pantalla):\n    raise RuntimeError('py boom')\n")
    escribir(chq / "pymal.py", "x = 1\n")
    cfg = proyecto(tmp, {"nombre": "c", "url": url, "pantallas": limpio, **clima})
    r = correr(["--config", str(cfg), "--chequeos", str(chq), "--salida", str(tmp / "chq")])
    f = informe(tmp / "chq")["fallas"]
    prop = [x for x in f if x.get("origen") == "proyecto"]
    roto = {x["selector"] for x in f if x["tipo"] == "chequeo_roto"}
    check("chequeo js entra al informe con origen proyecto y su certeza", any(x["tipo"] == "proyecto_h1-limpio" and x["certeza"] == "medida" for x in prop), str(f))
    check("chequeo py entra al informe", any(x["tipo"] == "py_tipo" and x["certeza"] == "sospecha" and "Limpio en limpio" in x["detalle"] for x in prop), str(prop))
    check("chequeos rotos => chequeo_roto sin tumbar la corrida", roto == {"roto.js", "sincontrato.js", "sintaxis.js", "pyroto.py", "pymal.py"} and r.returncode == 1, str(roto))
    check("los chequeos del proyecto no ensucian lo nativo", all(x.get("origen") == "proyecto" for x in f), str([x["tipo"] for x in f if x.get("origen") != "proyecto"]))
    shutil.copytree(chq, tmp / ".claude" / "revision" / "chequeos", dirs_exist_ok=True)
    correr(["--config", str(cfg), "--salida", str(tmp / "chq2")])
    check("carpeta .claude/revision/chequeos/ se usa por defecto", any(x["tipo"] == "proyecto_h1-limpio" for x in informe(tmp / "chq2")["fallas"]))
    shutil.rmtree(tmp / ".claude" / "revision" / "chequeos")

    # --- 4. silenciamientos ---
    cfg = proyecto(tmp, {"nombre": "s", "url": url, "pantallas": [{"id": "sil", "ruta": "/silenciado.html"}, {"id": "st", "ruta": "/sin_titulo.html"}],
                         "umbrales": {"desactivar": ["sin_titulo"]}, **clima})
    r = correr(["--config", str(cfg), "--salida", str(tmp / "sil")])
    inf = informe(tmp / "sil")
    s = inf["silenciamientos"]
    md = (tmp / "sil" / "informe.md").read_text(encoding="utf-8")
    check("silenciamientos: cuenta data-revision-ok y desactivar", s["total"] == 2 and s["data_revision_ok"] == {"tactil": 1} and s["umbrales_desactivar"] == {"sin_titulo": 1}, str(s))
    check("informe.md lista «Silenciamientos: 2»", "## Silenciamientos: 2" in md and "umbrales.desactivar" in md and r.returncode == 0, md[-400:])

    # --- 5. métricas ---
    filas = json.loads((tmp / ".claude" / "revision" / "metricas.json").read_text(encoding="utf-8"))
    claves = {"fecha", "pantallas_en_mapa", "hallazgos_cajon1", "cajon2", "chequeos_propios", "minutos"}
    check("metricas.json acumula una fila por corrida", len(filas) >= 5 and all(set(x) == claves for x in filas), str(filas[-1:]))

    # --- 6. baseline visual ---
    sitio2 = tmp / "sitio2"
    sitio2.mkdir()
    shutil.copy(h.SITIO / "limpio.html", sitio2 / "p.html")
    p2 = h.puerto_libre()
    srv2 = h.servidor(p2, sitio2)
    try:
        url2 = "http://127.0.0.1:%d" % p2
        cfg = proyecto(tmp, {"nombre": "b", "url": url2, "pantallas": [{"id": "p", "ruta": "/p.html"}], **clima})
        base = ["--config", str(cfg), "--baseline"]
        r = correr(base + ["--salida", str(tmp / "b1")])
        ref = tmp / ".claude" / "revision" / "baseline" / "p-1366-claro.png"
        check("baseline: primera corrida crea la referencia", ref.exists() and informe(tmp / "b1")["baseline"].get("creadas") == 1 and r.returncode == 0, salida(r)[-200:])
        r = correr(base + ["--salida", str(tmp / "b2")])
        check("baseline: sin cambios no hay regresion", informe(tmp / "b2")["baseline"].get("comparadas") == 1 and r.returncode == 0, str(informe(tmp / "b2")["por_tipo"]))
        html = (sitio2 / "p.html").read_text(encoding="utf-8")
        (sitio2 / "p.html").write_text(html.replace("background: #fff", "background: #ddd"), encoding="utf-8")
        r = correr(base + ["--salida", str(tmp / "b3")])
        reg = [x for x in informe(tmp / "b3")["fallas"] if x["tipo"] == "regresion_visual"]
        check("baseline: cambio visual => regresion_visual (sospecha) con diff", len(reg) == 1 and reg[0]["certeza"] == "sospecha" and (tmp / "b3" / "diffs" / "p-1366-claro-diff.png").exists(), str(reg))
        (sitio2 / "p.html").write_text(html.replace("<h1>", "<div style='height:1500px'></div><h1>"), encoding="utf-8")
        r = correr(base + ["--salida", str(tmp / "b3b")])
        reg = [x for x in informe(tmp / "b3b")["fallas"] if x["tipo"] == "regresion_visual"]
        check("baseline: cambio de tamaño también es regresion", len(reg) == 1 and "tamaño" in reg[0]["detalle"], str(reg))
        (sitio2 / "p.html").write_text(html.replace("background: #fff", "background: #ddd"), encoding="utf-8")
        r = correr(base + ["--aprobar-baseline", "--pantalla", "p", "--salida", str(tmp / "b4")])
        check("aprobar-baseline sin --motivo se niega", r.returncode != 0 and "--motivo" in salida(r) and not (tmp / ".claude" / "revision" / "baseline" / "CAMBIOS.tsv").exists(), salida(r)[-200:])
        r = correr(base + ["--aprobar-baseline", "--motivo", "fondo gris a propósito", "--salida", str(tmp / "b5")])
        check("aprobar-baseline sin --pantalla se niega", r.returncode != 0 and "--pantalla" in salida(r))
        r = correr(base + ["--aprobar-baseline", "--pantalla", "p", "--motivo", "fondo gris a propósito", "--salida", str(tmp / "b6")])
        tsv = tmp / ".claude" / "revision" / "baseline" / "CAMBIOS.tsv"
        check("aprobar-baseline regenera y anota el motivo", r.returncode == 0 and tsv.exists() and "fondo gris a propósito" in tsv.read_text(encoding="utf-8"), salida(r)[-200:])
        r = correr(base + ["--salida", str(tmp / "b7")])
        check("baseline: tras aprobar vuelve a pasar", r.returncode == 0 and not any(x["tipo"] == "regresion_visual" for x in informe(tmp / "b7")["fallas"]))
    finally:
        srv2.terminate()
        try:
            srv2.wait(10)
        except subprocess.TimeoutExpired:
            srv2.kill()

    # --- 7. alcance + estado en un repo git temporal ---
    repo = tmp / "repo"
    for f, t in (("apps/a/f.txt", "a"), ("apps/b/f.txt", "b"), ("apps/c/f.txt", "c"), ("shared/x.css", "x"), ("core/y.js", "y"), ("lib/z.js", "z"), (".gitignore", ".claude/revision/salida/\n.claude/revision/alcance.json\n")):
        escribir(repo / f, t + "\n")
    pantallas = [{"id": "A1", "sistema": "a", "ruta": "/limpio.html"}, {"id": "A2", "sistema": "a", "ruta": "/limpio.html"},
                 {"id": "B1", "sistema": "b", "ruta": "/limpio.html"}, {"id": "C1", "sistema": "c", "ruta": "/defectos.html"}]
    cfg = proyecto(repo, {"nombre": "r", "url": url, "pantallas": pantallas, **clima})
    escribir(repo / ".claude/revision/dependencias.json", json.dumps({
        "sistemas": {"a": {"propios": ["apps/a/**"], "consume": ["lib/**"]}, "b": {"propios": ["apps/b/**"]}, "c": {"propios": ["apps/c/**"]}},
        "compartido": {"shared/**": {"afecta": ["a"]}, "core/**": {"afecta": "*"}},
        "pantallas": {"a": ["A1", "A2"], "b": ["B1"], "c": ["C1"]}, "vigencia_dias": 90}))
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "t")
    git(repo, "config", "core.autocrlf", "false")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    base_sha = git(repo, "rev-parse", "HEAD")
    al = repo / ".claude/revision/alcance.json"

    def alcance():
        r = scr("alcance.py", ["--raiz", repo])
        return json.loads(al.read_text(encoding="utf-8")), r

    a, r = alcance()
    check("alcance: sin estado => todo completo y sin sondas", a["revisar"] == ["A1", "A2", "B1", "C1"] and a["sondas"] == [] and a["motivo"]["a"] == ["sin estado"], str(a))
    correr(["--config", str(cfg), "--url", url])
    for s in ("a", "b"):
        r = scr("estado.py", ["escribir", "--raiz", repo, "--sistema", s, "--sha", "HEAD"])
        check("estado escribir %s (sin fallas medidas)" % s, r.returncode == 0 and "verificado" in r.stdout, salida(r)[-300:])
    ea = json.loads((repo / ".claude/revision/estado/a.json").read_text(encoding="utf-8"))
    check("estado.json tiene el formato", ea["verificado_en"] == base_sha and ea["estado"] == "verificado" and set(ea["pantallas"]) == {"A1@1366@claro", "A2@1366@claro"}
          and ea["archivos"]["apps/a/**"] and set(ea) >= {"fecha", "funciones", "tests", "umbrales_hash"}, str(ea)[:300])
    r = scr("estado.py", ["escribir", "--raiz", repo, "--sistema", "c", "--sha", "HEAD"])
    check("estado se niega si hay fallas medidas", r.returncode == 1 and "falla(s) medida(s)" in r.stdout and not (repo / ".claude/revision/estado/c.json").exists(), salida(r)[-300:])
    r = scr("estado.py", ["escribir", "--raiz", repo, "--sistema", "c", "--sha", "HEAD", "--parcial"])
    check("estado --parcial escribe como parcial", r.returncode == 0 and json.loads((repo / ".claude/revision/estado/c.json").read_text(encoding="utf-8"))["estado"] == "parcial")
    r = scr("estado.py", ["ver", "--raiz", repo])
    check("estado ver imprime la tabla", r.returncode == 0 and "verificado" in r.stdout and "parcial" in r.stdout, r.stdout)

    a, r = alcance()
    check("alcance: lo verificado queda vigente (parcial se revisa) y hay sondas", a["revisar"] == ["C1"] and [v["sistema"] for v in a["vigentes"]] == ["a", "b"] and a["sondas"] == ["A1", "B1"], str(a))

    def tras_cambio(archivo, texto="cambio\n", commit=True):
        escribir(repo / archivo, texto)
        if commit:
            git(repo, "add", "--", "apps", "shared", "core", "lib")
            git(repo, "commit", "-q", "-m", "cambio")
        return alcance()[0]

    def volver():
        git(repo, "reset", "-q", "--hard", base_sha)
        (repo / "apps/b/nuevo.txt").unlink(missing_ok=True)

    a = tras_cambio("apps/a/f.txt")
    check("archivo propio tocado => ese sistema completo", a["revisar"] == ["A1", "A2", "C1"] and "propio: apps/a/f.txt" in a["motivo"]["a"] and a["sondas"] == ["B1"], str(a))
    r = correr(["--config", str(cfg), "--url", url, "--alcance", str(al), "--salida", str(tmp / "repo-m2")])
    ids = {m["id"] for m in informe(tmp / "repo-m2")["pantallas_medidas"]}
    check("medir --alcance mide solo revisar + sondas", ids == {"A1", "A2", "C1", "B1"}, str(ids))
    volver()
    a = tras_cambio("shared/x.css")
    check("compartido con afecta=[a] => solo a", "a" in a["motivo"] and "b" not in a["motivo"], str(a["motivo"]))
    volver()
    a = tras_cambio("core/y.js")
    check("compartido con afecta=* => todos", set(a["motivo"]) == {"a", "b", "c"}, str(a["motivo"]))
    volver()
    a = tras_cambio("lib/z.js")
    check("archivo que consume => ese sistema", "a" in a["motivo"] and "b" not in a["motivo"], str(a["motivo"]))
    volver()
    a = tras_cambio("apps/b/nuevo.txt", commit=False)
    check("archivo nuevo sin commit cuenta", "b" in a["motivo"] and "a" not in a["motivo"], str(a["motivo"]))
    volver()
    cfgj = json.loads(cfg.read_text(encoding="utf-8"))
    cfgj["umbrales"] = {"tactil": 40}
    cfg.write_text(json.dumps(cfgj), encoding="utf-8")
    a, _ = alcance()
    check("cambió proyecto.json => todos vencen", set(a["motivo"]) == {"a", "b", "c"} and any("proyecto.json" in x for x in a["motivo"]["b"]), str(a["motivo"]))
    git(repo, "checkout", "-q", "--", ".claude/revision/proyecto.json")
    ej = repo / ".claude/revision/estado/b.json"
    e = json.loads(ej.read_text(encoding="utf-8"))
    e["fecha"] = "2020-01-01T00:00:00"
    ej.write_text(json.dumps(e), encoding="utf-8")
    a, _ = alcance()
    check("estado con más de vigencia_dias => vence", "b" in a["motivo"] and "a" not in a["motivo"] and any("vigencia" in x for x in a["motivo"]["b"]), str(a["motivo"]))

    # --- 8. presupuesto ---
    raiz = tmp / "pres"
    proyecto(raiz, {"nombre": "p", "url": url, "vueltas": 5, "presupuesto": {"tokens": 1000, "minutos": 100, "vueltas": 5}, "pantallas": limpio})

    def pres(*args, salida_dir):
        return scr("presupuesto.py", ["--raiz", raiz, "--salida", salida_dir, *args])

    d1 = raiz / "salida1"
    r = pres("iniciar", salida_dir=d1)
    cp = json.loads((d1 / "checkpoint.json").read_text(encoding="utf-8"))
    check("presupuesto iniciar crea checkpoint.json", r.returncode == 0 and {"fase", "vuelta", "abiertos", "commits", "ultimo_medir_ok", "proximo_paso", "tokens", "minutos", "estado"} <= set(cp) and cp["estado"] == "running", r.stdout)
    r = pres("decidir", salida_dir=d1)
    check("decidir => seguir", r.stdout.split()[0] == "seguir" and r.returncode == 0, r.stdout)
    pres("anotar", "--tokens", "800", "--fase", "arreglar", "--proximo", "arreglar tactil en el componente", salida_dir=d1)
    r = pres("decidir", salida_dir=d1)
    check("queda < 25 % => degradar", r.stdout.split()[0] == "degradar", r.stdout)
    pres("anotar", "--tokens", "150", salida_dir=d1)
    r = pres("decidir", salida_dir=d1)
    check("queda < 10 % => parar (exit 10, estado paused)", r.stdout.split()[0] == "parar" and r.returncode == 10 and json.loads((d1 / "checkpoint.json").read_text(encoding="utf-8"))["estado"] == "paused", r.stdout)
    r = pres("reanudar", salida_dir=d1)
    check("reanudar dice por dónde seguir", "SEGUÍ POR: arreglar tactil en el componente" in r.stdout and "fase: arreglar" in r.stdout, r.stdout)
    d2 = raiz / "salida2"
    pres("iniciar", salida_dir=d2)
    for v, m in ((1, 10), (2, 10), (3, 11)):
        pres("anotar", "--vuelta", str(v), "--medidos", str(m), salida_dir=d2)
    r = pres("decidir", salida_dir=d2)
    check("2 vueltas sin bajar => pivotar", r.stdout.split()[0] == "pivotar", r.stdout)
    r = pres("decidir", salida_dir=d2)
    check("después de pivotar vuelve a seguir", r.stdout.split()[0] == "seguir", r.stdout)
    for v, m in ((4, 12), (5, 13)):
        pres("anotar", "--vuelta", str(v), "--medidos", str(m), salida_dir=d2)
    r = pres("decidir", salida_dir=d2)
    check("estancado otra vez => parar (aborted)", r.stdout.split()[0] == "parar" and r.returncode == 10 and json.loads((d2 / "checkpoint.json").read_text(encoding="utf-8"))["estado"] == "aborted", r.stdout)

    # --- 9. promover ---
    cand = tmp / "cand"
    bueno = ("---\nid: foco-en-contenedor\nregla_1_linea: El foco de un input escondido se ve en su caja, no en el input.\n"
             "causa_tecnica: El input tiene opacity 0 y el anillo lo dibuja el contenedor con :has(:focus-visible).\nproyectos_que_lo_vieron: 3\n---\n"
             "## Caso mínimo\n\n```html\n<label><input type=\"checkbox\" style=\"opacity:0\"> Opción</label>\n```\n")
    escribir(cand / "bueno.md", bueno)
    r = scr("promover.py", [cand / "bueno.md", "--nombre", "AcmeCorp"])
    check("promover: candidato limpio => OK y borrador de PR", r.returncode == 0 and "BORRADOR DE PR" in r.stdout and "tests/sitio/foco-en-contenedor.html" in r.stdout, salida(r)[-300:])
    sucios = {
        "email": (bueno.replace("Opción", "escribir a ana@acme.com"), "email"),
        "ruta": (bueno.replace("Opción", r"C:\Users\ana\proyecto"), "ruta de usuario"),
        "url": (bueno.replace("Opción", "https://intranet.acme.com/x"), "URL"),
        "cifra": (bueno.replace("Opción", "pedido 123456"), "cifra"),
        "nombre": (bueno.replace("Opción", "sistema AcmeCorp"), "lista negra"),
        "largo": (bueno.replace("<label>", "\n".join("<p>%d</p>" % i for i in range(31)) + "\n<label>"), "líneas"),
        "sin_frontmatter": (bueno.split("---\n", 2)[2], "frontmatter"),
        "sin_causa": (bueno.replace("causa_tecnica:", "otra:"), "causa_tecnica"),
    }
    for nombre, (txt, esperado) in sucios.items():
        escribir(cand / (nombre + ".md"), txt)
        r = scr("promover.py", [cand / (nombre + ".md"), "--nombre", "AcmeCorp"])
        check("promover rechaza: %s" % nombre, r.returncode == 1 and esperado in r.stdout, r.stdout[-200:])
    escribir(cand / "negra.txt", "# clientes\nPepito SA\n")
    escribir(cand / "lista.md", bueno.replace("Opción", "cliente Pepito SA"))
    r = scr("promover.py", [cand / "lista.md", "--lista-negra", cand / "negra.txt"])
    check("promover usa --lista-negra de archivo", r.returncode == 1 and "Pepito SA" in r.stdout, r.stdout[-200:])
