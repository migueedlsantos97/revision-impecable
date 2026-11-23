# scripts

- `medir.py` mide pantallas con Playwright; `medidas.js` es lo que inyecta en la página.
- Instalar: `python -m pip install -r requirements.txt && python -m playwright install chromium`
- Medir: `python medir.py --config .claude/revision/proyecto.json [--rapido] [--url URL] [--motores chromium,firefox,webkit]`
- Descubrir pantallas sin config: `python medir.py --descubrir --url http://127.0.0.1:8000 [--rol admin] [--max-paginas 40] [--profundidad 2]`
  escribe un `proyecto.json` candidato (o `.candidato.json` si ya existe uno). Solo sigue enlaces; no hace clic en botones ni visita rutas de salir/borrar.
- Probar los chequeos: `python tests/run_tests.py` (HTML con un defecto sembrado por chequeo + uno limpio que no debe disparar nada).
- Cada falla trae `certeza`: `medida` (hecho) o `sospecha` (mirar con criterio). Se apagan tipos con `umbrales.desactivar`.
