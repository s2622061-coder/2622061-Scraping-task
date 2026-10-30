import time
import requests
from bs4 import BeautifulSoup

base = 'https://www.musashino-u.ac.jp'
start = base + '/'           

to_visit = [start]
seen = {start}
sitemap = {}

while len(to_visit) > 0:  
    url = to_visit.pop(0)
    print(url)

    time.sleep(1)                

    try:
        res = requests.get(url, timeout=10)
    except requests.RequestException:
        continue

    if 'text/html' not in res.headers.get('Content-Type', ''):
        continue

    html_soup = BeautifulSoup(res.content, 'html.parser')

    if html_soup.title and html_soup.title.string:
        sitemap[url] = html_soup.title.string.strip()
    else:
        sitemap[url] = ''

    for a in html_soup.find_all('a'):
        href = a.get('href')
        if href is None:
            continue
        href = href.split('#')[0]

        if href.startswith('/') and not href.startswith('//'):
            full_url = base + href
        elif href.startswith(base):
            full_url = href
        else:
            continue

        if full_url not in seen:
            seen.add(full_url)
            to_visit.append(full_url)

import csv

with open('sitemap.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['url', 'title'])    
    for url, title in sitemap.items():
        writer.writerow([url, title])

print(f'{len(sitemap)}ページを sitemap.csv に保存しました')