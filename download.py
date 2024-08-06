import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse
from html2text import HTML2Text
from concurrent import futures

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0"
}

def url_to_path(url: str) -> str:
    parsed_url = urlparse(url)
    path = parsed_url.path.strip('/')
    path = path.replace('/', '_')
    return path

def parse_content(html):
    soup = BeautifulSoup(html, 'lxml')
    content = soup.find('article')
    return content

def preprocess_content(content):
    for c in content.find_all('th'):
        c_text = ' '.join(c.stripped_strings)
        c.clear()
        c.append(c_text)
    return str(content)

def html_to_markdown(html_content):
    h = HTML2Text()
    h.ignore_links = True
    markdown_content = h.handle(html_content)
    return markdown_content.strip()

def save_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

def download_html(url):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print(f"Downloaded: {url}")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")

def read_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'xml')
        for loc in soup.find_all('loc'):
            yield loc.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to read sitemap {sitemap_url}: {e}")
        
def pipeline(url):
    filename = os.path.join(save_path, (url_to_path(url) or 'index') + '.md')
    html = download_html(url)
    content = parse_content(html)
    if content is None: return
    content = preprocess_content(content)
    markdown = html_to_markdown(content)
    save_file(filename, markdown)  

def main(sitemap_url, save_path):
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    urls = read_sitemap(sitemap_url)
    with futures.ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(pipeline, urls)

if __name__ == "__main__":
    sitemap_url = 'https://ejaan.kemdikbud.go.id/sitemap.xml'
    save_path = os.path.join(os.getcwd(), 'result')
    main(sitemap_url, save_path)
