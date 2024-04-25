import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_rbk_economic_news():
    url = "https://www.rbc.ru/economics/"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        news_items = soup.find_all("div", class_="item")

        news_data = []

        for item in news_items:
            title_element = item.find("span", class_="item__title")
            link_element = item.find("a", class_="item__link")

            if title_element and link_element:
                title = title_element.text.strip()
                link = link_element["href"]

                full_link = urljoin(url, link)

                news_data.append({'title': title, 'link': full_link})

        return news_data
    else:
        print("Ошибка при получении данных с РБК:", response.status_code)
        return None
