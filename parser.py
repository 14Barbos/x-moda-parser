import requests
import mysql.connector
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def create_table(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS shop (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title TEXT,
            additional_title TEXT,
            main_image TEXT,
            price TEXT,
            image1 TEXT,
            image2 TEXT,
            image3 TEXT,
            color TEXT,
            composition TEXT,
            brand TEXT, 
            season TEXT, 
            maker TEXT, 
            country TEXT,
            size1 TEXT,
            size2 TEXT,
            size3 TEXT,
            size4 TEXT,
            size5 TEXT,
            size6 TEXT
            )''')


def save_info_to_db(cursor, product_name, additional_name, image_url, price, image1, image2, image3, color, composition,
                    brand, season, maker, country, size1, size2, size3, size4, size5, size6):
    cursor.execute('''INSERT INTO shop (title, additional_title, main_image, price, image1, image2, image3, color, composition,
                                        brand, season, maker, country, size1, size2, size3, size4, size5, size6)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                   (product_name, additional_name, image_url, price, image1, image2, image3, color, composition,
                    brand, season, maker, country, size1, size2, size3, size4, size5, size6))
    conn.commit()


def scrape_page(url, cursor):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        product_cards = soup.find_all("div", class_="catalog__card-wrapper")

        for card in product_cards:
            product_name = card.find("div", class_="product-card__name").text.strip()
            additional_name = card.find("div", class_="product-card__kind").text.strip()
            image_url = "https:" + card.find("img")["src"]
            product_url = 'https://x-moda.ru' + card.find("a")["href"]

            driver.get(product_url)
            print(f'Обрабатываемая карточка: {product_url}')

            price_element = driver.find_element(By.XPATH, "//div[@class='product-b__price-new']")
            price = price_element.text.strip()

            image_elements = driver.find_elements(By.CSS_SELECTOR, ".photos-slider__item img")[1:4]
            image1 = image_elements[0].get_attribute("src") if image_elements else "Нет картинки"
            image2 = image_elements[1].get_attribute("src") if len(image_elements) > 1 else "Нет картинки"
            image3 = image_elements[2].get_attribute("src") if len(image_elements) > 2 else "Нет картинки"

            color_element = driver.find_element(By.XPATH, "//p[contains(text(), 'Цвет')]")
            color_text = color_element.text
            color = color_text.replace("Цвет: ", "")

            composition_element = driver.find_element(By.XPATH, "//p[contains(text(), 'Состав')]")
            composition = composition_element.text
            composition = composition.replace("Состав: ", "")

            brand_element = driver.find_element(By.XPATH, "//p[contains(text(), 'Бренд')]")
            brand = brand_element.text
            brand = brand.replace("Бренд: ", "")

            season_element = driver.find_element(By.XPATH, "//p[contains(text(), 'Сезон')]")
            season = season_element.text
            season = season.replace("Сезон: ", "")

            maker_element = driver.find_element(By.XPATH, "//p[contains(text(), 'Производитель')]")
            maker = maker_element.text
            maker = maker.replace("Производитель: ", "")

            country_element = driver.find_element(By.XPATH, "//p[contains(text(), 'Страна производства')]")
            country = country_element.text
            country = country.replace("Страна производства: ", "")

            size_elements = driver.find_elements(By.XPATH, "//label[contains(@class, 'w-radio_product-sizes')]")
            size1 = size2 = size3 = size4 = size5 = size6 = None

            for i, size_element in enumerate(size_elements):
                size_text = size_element.find_element(By.CLASS_NAME, 'label').text.strip()
                if i == 0:
                    size1 = size_text
                elif i == 1:
                    size2 = size_text
                elif i == 2:
                    size3 = size_text
                elif i == 3:
                    size4 = size_text
                elif i == 4:
                    size5 = size_text
                elif i == 5:
                    size6 = size_text

            # print(f"Название: {product_name}")
            # print(f"Категория: {additional_name}")
            # print(f"Основная картинка: {image_url}")
            # print(f"Картинка 1: {image1}")
            # print(f"Картинка 2: {image2}")
            # print(f"Картинка 3: {image3}")
            # print(f"Цена: {price}")
            # print(f"Цвет: {color}")
            # print(f"Состав: {composition}")
            # print(f"Бренд: {brand}")
            # print(f"Сезон: {season}")
            # print(f"Производитель: {maker}")
            # print(f"Страна производства: {country}")
            # print(f"Размер 1: {size1}")
            # print(f"Размер 2: {size2}")
            # print(f"Размер 3: {size3}")
            # print(f"Размер 4: {size4}")
            # print(f"Размер 5: {size5}")
            # print(f"Размер 6: {size6}")
            # print('')

            save_info_to_db(cursor, product_name, additional_name, image_url, price, image1, image2, image3, color,
                            composition, brand, season, maker, country, size1, size2, size3, size4, size5, size6)
    else:
        print(f"Ошибка при первом запросе: {response.status_code}")


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="shop"
    )

    cursor = conn.cursor()
    create_table(cursor)

    for page_num in range(1, 160):
        page_url = f"https://x-moda.ru/catalog/zhenschinam?page={page_num}"
        print(f"Обрабатываем страницу: {page_url}")
        try:
            scrape_page(page_url, cursor)
        except Exception as e:
            print(e)

    for page_num in range(1, 69):
        page_url = f"https://x-moda.ru/catalog/muzhchinam?page={page_num}"
        print(f"Обрабатываем страницу: {page_url}")
        try:
            scrape_page(page_url, cursor)
        except Exception as e:
            print(e)

    for page_num in range(1, 20):
        page_url = f"https://x-moda.ru/catalog/detyam?page={page_num}"
        print(f"Обрабатываем страницу: {page_url}")
        try:
            scrape_page(page_url, cursor)
        except Exception as e:
            print(e)

    conn.close()
    driver.close()
    input("Суши вёсла")