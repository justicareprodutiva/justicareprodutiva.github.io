"""Lê o feed do Blíster no Substack e grava blister.json com as últimas edições."""
import json, re, sys, html, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEED = 'https://justicareprodutiva.substack.com/feed'
req = urllib.request.Request(FEED, headers={'User-Agent': 'Mozilla/5.0 (site justicareprodutiva.org)'})
xml = open(sys.argv[1], 'rb').read() if len(sys.argv) > 1 else urllib.request.urlopen(req, timeout=30).read()
root = ET.fromstring(xml)
itens = []
for it in root.iter('item'):
    def t(tag):
        e = it.find(tag)
        return html.unescape((e.text or '').strip()) if e is not None else ''
    enc = it.find('enclosure')
    img = enc.get('url') if enc is not None else ''
    if img:
        img = 'https://substackcdn.com/image/fetch/w_800,c_limit,f_auto,q_auto:good,fl_progressive:steep/' + urllib.request.quote(img, safe='')
    d = parsedate_to_datetime(t('pubDate'))
    itens.append({'titulo': t('title'), 'subtitulo': t('description'), 'link': t('link').split('?')[0],
                  'data': d.strftime('%Y-%m-%d'), 'imagem': img})
itens.sort(key=lambda x: x['data'], reverse=True)
if not itens:
    sys.exit('feed vazio')
json.dump(itens[:6], open('blister.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(itens), 'edições')
