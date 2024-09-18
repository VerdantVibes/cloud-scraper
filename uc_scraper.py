from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from undetected_chromedriver.options import ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
import shutil
import time
import os


class WebScraper:
    # Create a WebScraper instance
    def __init__(self, driver_temp_dir, UserName):
        self.driver = self.initialize_driver(driver_temp_dir, UserName)
        self.wait = WebDriverWait(self.driver, 10)  # Added explicit wait

    # Init the WebScraper instance
    def initialize_driver(self, driver_temp_dir, UserName):
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
        }
        chrome_options.add_experimental_option("prefs", prefs)

        chromedriver_path = f"C:\\Users\\{UserName}\\AppData\\Roaming\\undetected_chromedriver\\undetected\\chromedriver-win32\\chromedriver.exe"

        if not os.path.isfile(chromedriver_path):
            raise FileNotFoundError(f"Cannot find chromedriver at {chromedriver_path}")

        chromedriver_temp_path = os.path.join(driver_temp_dir, "chromedriver.exe")
        shutil.copy(chromedriver_path, chromedriver_temp_path)

        # Initialize undetected ChromeDriver
        driver = uc.Chrome(
            options=chrome_options, driver_executable_path=chromedriver_temp_path
        )
        return driver

    # Scrape the website
    def scrape_website(self, url, lastname, data_array, start_page, per_thread):
        attempts = 0
        max_attempts = 3
        debugging = 0
        while attempts < max_attempts:
            try:
                self.driver.maximize_window()
                self.driver.get(url)
                # last_name_input = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#LastName")))
                time.sleep(5)

                # Find the input field and enter the keyword "aa"
                last_name_input = self.driver.find_element(By.CSS_SELECTOR, "#LastName")
                last_name_input.send_keys(lastname)

                # Find the button and click it
                search_button = self.driver.find_element(By.CSS_SELECTOR, "#NAME")
                search_button.click()

                # Wait for the results page to load
                # self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainContent > div > div.table-responsive > table")))
                i = start_page
                if debugging == 0:
                    debugging = start_page  # for debugging
                    time.sleep(8)  # Adjust sleep time as necessary
                else:
                    time.sleep(4)
                while i < start_page + per_thread:
                    debugging = i
                    base_url = "https://registry.cno.org/Search/SearchResultsPartial?page={}&sortBy=lastname&sortAsync=True&usePagingCookie=True"
                    base_url = base_url.format(i)
                    self.driver.get(base_url)
                    time.sleep(3)
                    # Scrape data
                    self.scrape_table(data_array)

                    i = i + 1
                print(
                    f"----------------Success------------------------{lastname}, {start_page}"
                )
                break
            except Exception as e:
                print(
                    f"----------------Retry------------------------ no {attempts} => {lastname}, {start_page}, {debugging}"
                )
                if start_page == debugging:
                    attempts += 1
                else:
                    break
        self.close_driver()

    def scrape_table(self, data_array):
        table = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#mainContent > div > div.table-responsive > table")
            )
        )
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "td")
            row_data = []
            for cell in cells:
                # Check if the cell contains an <a> element
                a_tag = (
                    cell.find_element(By.CSS_SELECTOR, "a")
                    if cell.find_elements(By.CSS_SELECTOR, "a")
                    else None
                )
                if a_tag:
                    row_data.append(a_tag.text.strip())
                    url = a_tag.get_attribute("href")
                else:
                    row_data.append(cell.text.strip())
            if url:
                data_array[url] = row_data

    # Close the WebDriver instance
    def close_driver(self):
        self.driver.quit()
