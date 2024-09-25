# For links from 2017 to 2022 published on SlideShare.com

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
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from fpdf import FPDF

def collect_iframe_src_links(page_urls):
    iframe_src_links = []
    for page_url in page_urls:
        try:
            # Fetch the page source
            response = requests.get(page_url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # print(f"\nProcessing {page_url}")

            # Get the page content
            page_source = response.text

            # Parse the HTML content
            soup = BeautifulSoup(page_source, 'html.parser')

            # Find all iframe tags
            iframes = soup.find_all('iframe')

            if iframes:
                found = False
                for iframe in iframes:
                    src = iframe.get('src')
                    if src:
                        # Filter iframes containing specific keywords
                        if 'slideshare.net' in src or 'slideshow' in src:
                            # Ensure the link is complete
                            if src.startswith('//'):
                                src = 'https:' + src
                            elif src.startswith('/'):
                                src = requests.compat.urljoin(page_url, src)
                            print(f"Found iframe src: {src}")
                            # Get the page title
                            page_title = soup.title.string if soup.title else 'SlidePresentation'
                            iframe_src_links.append({'src': src, 'title': page_title})
                            found = True
                if not found:
                    print("No matching iframe src found in the page.")
            else:
                print("No iframe tags found in the page.")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while processing {page_url}: {e}")

    return iframe_src_links


def screenshot_slides_to_pdf(driver, url, page_title):
    # Navigate to URL
    driver.get(url)
    wait = WebDriverWait(driver, 15)  # Waits for elements up to 15 seconds

    # Accept cookies if prompted
    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Accept')]")))
        cookie_button.click()
        time.sleep(2)
        print("Accepted cookies.")
    except TimeoutException:
        print("No cookie prompt found, proceeding.")

    # Prepare folder and PDF names
    if not page_title:
        page_title = 'SlidePresentation'
    page_title = page_title.strip().replace(' ', '_').replace('/', '_')
    page_title = re.sub(r'[\\/*?:"<>|]', "_", page_title)
    folder_name = page_title
    pdf_file_name = f"{page_title}.pdf"

    # Create folder for screenshots
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    slide_number = 1

    while True:
        # Click to ensure navigation buttons are visible
        actions = ActionChains(driver)
        viewer_area = driver.find_element(By.TAG_NAME, 'body')
        actions.move_to_element(viewer_area).click().perform()
        actions.reset_actions()
        time.sleep(1)

        # Save screenshot
        screenshot_path = os.path.join(folder_name, f"slide_{slide_number}.png")
        driver.save_screenshot(screenshot_path)
        print(f"Captured {screenshot_path}")

        # Try to find and click the "Next" button
        try:
            next_button = wait.until(EC.element_to_be_clickable((By.ID, "next-slide")))
            print("Найдена кнопка 'Next'.")
            next_button.click()
            print("Клик по кнопке 'Next' выполнен.")
            time.sleep(2)  # Ожидание загрузки следующего слайда
            slide_number += 1
        except TimeoutException:
            print("Кнопка 'Next' не найдена или больше нет слайдов.")
            break


    # Convert screenshots to PDF
    first_screenshot_path = os.path.join(folder_name, "slide_1.png")
    if os.path.exists(first_screenshot_path):
        img = Image.open(first_screenshot_path)
        width, height = img.size
        width_mm = width * 0.264583  # Convert pixels to mm (assuming 96 dpi)
        height_mm = height * 0.264583

        # Initialize PDF with the size of the first image
        pdf = FPDF(unit='mm', format=(width_mm, height_mm))

        for i in range(1, slide_number + 1):
            screenshot_path = os.path.join(folder_name, f"slide_{i}.png")
            if os.path.exists(screenshot_path):
                pdf.add_page()
                pdf.image(screenshot_path, 0, 0, width_mm, height_mm)

        pdf.output(os.path.join(folder_name, pdf_file_name))
        print(f"PDF saved as {os.path.join(folder_name, pdf_file_name)}")
    else:
        print("No screenshots found to create PDF.")

# Main execution
if __name__ == "__main__":
    # List of page URLs to collect iframe src links from
    page_urls = [
        # "https://datareportal.com/reports/digital-2017-kazakhstan",
        # "https://datareportal.com/reports/digital-2018-kazakhstan",
        # "https://datareportal.com/reports/digital-2019-kazakhstan",
        # "https://datareportal.com/reports/digital-2020-kazakhstan",
        # "https://datareportal.com/reports/digital-2021-kazakhstan",
        "https://datareportal.com/reports/digital-2022-kazakhstan",
        # "https://datareportal.com/reports/digital-2017-kyrgyzstan",
        # "https://datareportal.com/reports/digital-2018-kyrgyzstan",
        # "https://datareportal.com/reports/digital-2019-kyrgyzstan",
        # "https://datareportal.com/reports/digital-2020-kyrgyzstan",
        # "https://datareportal.com/reports/digital-2021-kyrgyzstan",
        # "https://datareportal.com/reports/digital-2022-kyrgyzstan",
        # "https://datareportal.com/reports/digital-2017-tajikistan",
        # "https://datareportal.com/reports/digital-2018-tajikistan",
        # "https://datareportal.com/reports/digital-2019-tajikistan",
        # "https://datareportal.com/reports/digital-2020-tajikistan",
        # "https://datareportal.com/reports/digital-2021-tajikistan",
        # "https://datareportal.com/reports/digital-2022-tajikistan",
        # "https://datareportal.com/reports/digital-2017-turkmenistan",
        # "https://datareportal.com/reports/digital-2018-turkmenistan",
        # "https://datareportal.com/reports/digital-2019-turkmenistan",
        # "https://datareportal.com/reports/digital-2020-turkmenistan",
        # "https://datareportal.com/reports/digital-2021-turkmenistan",
        # "https://datareportal.com/reports/digital-2022-turkmenistan",
        # "https://datareportal.com/reports/digital-2017-uzbekistan",
        # "https://datareportal.com/reports/digital-2018-uzbekistan",
        # "https://datareportal.com/reports/digital-2019-uzbekistan",
        # "https://datareportal.com/reports/digital-2020-uzbekistan",
        # "https://datareportal.com/reports/digital-2021-uzbekistan",
        # "https://datareportal.com/reports/digital-2022-uzbekistan"
    ]

    # Collect iframe src links
    iframe_src_links = collect_iframe_src_links(page_urls)

    # Initialize the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Process each iframe src link
    for item in iframe_src_links:
        src_url = item['src']
        page_title = item['title']
        screenshot_slides_to_pdf(driver, src_url, page_title)

    # Quit the driver
    driver.quit()
