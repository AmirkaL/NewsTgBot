import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_ria_economic_news():
    url = 'https://ria.ru/economy/'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        news_items = soup.find_all('div', class_='list-item')

        news_data = []

        for news in news_items:
            title = news.find('a', class_='list-item__title').text.strip()

            link = news.find('a', class_='list-item__title')['href']
            full_link = urljoin(url, link)

            news_data.append({'title': title, 'link': full_link})

        return news_data
    else:
        print("Ошибка при получении данных с РБК:", response.status_code)
        return None


