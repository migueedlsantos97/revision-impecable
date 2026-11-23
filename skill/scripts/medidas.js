async (u) => {
  // Se inyecta en la página. Recibe umbrales y devuelve {fallas: [{tipo, selector, detalle}], componentes: [...], tema: {...}, titulo}.
  // why: sin esperar las fuentes se mide texto con la fuente de reemplazo (anchos y contraste distintos); tope de 3 s
  try { await Promise.race([document.fonts.ready, new Promise((r) => setTimeout(r, 3000))]); } catch (x) { /* sin Font Loading API */ }
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
    if (e.scrollWidth > e.clientWidth + u.tol_recorte && e.querySelector('*') && e.innerText.trim()) {
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
  const SIMBOLO = /[☀-➿⬀-⯿←-⇿■-◿✓✔✖★☆☰×‹›✕]/u;
  const SIN_MARCAS = (t) => t.replace(/[©®™]/g, ''); // why: © ® ™ son texto legal, no íconos, aunque Unicode los llame pictográficos
  for (const { e } of textuales) {
    if (ok(e, 'glifo')) continue;
    for (const n of e.childNodes) {
      if (n.nodeType !== 3) continue;
      const t = n.textContent.trim();
      // why: una flecha dentro de una frase es tipografía; sola, en un botón o una etiqueta, es un ícono
      const comoIcono = SIMBOLO.test(t) && (t.replace(/\s/g, '').length <= 2 || (e.closest('button,a,[role=button],[role=tab]') && t.length <= 4));
      const tl = SIN_MARCAS(t);
      if ((EMOJI.test(tl) && !/^[\d#*]+$/.test(tl)) || comoIcono) {
        const m = (tl.match(EMOJI) || t.match(SIMBOLO))[0];
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
    const grande = px >= u.texto_grande_px || (px >= u.texto_grande_negrita_px && parseInt(s.fontWeight, 10) >= 700);
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
  const todos = [...interactivos, ...textuales];
  const cand = todos.slice(0, u.max_candidatos_solape);
  if (todos.length > cand.length) fallas.push({ tipo: 'solape_truncado', selector: 'html', detalle: 'hay ' + todos.length + ' elementos y solo se compararon ' + cand.length + ' (umbrales.max_candidatos_solape)' });
  const pre = cand.map((c) => ({ ...c, rc: recorte(c.e), fijo: enFijo(c.e) }));
  const ya = new Set();
  for (let i = 0; i < pre.length; i++) {
    for (let j = i + 1; j < pre.length; j++) {
      const a = pre[i], b = pre[j];
      if (a.e === b.e || a.e.contains(b.e) || b.e.contains(a.e)) continue;
      if (ok(a.e, 'solape') || ok(b.e, 'solape')) continue;
      if (a.fijo !== b.fijo) continue; // why: una barra fija tapa por diseño lo que scrollea debajo
      const ca = a.rc, cb = b.rc;
      const iw = Math.min(a.r.r, b.r.r, ca.r, cb.r) - Math.max(a.r.l, b.r.l, ca.l, cb.l);
      const ih = Math.min(a.r.b, b.r.b, ca.b, cb.b) - Math.max(a.r.t, b.r.t, ca.t, cb.t);
      if (iw > u.tol_solape && ih > u.tol_solape) {
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
  const saturado = (c) => { const mx = Math.max(c[0], c[1], c[2]), mn = Math.min(c[0], c[1], c[2]); return c[3] > 0.5 && mx > 0 && (mx - mn) / mx > u.saturacion; };
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
    if (componentes.length > u.max_componentes) return;
    const s = cs(e), b = e.getBoundingClientRect();
    if (b.width < 120 || b.height < 60 || parseFloat(s.borderTopLeftRadius) < 2) return;
    const bg = rgba(s.backgroundColor);
    if (bg[3] === 0 && (s.borderTopStyle === 'none' || s.borderTopWidth === '0px') && s.boxShadow === 'none') return;
    anotar(e, 'tarjeta');
  });

  // 8b. accesibilidad básica y chequeos de documento (sin criterio: o está o no está)
  const falla = (tipo, sel, det) => fallas.push({ tipo, selector: sel, detalle: det });
  if (!(document.documentElement.getAttribute('lang') || '').trim()) falla('sin_lang', 'html', 'falta <html lang>: los lectores de pantalla no saben en qué idioma leer');
  if (!document.querySelector('meta[name=viewport]')) falla('sin_viewport', 'head', 'falta <meta name="viewport">: el celular renderiza la página como de escritorio');
  if (!(document.title || '').trim()) falla('sin_titulo', 'head', 'la página no tiene <title>');
  const textoDe = (ids) => (ids || '').split(/\s+/).filter(Boolean).map((i) => { const n = document.getElementById(i); return n ? (n.textContent || '').trim() : ''; }).join('').trim();
  const nombreDe = (e) => (e.getAttribute('aria-label') || '').trim() || textoDe(e.getAttribute('aria-labelledby')) || (e.getAttribute('title') || '').trim();

  document.querySelectorAll('img:not([alt])').forEach((e) => {
    if (e.closest('[aria-hidden=true]') || e.getAttribute('role') === 'presentation' || e.getAttribute('role') === 'none' || ok(e, 'alt') || !rectVisible(e)) return;
    falla('img_sin_alt', selector(e), 'img sin atributo alt (un alt="" vacío marca una imagen decorativa)');
  });
  document.querySelectorAll('img').forEach((e) => {
    if (ok(e, 'dimensiones') || !rectVisible(e) || (e.getAttribute('width') && e.getAttribute('height')) || cs(e).aspectRatio !== 'auto' || e.style.height || e.closest('picture,[style*=aspect-ratio]')) return;
    falla('img_sin_dimensiones', selector(e), 'sin width/height ni aspect-ratio: la página se corre al cargar la imagen (CLS)');
  });
  document.querySelectorAll('input:not([type=hidden]):not([type=submit]):not([type=button]):not([type=reset]):not([type=image]),select,textarea').forEach((e) => {
    if (ok(e, 'nombre') || !rectVisible(e)) return;
    const conLabel = [...(e.labels || [])].some((l) => (l.textContent || '').trim());
    if (!conLabel && !nombreDe(e)) falla('campo_sin_nombre', selector(e), 'campo sin label, aria-label ni title (el placeholder no es un nombre)');
  });
  const ICONO = 'svg,img,i,[class*=icon],[class*=ico]';
  document.querySelectorAll('a[href],button,[role=button],[role=link]').forEach((e) => {
    if (ok(e, 'nombre') || !rectVisible(e)) return;
    const href = e.getAttribute('href');
    if (e.tagName === 'A' && e.getAttribute('role') !== 'button' && (href === '#' || /^\s*javascript:/i.test(href || ''))) {
      falla('enlace_falso', selector(e), 'enlace con href="' + href.slice(0, 30) + '": es un botón disfrazado (no navega ni se anuncia como botón)');
    }
    const hijoAlt = [...e.querySelectorAll('img[alt],svg title')].some((x) => (x.getAttribute('alt') || x.textContent || '').trim());
    if (!(e.innerText || '').trim() && !nombreDe(e) && !hijoAlt && !e.querySelector(ICONO) && !(e.value || '').trim()) falla('sin_nombre_accesible', selector(e), 'enlace o botón vacío: sin texto, aria-label ni title');
  });
  const porId = {};
  document.querySelectorAll('[id]').forEach((e) => { if (e.id) (porId[e.id] = porId[e.id] || []).push(e); });
  Object.keys(porId).filter((id) => porId[id].length > 1).slice(0, 30).forEach((id) => falla('id_duplicado', '#' + id, porId[id].length + ' elementos con el mismo id'));
  ['aria-labelledby', 'aria-describedby', 'aria-controls', 'aria-owns'].forEach((at) => {
    document.querySelectorAll('[' + at + ']').forEach((e) => {
      const rotos = (e.getAttribute(at) || '').split(/\s+/).filter((i) => i && !document.getElementById(i));
      if (rotos.length) falla('aria_roto', selector(e), at + ' apunta a #' + rotos.join(', #') + ', que no existe');
    });
  });
  document.querySelectorAll('label[for]').forEach((l) => { if (!document.getElementById(l.getAttribute('for'))) falla('aria_roto', selector(l), 'label for="' + l.getAttribute('for') + '" apunta a un id que no existe'); });
  document.querySelectorAll('[tabindex]').forEach((e) => {
    if (parseInt(e.getAttribute('tabindex'), 10) > 0 && !ok(e, 'tabindex')) falla('tabindex_positivo', selector(e), 'tabindex=' + e.getAttribute('tabindex') + ' rompe el orden natural del teclado; usar 0 o reordenar el DOM');
  });
  // headings: una h1 y sin saltos de nivel
  const hs = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6,[role=heading][aria-level]')].filter((e) => rectVisible(e));
  const nivel = (e) => (e.tagName[0] === 'H' && e.tagName.length === 2 ? +e.tagName[1] : parseInt(e.getAttribute('aria-level'), 10) || 2);
  const h1s = hs.filter((e) => nivel(e) === 1);
  if (hs.length && h1s.length !== 1) falla('heading_h1', h1s[1] ? selector(h1s[1]) : 'body', h1s.length ? h1s.length + ' títulos h1 (debería haber uno)' : 'la página no tiene h1');
  hs.forEach((e, i) => { if (i && nivel(e) - nivel(hs[i - 1]) > u.heading_max_salto) falla('heading_salto', selector(e), 'salta de h' + nivel(hs[i - 1]) + ' a h' + nivel(e)); });
  // texto cortado con puntos suspensivos o line-clamp, sin forma de leerlo entero
  document.body.querySelectorAll('*').forEach((e) => {
    const s = cs(e);
    const clamp = s.webkitLineClamp && s.webkitLineClamp !== 'none';
    if ((s.textOverflow !== 'ellipsis' && !clamp) || ok(e, 'cortado') || e.closest('[title],[aria-label]')) return;
    if ((clamp ? e.scrollHeight > e.clientHeight + 1 : e.scrollWidth > e.clientWidth + 1) && rectVisible(e)) falla('texto_cortado_sin_title', selector(e), 'el texto se corta y no hay title para leerlo completo');
  });
  // fuentes que no cargaron
  try { [...document.fonts].filter((f) => f.status === 'error').slice(0, 10).forEach((f) => falla('fuente_no_cargo', f.family, 'la fuente declarada no se pudo cargar; se muestra la de reemplazo')); } catch (x) { /* sin API */ }
  // lo que tapa a un control: en el centro de un control a la vista, el elemento de más arriba no es él ni lo contiene
  const pv = { w: window.innerWidth, h: window.innerHeight };
  for (const { e, r } of interactivos.slice(0, 300)) {
    if (ok(e, 'tapado') || enFijo(e)) continue;
    const cx = (r.l + r.r) / 2, cy = (r.t + r.b) / 2;
    if (cx < 0 || cy < 0 || cx >= pv.w || cy >= pv.h) continue;
    const t = document.elementFromPoint(cx, cy);
    if (t && t !== e && !e.contains(t) && !t.contains(e) && !(e.closest('label') && e.closest('label').contains(t)) && !(t.closest('label') && t.closest('label').contains(e))) {
      falla('tapado', selector(e), 'en su centro hay otro elemento encima: ' + selector(t));
    }
  }

  // 9. muestra de colores para comparar entre temas
  const muestra = {};
  let k = 0;
  for (const e of document.body.querySelectorAll('*')) {
    if (k > u.max_muestra) break;
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

  const silencios = {};
  document.querySelectorAll('[data-revision-ok]').forEach((e) => { (e.getAttribute('data-revision-ok') || '').split(/\s+/).filter(Boolean).forEach((k) => { silencios[k] = (silencios[k] || 0) + 1; }); });
  return { fallas, componentes, tema: { fondoPagina, muestra }, titulo: document.title || '', silencios };
}
