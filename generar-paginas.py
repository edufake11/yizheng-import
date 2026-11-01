#!/usr/bin/env python3
"""
Genera las páginas por categoría y de producto (para SEO) y el sitemap.xml a partir de productos.json.

Uso (desde la carpeta de tu sitio, donde están index.html y productos.json):
    python generar-paginas.py            # usa la fecha de hoy
    python generar-paginas.py 2026-10-26 # o una fecha concreta

Crea:  categoria/<nombre>/index.html   producto/<nombre>/index.html   sitemap.xml
Vuelve a ejecutarlo cada vez que cambies productos.json.
"""
import json, html, re, sys, unicodedata, datetime, pathlib
from urllib.parse import quote

BASE = 'https://www.yizhengimport.com'
PHONE = '51960319600'
MAPS = 'https://maps.app.goo.gl/GHwrE2H2a6AiTUVKA'
TIKTOK = 'https://www.tiktok.com/@yizhengimport'
ROOT = pathlib.Path(__file__).resolve().parent

# Título "buscable" de cada categoría (lo que la gente escribe en Google)
H1 = {
    'Cocina y comedor': 'Artículos de cocina y comedor',
    'Organización del hogar': 'Organizadores para el hogar',
    'Tazas, vasos y bebidas': 'Tazas, vasos y artículos para bebidas',
    'Belleza y maquillaje': 'Organizadores de maquillaje y belleza',
    'Otros productos': 'Más artículos para el hogar',
    'Fiestas y temporada': 'Artículos para fiestas y temporada',
    'Joyeros y exhibidores': 'Joyeros y exhibidores',
    'Baño y cuidado personal': 'Artículos para baño y cuidado personal',
}
ICONOS = {
    'tag': '<path d="M12 2H2v10l9.3 9.3a2.4 2.4 0 0 0 3.4 0l6.6-6.6a2.4 2.4 0 0 0 0-3.4Z"/><path d="M7 7h.01"/>',
    'pin': '<path d="M20 10c0 5-8 12-8 12s-8-7-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    'link': '<path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/>',
    'clock': '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    'wa': '<path class="b" d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>',
}
def ico(n):
    cls = 'i b' if n == 'wa' else 'i'
    return '<svg class="%s" viewBox="0 0 24 24" aria-hidden="true">%s</svg>' % (cls, ICONOS[n])

