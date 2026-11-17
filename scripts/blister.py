"""Lê as edições do Blíster (Substack) e grava blister.json com as mais recentes.

O Substack costuma bloquear os servidores do GitHub (erro 403); nesse caso o feed é lido
pelo rss2json.com, um leitor público de RSS. Para testar com um arquivo local: blister.py feed.xml
"""
import json, sys, html, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEED = 'https://justicareprodutiva.substack.com/feed'
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36',
      'Accept': 'application/rss+xml, application/xml;q=0.9, */*;q=0.8'}


def capa(url):
    return ('https://substackcdn.com/image/fetch/w_800,c_limit,f_auto,q_auto:good,fl_progressive:steep/'
            + urllib.parse.quote(url, safe='')) if url else ''


def do_xml(dados):
    itens = []
    for it in ET.fromstring(dados).iter('item'):
        def t(tag):
            e = it.find(tag)
            return html.unescape((e.text or '').strip()) if e is not None else ''
        enc = it.find('enclosure')
        itens.append({'titulo': t('title'), 'subtitulo': t('description'), 'link': t('link').split('?')[0],
                      'data': parsedate_to_datetime(t('pubDate')).strftime('%Y-%m-%d'),
                      'imagem': capa(enc.get('url') if enc is not None else '')})
    return itens


def do_rss2json():
    u = 'https://api.rss2json.com/v1/api.json?rss_url=' + urllib.parse.quote(FEED, safe='')
    j = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30))
    if j.get('status') != 'ok':
        raise RuntimeError(j.get('message'))
    return [{'titulo': html.unescape(i.get('title', '')).strip(),
             'subtitulo': html.unescape(i.get('description', '')).strip() if len(i.get('description', '')) < 400 else '',
             'link': i.get('link', '').split('?')[0], 'data': i.get('pubDate', '')[:10],
             'imagem': capa((i.get('enclosure') or {}).get('link') or i.get('thumbnail') or '')} for i in j.get('items', [])]


if len(sys.argv) > 1:
    itens = do_xml(open(sys.argv[1], 'rb').read())
else:
    try:
        itens = do_xml(urllib.request.urlopen(urllib.request.Request(FEED, headers=UA), timeout=30).read())
    except Exception as e:
        print('feed direto falhou (%s); usando rss2json' % e)
        itens = do_rss2json()
itens.sort(key=lambda x: x['data'], reverse=True)
if not itens:
    sys.exit('nenhuma edição encontrada')
json.dump(itens[:6], open('blister.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(itens), 'edições')
