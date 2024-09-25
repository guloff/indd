# For links from 2023 published on indd.adobe.com

import requests
from bs4 import BeautifulSoup
import time
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from PIL import Image, ImageChops
from fpdf import FPDF

class PresentationScraper:
    def __init__(self, page_urls):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.page_urls = page_urls
        self.iframe_src_links = []

    def collect_iframe_src_links(self):
        for page_url in self.page_urls:
            try:
                # Получение содержимого страницы
                response = requests.get(page_url)
                response.raise_for_status()  # Вызывает исключение при HTTP ошибках

                # Получение HTML-кода страницы
                page_source = response.text

                # Разбор HTML-кода с помощью BeautifulSoup
                soup = BeautifulSoup(page_source, 'html.parser')

                # Поиск всех тегов iframe
                iframes = soup.find_all('iframe')

                if iframes:
                    found = False
                    for iframe in iframes:
                        src = iframe.get('src')
                        if src:
                            # Фильтрация iframe, содержащих 'indd.adobe.com' в src
                            if 'indd.adobe.com' in src:
                                # Обеспечение полноты ссылки
                                if src.startswith('//'):
                                    src = 'https:' + src
                                elif src.startswith('/'):
                                    src = requests.compat.urljoin(page_url, src)
                                print(f"Найдена ссылка на презентацию: {src}")
                                # Получение заголовка страницы
                                page_title = soup.title.string if soup.title else 'SlidePresentation'
                                self.iframe_src_links.append({'src': src, 'title': page_title})
                                found = True
                    if not found:
                        print(f"На странице {page_url} не найдено подходящих iframe.")
                else:
                    print(f"На странице {page_url} нет тегов iframe.")

            except requests.exceptions.RequestException as e:
                print(f"Ошибка при обработке {page_url}: {e}")

    def process_presentations(self):
        for item in self.iframe_src_links:
            src_url = item['src']
            page_title = item['title']
            print(f"\nОбработка презентации: {page_title}")
            presentation = Presentation(self.driver, src_url, page_title)
            presentation.process()

    def quit(self):
        self.driver.quit()

class Presentation:
    def __init__(self, driver, url, page_title):
        self.driver = driver
        self.url = url
        self.page_title = page_title
        self.wait = WebDriverWait(self.driver, 15)
        self.folder_name = ''
        self.pdf_file_name = ''
        self.slide_number = 1

    def process(self):
        self.driver.get(self.url)
        self.accept_cookies()
        self.switch_to_presentation_frame()
        self.prepare_folder()
        self.take_screenshots()
        self.driver.switch_to.default_content()
        self.save_as_pdf()

    def accept_cookies(self):
        try:
            cookie_button = self.wait.until(EC.element_to_be_clickable((By.ID, "btn-accept")))
            cookie_button.click()
            time.sleep(2)
            print("Приняли cookies.")
        except TimeoutException:
            print("Окно с cookies не появилось.")

    def switch_to_presentation_frame(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            print(f"Найдено {len(iframes)} iframe на странице.")
            self.driver.switch_to.frame(iframes[0])
            print("Переключились на первый iframe.")

            # Проверяем наличие внутренних iframes
            inner_iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            if len(inner_iframes) > 0:
                self.driver.switch_to.frame(inner_iframes[0])
                print("Переключились на внутренний iframe.")
        except Exception as e:
            print(f"Ошибка при переключении на iframe: {e}")

    def prepare_folder(self):
        if not self.page_title:
            self.page_title = 'SlidePresentation'
        self.page_title = self.page_title.strip().replace(' ', '_').replace('/', '_')
        self.page_title = re.sub(r'[\\/*?:"<>|]', "_", self.page_title)
        self.folder_name = self.page_title
        self.pdf_file_name = f"{self.page_title}.pdf"

        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)

    def take_screenshots(self):
        # Установка фокуса на область презентации
        try:
            actions = ActionChains(self.driver)
            actions.move_by_offset(10, 10).click().perform()
            print("Кликнули для установки фокуса.")
        except Exception as e:
            print(f"Не удалось установить фокус на презентации: {e}")

        while True:
            # Сохранение скриншота
            screenshot_path = os.path.join(self.folder_name, f"slide_{self.slide_number}.png")
            self.driver.save_screenshot(screenshot_path)
            print(f"Сохранён скриншот: {screenshot_path}")

            try:
                # Отправка события клавиши через JavaScript
                self.driver.execute_script("""
                    var event = new KeyboardEvent('keydown', {
                        key: 'ArrowRight',
                        keyCode: 39,
                        which: 39,
                        bubbles: true
                    });
                    document.dispatchEvent(event);
                """)
                print(f"Отправлено событие 'keydown' с клавишей 'ArrowRight' на слайде {self.slide_number}.")
                time.sleep(3)  # Ожидание загрузки следующего слайда

                # Проверяем, изменился ли слайд
                new_screenshot_path = os.path.join(self.folder_name, f"slide_temp.png")
                self.driver.save_screenshot(new_screenshot_path)
                if self.compare_images(screenshot_path, new_screenshot_path):
                    print("Больше нет новых слайдов.")
                    os.remove(new_screenshot_path)
                    break
                else:
                    self.slide_number += 1
                    os.rename(new_screenshot_path, os.path.join(self.folder_name, f"slide_{self.slide_number}.png"))
            except Exception as e:
                print(f"Ошибка при переходе к следующему слайду: {e}")
                break

    def compare_images(self, img1_path, img2_path):
        img1 = Image.open(img1_path)
        img2 = Image.open(img2_path)
        diff = ImageChops.difference(img1, img2)
        if diff.getbbox():
            return False  # Изображения разные
        else:
            return True  # Изображения одинаковые

    def save_as_pdf(self):
        first_screenshot_path = os.path.join(self.folder_name, "slide_1.png")
        if os.path.exists(first_screenshot_path):
            img = Image.open(first_screenshot_path)
            width, height = img.size
            width_mm = width * 0.264583  # Конвертация пикселей в мм (при условии 96 dpi)
            height_mm = height * 0.264583

            # Инициализация PDF с размерами первого изображения
            pdf = FPDF(unit='mm', format=(width_mm, height_mm))

            for i in range(1, self.slide_number + 1):
                screenshot_path = os.path.join(self.folder_name, f"slide_{i}.png")
                if os.path.exists(screenshot_path):
                    pdf.add_page()
                    pdf.image(screenshot_path, 0, 0, width_mm, height_mm)

            pdf.output(os.path.join(self.folder_name, self.pdf_file_name))
            print(f"PDF сохранён как {os.path.join(self.folder_name, self.pdf_file_name)}")
        else:
            print("Скриншоты не найдены для создания PDF.")

if __name__ == "__main__":
    # Список URL-адресов страниц
    page_urls = [
        "https://datareportal.com/reports/digital-2023-kazakhstan",
        "https://datareportal.com/reports/digital-2024-kazakhstan",
        "https://datareportal.com/reports/digital-2023-kyrgyzstan",
        "https://datareportal.com/reports/digital-2024-kyrgyzstan",
        "https://datareportal.com/reports/digital-2023-tajikistan",
        "https://datareportal.com/reports/digital-2024-tajikistan",
        "https://datareportal.com/reports/digital-2023-turkmenistan",
        "https://datareportal.com/reports/digital-2024-turkmenistan",
        "https://datareportal.com/reports/digital-2023-uzbekistan",
        "https://datareportal.com/reports/digital-2024-uzbekistan"
    ]

    scraper = PresentationScraper(page_urls)
    scraper.collect_iframe_src_links()
    scraper.process_presentations()
    scraper.quit()
