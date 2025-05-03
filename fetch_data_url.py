import requests
from bs4 import BeautifulSoup


def fetch_data_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        media_url = soup.find(id="instant-page-button-element").attrs.get('data-url')
        if '.mp3' in media_url:
            ext = '.mp3'
        elif '.wav' in media_url:
            ext = '.wav'
        if media_url:
            return f"https://www.myinstants.com{media_url}", ext
        else:
            raise Exception("Can't find media url")
    return None
