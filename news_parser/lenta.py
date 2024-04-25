import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_lenta_economic_news():
    url = 'https://lenta.ru/rubrics/economics/economy/'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        news_items = soup.find_all('a', class_='_subrubric')

        news_data = []

        for news_item in news_items:
            title_element = news_item.find('h3', class_='card-full-news__title')
            link = news_item.get('href')
            if title_element and link:
                full_link = urljoin(url, link)
                title = title_element.text.strip()
                news_data.append({'title': title, 'link': full_link})

        return news_data
    else:
        print("Ошибка при получении данных с Lenta.ru:", response.status_code)
        return None