e = html.escape
def slug(t):
    t = unicodedata.normalize('NFD', t.lower())
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')
def money(n): return 'S/ %.2f' % n
def img_url(p): return quote(p['image'])           # "HA 0079.webp" -> "HA%200079.webp"
def lista(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' y ' + xs[-1]

hoy = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
prods = json.load(open(ROOT / 'productos.json', encoding='utf-8'))
cats = []
for p in prods:
    if p['category'] not in cats: cats.append(p['category'])
SL = {c: slug(c) for c in cats}

ONERR = "if(!this.dataset.f){this.dataset.f=1;this.src=this.src.replace(/\\.webp$/,'.png')}"

FIT_JS = """<script>document.querySelectorAll('.ph img').forEach(function(i){var f=function(){i.parentNode.classList.add('ok');var r=i.naturalWidth/i.naturalHeight;if(r&&(r<0.8||r>1.25)){i.parentNode.classList.add('fit');i.parentNode.style.setProperty('--u','url("'+i.currentSrc+'")')}};if(i.complete){f()}else{i.addEventListener('load',f);i.addEventListener('error',function(){i.parentNode.classList.add('ok')})}})</script>"""

def prod_slug(p): return '%s-%s' % (slug(p['name']), slug(p['code']))
def wa_link(p):
    msg = 'Hola, quisiera consultar por %s (Código: %s) de YIZHENG IMPORT.' % (p['name'], p['code'])
    return 'https://wa.me/%s?text=%s' % (PHONE, quote(msg, safe=''))

def chips_nav(current=None):
    return ''.join('<a href="/categoria/%s/"%s>%s</a>' % (SL[c], ' aria-current="page"' if c == current else '', e(H1.get(c, c))) for c in cats)

def head_links():
    return '<link rel="icon" href="/favicon.ico" sizes="48x48"><link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png"><link rel="icon" type="image/png" sizes="192x192" href="/favicon-192x192.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">'

def topbar():
    return '''<header class="top"><div class="wrap bar"><a class="brand" href="/"><img src="/logo.jpg" alt="Logo de YIZHENG IMPORT" width="40" height="40"><span>YIZHENG <b>IMPORT</b></span></a>
<a class="btn-ghost" href="/#catalogo">Catálogo completo</a></div></header>'''

def wa_fab():
    return f'<a class="wa-fab" href="https://wa.me/{PHONE}?text=' + quote('Hola, quisiera consultar por los productos de YIZHENG IMPORT.', safe='') + f'" target="_blank" rel="noopener" aria-label="Escríbenos por WhatsApp">{ico("wa")}</a>'

def footer():
    foot = ''.join('<a href="/categoria/%s/">%s</a>' % (SL[c], e(H1.get(c, c))) for c in cats)
    return f'''<footer><div class="wrap fcols"><div><strong>YIZHENG IMPORT</strong><p>Galería Comercial Guizado Hnos., piso 5, stands 514 y 515<br>Lima, Perú<br>Lunes a sábado, 10:15 am a 8:00 pm</p>
<p><a href="https://wa.me/{PHONE}" target="_blank" rel="noopener">WhatsApp</a> · <a href="{MAPS}" target="_blank" rel="noopener">Cómo llegar</a> · <a href="{TIKTOK}" target="_blank" rel="noopener">TikTok</a></p></div>
<div><strong>Categorías</strong><div class="flinks">{foot}</div></div></div></footer>'''

TOOLS_JS = r"""<script>(function(){var g=document.querySelector('.grid'),q=document.getElementById('q'),o=document.getElementById('o'),n=document.getElementById('n'),z=document.getElementById('none');if(!g||!q)return;var cs=[].slice.call(g.children).map(function(c,i){var t=(c.textContent||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');var m=c.querySelector('.price');return{el:c,i:i,t:t,p:m?parseFloat(m.textContent.replace(/[^0-9.]/g,'')):0}});
function run(){var w=q.value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').split(/\s+/).filter(Boolean),v=o.value,l=cs.slice();if(v==='a')l.sort(function(a,b){return a.p-b.p});else if(v==='d')l.sort(function(a,b){return b.p-a.p});else l.sort(function(a,b){return a.i-b.i});var k=0;l.forEach(function(c){var ok=w.every(function(x){return c.t.indexOf(x)>-1});c.el.hidden=!ok;if(ok)k++;g.appendChild(c.el)});n.textContent=k+(k===1?' producto':' productos');z.hidden=k>0}
q.addEventListener('input',run);o.addEventListener('change',run);run()})()</script>"""

def card(p, i, eager=4):
    href = '/producto/%s/' % prod_slug(p)
    img = '<a class="ph" href="%s" tabindex="-1" aria-hidden="true"><img src="/%s" alt="%s" %s decoding="async" onerror="%s"></a>' % (
        href, e(img_url(p)), e('%s · código %s' % (p['name'], p['code'])),
        'loading="eager"' if i < eager else 'loading="lazy"', ONERR)
    if p['sold']:
        act = '<span class="soldout">Agotado</span>'
    else:
        act = '<a class="wa" href="%s" target="_blank" rel="noopener">Consultar por WhatsApp</a>' % wa_link(p)
    price = money(p['price']) if p['price'] is not None else 'Consultar precio'
    return ('<article class="card%s">%s<div class="ci"><span class="code">Código: %s</span><h2><a href="%s">%s</a></h2>'
            '<p class="price">%s</p>%s</div></article>') % (' is-sold' if p['sold'] else '', img, e(p['code']), href, e(p['name']), price, act)

def page(cat):
    items = [p for p in prods if p['category'] == cat]
    items = [p for p in items if not p['sold']] + [p for p in items if p['sold']]
    avail = [p for p in items if not p['sold']]
    h1 = H1.get(cat, cat)
    url = '%s/categoria/%s/' % (BASE, SL[cat])
    ej = [p['name'] for p in avail[:3]]
    priced = [p['price'] for p in items if p['price'] is not None]
    title = '%s por mayor y menor en Lima | YIZHENG IMPORT' % h1
    desc = '%s en Lima: %d productos como %s. Mismos precios por mayor y menor. Galería Guizado Hnos., piso 5. Consulta por WhatsApp.' % (h1, len(items), lista(ej))
    if len(desc) > 160: desc = desc[:157].rsplit(' ', 1)[0] + '…'
    intro = ('En YIZHENG IMPORT, en Lima, tienes %d productos de %s, entre ellos %s. ' % (len(items), cat.lower(), lista(ej)))
    if priced:
        intro += 'Los precios van desde %s hasta %s y son los mismos por mayor y por menor. ' % (money(min(priced)), money(max(priced)))
    intro += 'Elige el modelo por su código y consulta la disponibilidad por WhatsApp.'
    og_img = BASE + '/' + img_url(avail[0] if avail else items[0])

    ld_items = []
    for i, p in enumerate(items, 1):
        purl = '%s/producto/%s/' % (BASE, prod_slug(p))
        prod = {'@type': 'Product', 'name': p['name'], 'sku': p['code'], 'image': BASE + '/' + img_url(p),
                'category': cat, 'brand': {'@type': 'Brand', 'name': 'YIZHENG IMPORT'}}
        if p['price'] is not None:
            prod['offers'] = {'@type': 'Offer', 'priceCurrency': 'PEN', 'price': '%.2f' % p['price'], 'url': purl,
                              'availability': 'https://schema.org/OutOfStock' if p['sold'] else 'https://schema.org/InStock',
                              'seller': {'@type': 'Organization', 'name': 'YIZHENG IMPORT'}}
        prod['url'] = purl
        ld_items.append({'@type': 'ListItem', 'position': i, 'item': prod})
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Inicio', 'item': BASE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': h1, 'item': url}]},
        {'@type': 'CollectionPage', 'name': title, 'url': url, 'description': desc,
         'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(items), 'itemListElement': ld_items}}]}
    tools = f"""<div class="tools"><input id="q" type="search" placeholder="Buscar en esta categoría (nombre o código)" aria-label="Buscar en esta categoría"><select id="o" aria-label="Ordenar"><option value="">Orden original</option><option value="a">Precio: menor a mayor</option><option value="d">Precio: mayor a menor</option></select><span id="n" class="tn"></span></div><p id="none" class="none" hidden>No encontramos productos con esa búsqueda. <a href="https://wa.me/{PHONE}" target="_blank" rel="noopener">Pregúntanos por WhatsApp</a></p>"""
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
{head_links()}
<meta name="theme-color" content="#102a30">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="website"><meta property="og:locale" content="es_PE"><meta property="og:site_name" content="YIZHENG IMPORT">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{e(og_img)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/categoria.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head><body>
{topbar()}
<main class="wrap">
<nav class="crumbs" aria-label="Ruta"><a href="/">Inicio</a> › <span>{e(h1)}</span></nav>
<h1>{e(h1)} por mayor y menor en Lima</h1>
<p class="intro">{e(intro)}</p>
<ul class="facts"><li>Mismos precios por mayor y menor</li><li>Lunes a sábado · 10:15 am – 8:00 pm</li><li>Galería Guizado Hnos., piso 5</li></ul>
<nav class="chips" aria-label="Categorías">{chips_nav(cat)}</nav>
{tools}<div class="grid">{''.join(card(p, i) for i, p in enumerate(items))}</div>
<section class="cta"><h2>¿Quieres armar una lista con cantidades?</h2><p>En el catálogo completo puedes agregar varios productos, elegir cuántas unidades necesitas y enviar todo por WhatsApp.</p><a class="btn" href="/#catalogo">Ir al catálogo completo</a></section>
</main>
{footer()}
{wa_fab()}
{FIT_JS}
{TOOLS_JS}</body></html>"""

def product_page(p):
    cat = p['category']
    h1 = H1.get(cat, cat)
    low = h1[0].lower() + h1[1:]
    url = '%s/producto/%s/' % (BASE, prod_slug(p))
    img = BASE + '/' + img_url(p)
    price = money(p['price'])
    title = '%s · código %s | YIZHENG IMPORT' % (p['name'], p['code'])
    if p['sold']:
        desc = '%s (código %s): modelo agotado por el momento. Mira productos similares de %s en YIZHENG IMPORT, Lima.' % (p['name'], p['code'], low)
    else:
        desc = '%s (código %s) en Lima por %s. Mismo precio por mayor y menor. Galería Guizado Hnos., piso 5. Consulta por WhatsApp.' % (p['name'], p['code'], price)
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Inicio', 'item': BASE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': h1, 'item': '%s/categoria/%s/' % (BASE, SL[cat])},
            {'@type': 'ListItem', 'position': 3, 'name': p['name'], 'item': url}]},
        {'@type': 'Product', '@id': url + '#product', 'name': p['name'], 'sku': p['code'], 'mpn': p['code'], 'image': img,
         'description': desc, 'category': h1, 'brand': {'@type': 'Brand', 'name': 'YIZHENG IMPORT'},
         'offers': {'@type': 'Offer', 'url': url, 'priceCurrency': 'PEN', 'price': '%.2f' % p['price'],
                    'itemCondition': 'https://schema.org/NewCondition',
                    'availability': 'https://schema.org/OutOfStock' if p['sold'] else 'https://schema.org/InStock',
                    'seller': {'@type': 'Organization', 'name': 'YIZHENG IMPORT'}}}]}
    if p['sold']:
        act = '<p class="soldnote">Este modelo está agotado por el momento. Mira abajo otros productos de la misma categoría.</p>'
        ask = 'Hola, ¿cuándo vuelve %s (Código: %s) de YIZHENG IMPORT?' % (p['name'], p['code'])
        act += '<a class="wa big alt" href="https://wa.me/%s?text=%s" target="_blank" rel="noopener">Preguntar cuándo vuelve</a>' % (PHONE, quote(ask, safe=''))
        txt = '<p>Por ahora este modelo figura como agotado. Nos encuentras en la Galería Comercial Guizado Hnos., piso 5, stands 514 y 515, de lunes a sábado.</p>'
    else:
        act = '<a class="wa big" href="%s" target="_blank" rel="noopener">Consultar por WhatsApp</a>' % wa_link(p)
        txt = '<p>Para confirmar disponibilidad, escríbenos por WhatsApp indicando el código %s. Nos encuentras en la Galería Comercial Guizado Hnos., piso 5, stands 514 y 515, de lunes a sábado.</p>' % e(p['code'])
    same = [x for x in prods if x['category'] == cat]
    k = same.index(p)
    rel = [x for x in same[k + 1:] + same[:k] if not x['sold']][:4]
    rel_html = ''
    if rel:
        rel_html = '<section class="pd-rel"><h2>Más de %s</h2><div class="grid">%s</div></section>' % (e(low), ''.join(card(x, 9) for x in rel))
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
{head_links()}
<meta name="theme-color" content="#102a30">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="product"><meta property="og:locale" content="es_PE"><meta property="og:site_name" content="YIZHENG IMPORT">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{e(img)}">
<meta name="twitter:card" content="summary_large_image">
<meta property="product:price:amount" content="{'%.2f' % p['price']}"><meta property="product:price:currency" content="PEN">
<link rel="stylesheet" href="/categoria.css"><link rel="stylesheet" href="/producto.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head><body>
{topbar()}
<main class="wrap">
<nav class="crumbs" aria-label="Ruta"><a href="/">Inicio</a> › <a href="/categoria/{SL[cat]}/">{e(h1)}</a> › <span>{e(p['name'])}</span></nav>
<article class="pd">
<div class="pd-img ph"><img src="/{e(img_url(p))}" alt="{e('%s · código %s' % (p['name'], p['code']))}" width="640" height="640" loading="eager" decoding="async" fetchpriority="high" onerror="{ONERR}"></div>
<div class="pd-info">
<span class="code">Código: {e(p['code'])}</span>
<h1>{e(p['name'])}</h1>
<p class="pd-price">{price}</p>
<p class="pd-note">Mismo precio por mayor y por menor</p>
{act}
<a class="btn-ghost" href="/categoria/{SL[cat]}/">Ver más: {e(low)}</a>
<ul class="trust"><li><b>{ico('tag')}</b>Mismo precio por mayor y por menor</li><li><b>{ico('wa')}</b>Confirmamos disponibilidad por WhatsApp</li><li><b>{ico('pin')}</b>Retira en Galería Guizado Hnos., piso 5</li></ul><div class="share"><button type="button" onclick="var u=location.href;if(navigator.share){{navigator.share({{title:document.title,url:u}})}}else{{navigator.clipboard&amp;&amp;navigator.clipboard.writeText(u);this.lastChild.textContent='¡Enlace copiado!'}}">{ico('link')}<span>Compartir</span></button><a href="https://wa.me/?text=" onclick="this.href='https://wa.me/?text='+encodeURIComponent(document.title+' '+location.href)" target="_blank" rel="noopener">Enviar por WhatsApp</a></div>
</div></article>
<section class="pd-text"><h2>Sobre este producto</h2>
<p>{e(p['name'])} con código {e(p['code'])}, de YIZHENG IMPORT, en Lima, dentro de la categoría {e(low)}. Su precio es {price} y es el mismo si compras por mayor o por menor.</p>
{txt}</section>
{rel_html}
<nav class="chips" aria-label="Categorías">{chips_nav()}</nav>
</main>
{footer()}
{wa_fab()}
{FIT_JS}
</body></html>"""

for c in cats:
    d = ROOT / 'categoria' / SL[c]; d.mkdir(parents=True, exist_ok=True)
    (d / 'index.html').write_text(page(c), encoding='utf-8', newline='')
    print('ok categoria/%s/' % SL[c])
for p in prods:
    d = ROOT / 'producto' / prod_slug(p); d.mkdir(parents=True, exist_ok=True)
    (d / 'index.html').write_text(product_page(p), encoding='utf-8', newline='')
print('ok producto/ (%d páginas)' % len(prods))

urls = [BASE + '/'] + ['%s/categoria/%s/' % (BASE, SL[c]) for c in cats] + ['%s/producto/%s/' % (BASE, prod_slug(p)) for p in prods]
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
    sm.append('<url><loc>%s</loc><lastmod>%s</lastmod></url>' % (u, hoy))
sm.append('</urlset>')
(ROOT / 'sitemap.xml').write_text('\n'.join(sm) + '\n', encoding='utf-8', newline='')
print('ok sitemap.xml (%d páginas)' % len(urls))
