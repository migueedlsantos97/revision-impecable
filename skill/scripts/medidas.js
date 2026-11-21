(u) => {
  // Se inyecta en la página. Recibe umbrales y devuelve {fallas: [{tipo, selector, detalle}], componentes: [...], tema: {...}}.
  const fallas = [];
  const cs = (e) => getComputedStyle(e);
  const SALTAR = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'HEAD', 'TITLE', 'META', 'LINK', 'OPTION', 'OPTGROUP', 'TEMPLATE']);
  const ok = (e, marca) => !!e.closest('[data-revision-ok~="' + marca + '"],[data-revision-ok="todo"]');

  const selector = (e) => {
    const partes = [];
    for (let n = e, d = 0; n && n.nodeType === 1 && d < 4; n = n.parentElement, d++) {
      let p = n.tagName.toLowerCase();
      if (n.id) { partes.unshift(p + '#' + n.id); break; }
      const cl = [...n.classList].filter((c) => !/[:[\]/]/.test(c)).slice(0, 2).join('.');
      if (cl) p += '.' + cl;
      const hermanos = n.parentElement ? [...n.parentElement.children].filter((x) => x.tagName === n.tagName) : [];
      if (hermanos.length > 1) p += ':nth-of-type(' + (hermanos.indexOf(n) + 1) + ')';
      partes.unshift(p);
    }
    return partes.join(' > ');
  };

  // why: lo que el scroll o un contenedor recortan no se ve; medirlo da falsos solapes y falsos contrastes
  const rectVisible = (e) => {
    const s = cs(e);
    if (s.display === 'none' || s.visibility === 'hidden' || parseFloat(s.opacity) === 0) return null;
    const b = e.getBoundingClientRect();
    let r = { l: b.left, t: b.top, r: b.right, b: b.bottom };
    for (let a = e.parentElement; a && a !== document.documentElement; a = a.parentElement) {
      const sa = cs(a);
      if (sa.display === 'none' || parseFloat(sa.opacity) === 0 || sa.visibility === 'hidden') return null;
      if (/(hidden|auto|scroll|clip)/.test(sa.overflowX + sa.overflowY)) {
        const c = a.getBoundingClientRect();
        r = { l: Math.max(r.l, c.left), t: Math.max(r.t, c.top), r: Math.min(r.r, c.right), b: Math.min(r.b, c.bottom) };
      }
    }
    if (r.r - r.l <= 1 || r.b - r.t <= 1) return null;
    return r;
  };

  const rectTexto = (e) => {
    let q2 = null;
    for (const n of e.childNodes) {
      if (n.nodeType !== 3 || !n.textContent.trim()) continue;
      const g = document.createRange();
      g.selectNodeContents(n);
      for (const q of g.getClientRects()) {
        if (q.width <= 0 || q.height <= 0) continue;
        q2 = q2 ? { l: Math.min(q2.l, q.left), t: Math.min(q2.t, q.top), r: Math.max(q2.r, q.right), b: Math.max(q2.b, q.bottom) } : { l: q.left, t: q.top, r: q.right, b: q.bottom };
      }
    }
    return q2;
  };

  const cv = document.createElement('canvas');
  cv.width = cv.height = 1;
  const cx = cv.getContext('2d', { willReadFrequently: true });
  const rgba = (c) => {
    cx.clearRect(0, 0, 1, 1);
    cx.fillStyle = '#000';
    cx.fillStyle = c;
    cx.fillRect(0, 0, 1, 1);
    const d = cx.getImageData(0, 0, 1, 1).data;
    return [d[0], d[1], d[2], d[3] / 255];
  };
  const mezcla = (f, b) => [0, 1, 2].map((i) => f[i] * f[3] + b[i] * (1 - f[3]));
  const lum = (c) => {
    const l = c.map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); });
    return 0.2126 * l[0] + 0.7152 * l[1] + 0.0722 * l[2];
  };
  const razon = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  // why: el fondo real es el de la tarjeta, no el de la página; con imagen o degradado no se puede calcular
  const fondo = (e) => {
    const capas = [];
    for (let n = e; n; n = n.parentElement) {
      const s = cs(n);
      if (s.backgroundImage !== 'none') return null;
      const c = rgba(s.backgroundColor);
      if (c[3] > 0) { capas.push(c); if (c[3] >= 1) break; }
    }
    let base = [255, 255, 255];
    for (let i = capas.length - 1; i >= 0; i--) base = mezcla(capas[i], base);
    return base;
  };
  const hex = (c) => '#' + c.slice(0, 3).map((v) => Math.round(v).toString(16).padStart(2, '0')).join('');

  const INTERACTIVO = 'a[href],button,input:not([type=hidden]),select,textarea,summary,[role=button],[role=tab],[role=link],[role=menuitem],[role=option],[role=checkbox],[role=switch],[onclick],[tabindex]:not([tabindex="-1"])';
  const interactivos = [];
  document.querySelectorAll(INTERACTIVO).forEach((e) => { const r = rectVisible(e); if (r) interactivos.push({ e, r }); });

  const textuales = [];
  document.body.querySelectorAll('*').forEach((e) => {
    if (SALTAR.has(e.tagName) || e.closest('svg')) return;
    const rt = rectTexto(e);
    if (!rt || !rectVisible(e)) return;
    textuales.push({ e, r: rt });
  });

  // 1. desborde horizontal de la página y bloques más anchos que la pantalla
  const de = document.documentElement;
  if (de.scrollWidth > de.clientWidth + 1) {
    let culpable = '';
    for (const e of document.body.querySelectorAll('*')) {
      const b = e.getBoundingClientRect();
      if (b.right > de.clientWidth + 1 && b.width > 0 && cs(e).position !== 'fixed' && rectVisible(e)) { culpable = selector(e); break; }
    }
    fallas.push({ tipo: 'desborde', selector: culpable || 'html', detalle: 'la página mide ' + de.scrollWidth + ' px y la pantalla ' + de.clientWidth });
  }

  // 1b. contenido recortado: un contenedor que esconde lo que no entra (no scrollea, no avisa)
  for (const e of document.body.querySelectorAll('*')) {
    const s = cs(e);
    if (!/(hidden|clip)/.test(s.overflowX) || s.textOverflow === 'ellipsis' || ok(e, 'recorte')) continue;
    const b = e.getBoundingClientRect();
    if (b.width < 40 || b.height < 16 || !rectVisible(e)) continue;
    if (e.scrollWidth > e.clientWidth + 4 && e.querySelector('*') && e.innerText.trim()) {
      fallas.push({ tipo: 'recortado', selector: selector(e), detalle: 'adentro mide ' + e.scrollWidth + ' px y se ven ' + e.clientWidth + '; lo demás queda escondido sin scroll' });
    }
  }

  // 2. tamaño táctil, controles nativos, íconos sin nombre
  for (const { e } of interactivos) {
    if (ok(e, 'tactil')) continue;
    const bb = e.getBoundingClientRect();
    const w = Math.round(bb.width), h = Math.round(bb.height);
    const enLinea = cs(e).display === 'inline' && e.tagName === 'A' && e.closest('p,li,td');
    const lbl = e.tagName === 'INPUT' && e.closest('label');
    const obj = lbl ? lbl.getBoundingClientRect() : bb;
    if (!enLinea && Math.min(obj.width, obj.height) < u.tactil - 0.5) {
      fallas.push({ tipo: 'tactil', selector: selector(e), detalle: w + 'x' + h + ' px, el mínimo es ' + u.tactil });
    }
  }
  let _css = null;
  const reglasCss = () => {
    if (_css !== null) return _css;
    _css = '';
    for (const h of document.styleSheets) { try { for (const r of h.cssRules) _css += r.cssText + '\n'; } catch (x) { /* why: hojas de otro origen no se pueden leer */ } }
    return _css;
  };
  const NATIVOS_PANEL = ['date', 'time', 'datetime-local', 'month', 'week', 'color', 'file'];
  const NATIVOS_CAMPO = ['checkbox', 'radio', 'range'];
  document.querySelectorAll('select,input').forEach((e) => {
    if (ok(e, 'nativo')) return;
    const tag = e.tagName.toLowerCase(), tipo = (e.getAttribute('type') || 'text').toLowerCase();
    const s = cs(e);
    const visible = rectVisible(e);
    if (tag === 'select' && (visible || e.closest('label'))) {
      // why: la lista desplegable la dibuja el sistema fuera de la página, ningún CSS llega
      fallas.push({ tipo: 'control_nativo', selector: selector(e), detalle: 'select: su lista la dibuja el sistema; hace falta un listbox propio' });
    } else if (tag === 'input' && NATIVOS_PANEL.includes(tipo) && visible) {
      fallas.push({ tipo: 'control_nativo', selector: selector(e), detalle: 'input[type=' + tipo + ']: el panel lo dibuja el navegador' });
    } else if (tag === 'input' && NATIVOS_CAMPO.includes(tipo) && visible && s.appearance !== 'none' && s.webkitAppearance !== 'none') {
      fallas.push({ tipo: 'control_nativo', selector: selector(e), detalle: 'input[type=' + tipo + '] de fábrica' });
    } else if (tag === 'input' && tipo === 'search' && visible && !reglasCss().includes('search-cancel')) {
      fallas.push({ tipo: 'control_nativo', selector: selector(e), detalle: 'buscador con la X del navegador' });
    }
  });
  if (u.icono_sin_nombre) {
    for (const { e } of interactivos) {
      if (ok(e, 'icono')) continue;
      const nombre = (e.getAttribute('aria-label') || e.getAttribute('title') || '').trim();
      if (!e.innerText.trim() && !nombre && e.querySelector('svg,img,i,[class*=icon],[class*=ico]')) {
        fallas.push({ tipo: 'icono_sin_nombre', selector: selector(e), detalle: 'botón de ícono sin nombre accesible' });
      }
    }
  }

  // 3. glifos y emoji usados como íconos (los dibuja el sistema, cambian entre aparatos)
  const EMOJI = /\p{Extended_Pictographic}/u;
  const SIMBOLO = /[☀-➿⬀-⯿←-⇿■-◿✓✔✖★☆☰]/u;
  for (const { e } of textuales) {
    if (ok(e, 'glifo')) continue;
    for (const n of e.childNodes) {
      if (n.nodeType !== 3) continue;
      const t = n.textContent.trim();
      // why: una flecha dentro de una frase es tipografía; sola, en un botón o una etiqueta, es un ícono
      const comoIcono = SIMBOLO.test(t) && (t.replace(/\s/g, '').length <= 2 || (e.closest('button,a,[role=button],[role=tab]') && t.length <= 4));
      if ((EMOJI.test(t) && !/^[\d#*]+$/.test(t)) || comoIcono) {
        const m = (t.match(EMOJI) || t.match(SIMBOLO))[0];
        fallas.push({ tipo: 'glifo', selector: selector(e), detalle: '«' + m + '» lo dibuja la fuente del sistema; usar un ícono SVG' });
        break;
      }
    }
  }

  // 4. texto chico y contraste
  const min = u.contraste === 'AAA' ? [7, 4.5] : [4.5, 3];
  for (const { e } of textuales) {
    const s = cs(e);
    const px = parseFloat(s.fontSize);
    if (px < u.texto - 0.01 && !ok(e, 'texto')) fallas.push({ tipo: 'texto_chico', selector: selector(e), detalle: px + ' px, el mínimo es ' + u.texto });
    if (e.closest('[aria-disabled="true"],:disabled') || ok(e, 'contraste')) continue; // why: WCAG exime lo deshabilitado
    const bg = fondo(e);
    if (!bg) continue;
    const fg = mezcla(rgba(s.color), bg);
    const ra = razon(fg, bg);
    const grande = px >= 24 || (px >= 18.66 && parseInt(s.fontWeight, 10) >= 700);
    const need = grande ? min[1] : min[0];
    if (ra < need - 0.005) fallas.push({ tipo: 'contraste', selector: selector(e), detalle: hex(fg) + ' sobre ' + hex(bg) + ' da ' + ra.toFixed(2) + ':1, pide ' + need + ':1' });
  }

  // 5. imágenes rotas
  document.querySelectorAll('img').forEach((e) => {
    if (e.complete && e.naturalWidth === 0 && rectVisible(e)) fallas.push({ tipo: 'imagen_rota', selector: selector(e), detalle: (e.getAttribute('src') || '').slice(0, 120) });
  });

  // 6. barra de desplazamiento de fábrica, si la página o un panel scrollea
  if (u.scroll_propio) {
    const estilada = /scrollbar/.test(reglasCss());
    const scrollea = de.scrollHeight > de.clientHeight + 2 || [...document.querySelectorAll('*')].some((e) => /(auto|scroll)/.test(cs(e).overflowY) && e.scrollHeight > e.clientHeight + 2 && rectVisible(e));
    if (scrollea && !estilada) fallas.push({ tipo: 'control_nativo', selector: 'html', detalle: 'barra de desplazamiento de fábrica: ninguna regla de scrollbar en las hojas' });
  }

  // 7. solapes entre controles y textos (salvo contención y zonas marcadas)
  const recorte = (e) => { let l = -1e9, t = -1e9, r = 1e9, b = 1e9; for (let n = e; n && n !== document.body; n = n.parentElement) { const o = cs(n); if (/(auto|scroll|hidden|clip)/.test(o.overflowY + o.overflowX)) { const q = n.getBoundingClientRect(); l = Math.max(l, q.left); t = Math.max(t, q.top); r = Math.min(r, q.right); b = Math.min(b, q.bottom); } } return { l, t, r, b }; };
  const enFijo = (e) => { for (let n = e; n && n !== document.body; n = n.parentElement) { const p = cs(n).position; if (p === 'fixed' || p === 'sticky') return true; } return false; };
  const cand = [...interactivos, ...textuales].slice(0, 700);
  const ya = new Set();
  for (let i = 0; i < cand.length; i++) {
    for (let j = i + 1; j < cand.length; j++) {
      const a = cand[i], b = cand[j];
      if (a.e === b.e || a.e.contains(b.e) || b.e.contains(a.e)) continue;
      if (ok(a.e, 'solape') || ok(b.e, 'solape')) continue;
      if (enFijo(a.e) !== enFijo(b.e)) continue; // why: una barra fija tapa por diseño lo que scrollea debajo
      const ca = recorte(a.e), cb = recorte(b.e);
      const iw = Math.min(a.r.r, b.r.r, ca.r, cb.r) - Math.max(a.r.l, b.r.l, ca.l, cb.l);
      const ih = Math.min(a.r.b, b.r.b, ca.b, cb.b) - Math.max(a.r.t, b.r.t, ca.t, cb.t);
      if (iw > 2 && ih > 2) {
        const clave = selector(a.e) + '|' + selector(b.e);
        if (ya.has(clave)) continue;
        ya.add(clave);
        fallas.push({ tipo: 'solape', selector: selector(a.e) + ' × ' + selector(b.e), detalle: Math.round(iw) + 'x' + Math.round(ih) + ' px pisados' });
      }
    }
  }

  // 8. inventario de componentes: la materia prima de la consistencia entre pantallas y sistemas
  const componentes = [];
  const firma = (e, clase) => {
    const s = cs(e), b = e.getBoundingClientRect();
    const bg = rgba(s.backgroundColor);
    return {
      clase, familia: e.tagName.toLowerCase() + (([...e.classList].filter((c) => !/[:[\]/]/.test(c))[0] || '') ? '.' + [...e.classList].filter((c) => !/[:[\]/]/.test(c))[0] : ''), selector: selector(e), texto: (e.innerText || e.value || e.getAttribute('aria-label') || '').trim().slice(0, 40),
      alto: Math.round(b.height), radio: s.borderTopLeftRadius, fuente: s.fontSize, peso: s.fontWeight, tipografia: s.fontFamily.split(',')[0].replace(/["']/g, ''),
      relleno: s.paddingLeft + ' ' + s.paddingTop, fondo: bg[3] > 0 ? hex(mezcla(bg, fondo(e.parentElement || e) || [255, 255, 255])) : 'transparente',
      color: hex(rgba(s.color)), borde: s.borderTopWidth !== '0px' && s.borderTopStyle !== 'none' ? s.borderTopWidth + ' ' + hex(rgba(s.borderTopColor)) : 'sin', sombra: s.boxShadow !== 'none' ? 'sí' : 'no',
    };
  };
  const vistos = new Set();
  const anotar = (e, clase) => { if (vistos.has(e) || !rectVisible(e)) return; vistos.add(e); componentes.push(firma(e, clase)); };
  const saturado = (c) => { const mx = Math.max(c[0], c[1], c[2]), mn = Math.min(c[0], c[1], c[2]); return c[3] > 0.5 && mx > 0 && (mx - mn) / mx > 0.35; };
  const activo = (e) => e.matches('[aria-current]:not([aria-current=false]),[aria-selected=true],[aria-pressed=true],[aria-checked=true],.active,.activo,.on,.sel,.is-active');
  document.querySelectorAll('button,[role=button],[role=tab],input[type=submit],input[type=button],a').forEach((e) => {
    const s = cs(e);
    const pareceBoton = e.tagName !== 'A' || (rgba(s.backgroundColor)[3] > 0 || s.borderTopStyle !== 'none') && parseFloat(s.paddingLeft) >= 6;
    if (!pareceBoton || activo(e)) return; // why: el estado activo es otra cara del mismo botón, no otra forma
    const b = e.getBoundingClientRect();
    let clase = 'boton_secundario';
    if (!e.innerText.trim()) clase = 'boton_icono';
    else if (e.closest('nav,[role=tablist],[role=navigation],[role=menu]') || e.matches('[role=tab]')) clase = 'navegacion';
    else if (b.height > 60 || e.innerText.trim().includes('\n')) clase = 'boton_tarjeta';
    else if (saturado(rgba(s.backgroundColor))) clase = 'boton_primario';
    anotar(e, clase);
  });
  document.querySelectorAll('input:not([type=hidden]):not([type=checkbox]):not([type=radio]):not([type=submit]):not([type=button]),textarea,select,[role=combobox]').forEach((e) => anotar(e, 'campo'));
  document.querySelectorAll('h1,h2,h3').forEach((e) => anotar(e, e.tagName.toLowerCase()));
  document.querySelectorAll('th').forEach((e) => anotar(e, 'encabezado_tabla'));
  document.querySelectorAll('[role=tab]').forEach((e) => anotar(e, 'pestana'));
  document.querySelectorAll('[role=dialog],dialog').forEach((e) => anotar(e, 'dialogo'));
  // tarjetas: cajas con fondo o borde propio y radio, de tamaño de tarjeta
  document.querySelectorAll('div,section,article,li').forEach((e) => {
    if (componentes.length > 1500) return;
    const s = cs(e), b = e.getBoundingClientRect();
    if (b.width < 120 || b.height < 60 || parseFloat(s.borderTopLeftRadius) < 2) return;
    const bg = rgba(s.backgroundColor);
    if (bg[3] === 0 && (s.borderTopStyle === 'none' || s.borderTopWidth === '0px') && s.boxShadow === 'none') return;
    anotar(e, 'tarjeta');
  });

  // 9. muestra de colores para comparar entre temas
  const muestra = {};
  let k = 0;
  for (const e of document.body.querySelectorAll('*')) {
    if (k > 900) break;
    if (SALTAR.has(e.tagName) || e.closest('svg,[aria-hidden=true]') || !rectVisible(e)) continue;
    const s = cs(e);
    const bg = rgba(s.backgroundColor);
    const tieneTexto = !!rectTexto(e);
    const bq = e.getBoundingClientRect();
    if (bg[3] === 0 && !tieneTexto) continue;
    if (!tieneTexto && (bq.width < 24 || bq.height < 24)) continue; // why: puntos y adornos no son superficies
    if (saturado(bg)) continue; // why: un color de marca o de estado (el botón verde) puede ser el mismo en los dos temas
    muestra[selector(e)] = { fondo: bg[3] > 0 ? hex(bg) : null, color: tieneTexto ? hex(rgba(s.color)) : null, ok: ok(e, 'tema') };
    k++;
  }
  const fondoPagina = hex(fondo(document.body) || [255, 255, 255]);

  return { fallas, componentes, tema: { fondoPagina, muestra } };
}
