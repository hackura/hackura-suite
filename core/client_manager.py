import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from PySide6.QtCore import QObject, Signal

class ClientScraper(QObject):
    finished = Signal(str) # Path to saved logo

    def scrape_logo(self, website_url, storage_dir):
        try:
            if not website_url.startswith(('http://', 'https://')):
                website_url = 'https://' + website_url
            
            # Try to get with a slightly longer timeout and a retry
            try:
                response = requests.get(website_url, timeout=15)
            except (requests.Timeout, requests.ConnectionError):
                # Simple retry
                response = requests.get(website_url, timeout=20)
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for common logo patterns
            logo_url = None
            # 1. Look for <link rel="icon"> or <link rel="shortcut icon">
            icon_link = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
            if icon_link:
                logo_url = icon_link.get('href')
            
            # 2. Look for <img> with 'logo' in class or id
            if not logo_url:
                img = soup.find('img', {'class': lambda x: x and 'logo' in x.lower()}) or \
                      soup.find('img', {'id': lambda x: x and 'logo' in x.lower()}) or \
                      soup.find('img', {'src': lambda x: x and 'logo' in x.lower()})
                if img:
                    logo_url = img.get('src')
            
            # 3. Last ditch: OpenGraph or Twitter tags
            if not logo_url:
                og_image = soup.find('meta', property='og:image')
                if og_image:
                    logo_url = og_image.get('content')
            
            if logo_url:
                full_url = urljoin(website_url, logo_url)
                img_data = requests.get(full_url, timeout=10).content
                
                domain = urlparse(website_url).netloc
                filename = f"client_{domain.replace('.', '_')}.png"
                path = os.path.join(storage_dir, filename)
                
                with open(path, 'wb') as f:
                    f.write(img_data)
                
                self.finished.emit(path)
                return path
        except Exception as e:
            print(f"Scraping failed: {e}")
        
        self.finished.emit("")
        return ""
