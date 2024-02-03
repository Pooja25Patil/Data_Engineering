import urllib.request

# URL of the file to download
url = 'https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb'

# Local path to save the downloaded file
local_file_path = '/tmp/google-chrome-stable_current_amd64.deb'

# Download the file
urllib.request.urlretrieve(url, local_file_path)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import undetected_chromedriver as uc
import time
import csv

# URL of the site to scrape
#URL = "https://de.hotels.com/Hotel-Search?adults=2&d1=2024-02-06&d2=2024-02-10&destination=London%2C%20England%2C%20Gro%C3%9Fbritannien&endDate=2024-02-10&flexibility=0_DAY&latLong=51.50746%2C-0.127673&regionId=2114&rooms=1&semdtl=&sort=RECOMMENDED&startDate=2024-02-06&theme=&useRewards=false&userIntent="


options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(
    options=options
)
# Selenium WebDriver Configuration
#chrome_options = uc.ChromeOptions()
#driver = uc.Chrome(options=chrome_options)
#options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
#driver = webdriver.Chrome(options=options)

driver.get("https://de.hotels.com/Hotel-Search?adults=2&d1=2024-02-06&d2=2024-02-10&destination=London%2C%20England%2C%20Gro%C3%9Fbritannien&endDate=2024-02-10&flexibility=0_DAY&latLong=51.50746%2C-0.127673&regionId=2114&rooms=1&semdtl=&sort=RECOMMENDED&startDate=2024-02-06&theme=&useRewards=false&userIntent=")
time.sleep(20)  # Initial wait for the page to load

def dismiss_cookie_consent():
    try:
        dismiss_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "osano-cm-accept-all"))
        )
        dismiss_button.click()
        print("Cookie consent dialog dismissed.")
    except (TimeoutException, NoSuchElementException):
        print("No cookie consent dialog found or it's not clickable.")

def click_show_more():
    while True:
        try:
            show_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-stid='show-more-results']"))
            )
            show_more_button.click()
            print("Clicked 'Show More'")
            time.sleep(3)  # Wait for the AJAX content to load
        except (TimeoutException, NoSuchElementException):
            print("No more 'Show More' button found or reached maximum tries.")
            break
        except StaleElementReferenceException:
            print("Encountered StaleElementReferenceException. Retrying.")
            time.sleep(2)

def scroll_page():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Adjust time based on your network speed and page response
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

dismiss_cookie_consent()
click_show_more()
scroll_page()  # Ensure all content is loaded

# Data Extraction
hotel_elements = driver.find_elements(By.CLASS_NAME, 'uitk-heading.uitk-heading-5.overflow-wrap.uitk-layout-grid-item.uitk-layout-grid-item-has-row-start')
hotel_locations = driver.find_elements(By.CLASS_NAME, 'uitk-text.uitk-text-spacing-half.truncate-lines-2.uitk-type-300.uitk-text-default-theme')
hotel_ratings = driver.find_elements(By.CLASS_NAME, 'uitk-badge-base-text')
hotel_reviews = driver.find_elements(By.CLASS_NAME, 'uitk-text.truncate-lines-2.uitk-type-300.uitk-type-medium.uitk-text-emphasis-theme')
hotel_comments = driver.find_elements(By.CLASS_NAME, 'uitk-text.truncate-lines-2.uitk-type-200.uitk-type-regular.uitk-text-default-theme')
hotel_prices = driver.find_elements(By.CLASS_NAME, 'uitk-text.uitk-type-500.uitk-type-medium.uitk-text-emphasis-theme')
hotel_images = driver.find_elements(By.CLASS_NAME, 'uitk-image-media')

# Debugging to verify element counts
print(f"Scraping {len(hotel_elements)} data Successfully")

# Write to CSV
with open('HotelCom_Final.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Hotel_Name', 'Hotel_Location', 'Room_Price', 'Hotel_Rating', 'Hotel_Review', 'Hotel_Comment', 'Hotel_Image'])
    for i in range(len(hotel_elements)):
        name = hotel_elements[i].text if i < len(hotel_elements) else "Not Available"
        loc = hotel_locations[i].text if i < len(hotel_locations) else "Not Available"
        price = hotel_prices[i].text if i < len(hotel_prices) else "Not Available"
        rate = hotel_ratings[i].text if i < len(hotel_ratings) else "Not Available"
        review = hotel_reviews[i].text if i < len(hotel_reviews) else "Not Available"
        comment = hotel_comments[i].text if i < len(hotel_comments) else "Not Available"
        image_url = hotel_images[i].get_attribute('src') if i < len(hotel_images) else "Not Available"
        writer.writerow([name, loc, rate, review, comment, price, image_url])

driver.quit()
