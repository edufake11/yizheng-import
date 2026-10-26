#!/usr/bin/env python3
"""
Genera las páginas por categoría (para SEO) y el sitemap.xml a partir de productos.json.

Uso (desde la carpeta de tu sitio, donde están index.html y productos.json):
    python generar-paginas.py            # usa la fecha de hoy
    python generar-paginas.py 2026-10-26 # o una fecha concreta

Crea:  categoria/<nombre>/index.html   categoria.css (si no existe)   sitemap.xml
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

def card(p, i):
    img = '<img src="/%s" alt="%s" width="600" height="672" %s decoding="async" onerror="%s">' % (
        e(img_url(p)), e('%s · código %s' % (p['name'], p['code'])),
        'loading="eager"' if i < 4 else 'loading="lazy"', ONERR)
    if p['sold']:
        act = '<span class="soldout">Agotado</span>'
    else:
        msg = 'Hola, quisiera consultar por %s (Código: %s) de YIZHENG IMPORT.' % (p['name'], p['code'])
        act = '<a class="wa" href="https://wa.me/%s?text=%s" target="_blank" rel="noopener">Consultar por WhatsApp</a>' % (PHONE, quote(msg))
    price = money(p['price']) if p['price'] is not None else 'Consultar precio'
    return ('<article class="card%s">%s<div class="ci"><span class="code">Código: %s</span><h2>%s</h2>'
            '<p class="price">%s</p>%s</div></article>') % (' is-sold' if p['sold'] else '', img, e(p['code']), e(p['name']), price, act)

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
        prod = {'@type': 'Product', 'name': p['name'], 'sku': p['code'], 'image': BASE + '/' + img_url(p),
                'category': cat, 'brand': {'@type': 'Brand', 'name': 'YIZHENG IMPORT'}}
        if p['price'] is not None:
            prod['offers'] = {'@type': 'Offer', 'priceCurrency': 'PEN', 'price': '%.2f' % p['price'], 'url': url,
                              'availability': 'https://schema.org/OutOfStock' if p['sold'] else 'https://schema.org/InStock',
                              'seller': {'@type': 'Organization', 'name': 'YIZHENG IMPORT'}}
        ld_items.append({'@type': 'ListItem', 'position': i, 'item': prod})
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Inicio', 'item': BASE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': h1, 'item': url}]},
        {'@type': 'CollectionPage', 'name': title, 'url': url, 'description': desc,
         'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(items), 'itemListElement': ld_items}}]}
    chips = ''.join('<a href="/categoria/%s/"%s>%s</a>' % (SL[c], ' aria-current="page"' if c == cat else '', e(H1.get(c, c))) for c in cats)
    foot = ''.join('<a href="/categoria/%s/">%s</a>' % (SL[c], e(H1.get(c, c))) for c in cats)
    return f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.ico" sizes="48x48"><link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png"><link rel="icon" type="image/png" sizes="192x192" href="/favicon-192x192.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#102a30">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="website"><meta property="og:locale" content="es_PE"><meta property="og:site_name" content="YIZHENG IMPORT">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{e(og_img)}">
<link rel="stylesheet" href="/categoria.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head><body>
<header class="top"><div class="wrap bar"><a class="brand" href="/"><img src="/logo.jpg" alt="Logo de YIZHENG IMPORT" width="40" height="40"><span>YIZHENG <b>IMPORT</b></span></a>
<a class="btn-ghost" href="/#catalogo">Catálogo completo</a></div></header>
<main class="wrap">
<nav class="crumbs" aria-label="Ruta"><a href="/">Inicio</a> › <span>{e(h1)}</span></nav>
<h1>{e(h1)} por mayor y menor en Lima</h1>
<p class="intro">{e(intro)}</p>
<ul class="facts"><li>Mismos precios por mayor y menor</li><li>Lunes a sábado · 10:15 am – 8:00 pm</li><li>Galería Guizado Hnos., piso 5</li></ul>
<nav class="chips" aria-label="Categorías">{chips}</nav>
<div class="grid">{''.join(card(p, i) for i, p in enumerate(items))}</div>
<section class="cta"><h2>¿Quieres armar una lista con cantidades?</h2><p>En el catálogo completo puedes agregar varios productos, elegir cuántas unidades necesitas y enviar todo por WhatsApp.</p><a class="btn" href="/#catalogo">Ir al catálogo completo</a></section>
</main>
<footer><div class="wrap fcols"><div><strong>YIZHENG IMPORT</strong><p>Galería Comercial Guizado Hnos., piso 5, stands 514 y 515<br>Lima, Perú<br>Lunes a sábado, 10:15 am a 8:00 pm</p>
<p><a href="https://wa.me/{PHONE}" target="_blank" rel="noopener">WhatsApp</a> · <a href="{MAPS}" target="_blank" rel="noopener">Cómo llegar</a> · <a href="{TIKTOK}" target="_blank" rel="noopener">TikTok</a></p></div>
<div><strong>Categorías</strong><div class="flinks">{foot}</div></div></div></footer>
</body></html>'''

for c in cats:
    d = ROOT / 'categoria' / SL[c]; d.mkdir(parents=True, exist_ok=True)
    (d / 'index.html').write_text(page(c), encoding='utf-8')
    print('✓ categoria/%s/' % SL[c])

urls = [(BASE + '/', '1.0')] + [('%s/categoria/%s/' % (BASE, SL[c]), '0.8') for c in cats]
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u, pr in urls:
    sm.append('  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>' % (u, hoy, pr))
sm.append('</urlset>')
(ROOT / 'sitemap.xml').write_text('\n'.join(sm) + '\n', encoding='utf-8')
print('✓ sitemap.xml (%d páginas)' % len(urls))
