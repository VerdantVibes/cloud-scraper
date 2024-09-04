from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from undetected_chromedriver.options import ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import pandas as pd

class WebScraper:
    # Create a WebScraper instance
    def __init__(self):
        self.driver = self.initialize_driver()
        self.wait = WebDriverWait(self.driver, 10)  # Added explicit wait

    # Init the WebScraper instance
    def initialize_driver(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("--incognito")
        # chrome_options.add_argument("--headless")  # Run headless if you don't need to see the browser
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
        }
        chrome_options.add_experimental_option("prefs", prefs)

        # Initialize undetected ChromeDriver
        driver = uc.Chrome(options=chrome_options)
        return driver

    # Scrape the website
    def scrape_website(self, url, lastname, thread_id):
        try:
            self.driver.maximize_window()
            self.driver.get(url)
            time.sleep(5)
            
            # Find the input field and enter the keyword "aa"
            last_name_input = self.driver.find_element(By.CSS_SELECTOR, "#LastName")
            last_name_input.send_keys(lastname)

            # Find the button and click it
            search_button = self.driver.find_element(By.CSS_SELECTOR, "#NAME")
            search_button.click()

            # Wait for the results page to load
            time.sleep(5)  # Adjust sleep time as necessary

            all_data = []
            headers = ["Name", "Name Link", "Facility", "City", "Type", "Practice Information"]
            while True:
                # Scrape data
                data = self.scrape_table()
                all_data.extend(data)
                
                # Save data to CSV
                self.save_to_csv(headers, all_data, f'{thread_id}_data.csv')
                
                # Check if there is a next button and click it
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, "#mainContent > div > div.pagination > a")
                    next_button.click()
                    
                    # Wait for the next page's table to load
                    # WebDriverWait(self.driver, 10).until(
                    #     EC.presence_of_element_located((By.CSS_SELECTOR, "#mainContent > div > div.table-responsive > table"))
                    # )
                    time.sleep(3) # not professional
                except:
                    break  # Exit the loop if there is no next button

            # Get the page source of the results page
            # result_html = self.driver.page_source
            
        except Exception as e:
            print(e)
        finally:
            self.close_driver()

    def scrape_table(self):
        table = self.driver.find_element(By.CSS_SELECTOR, "#mainContent > div > div.table-responsive > table")
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
        data = []
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "td")
            row_data = []
            for cell in cells:
                # Check if the cell contains an <a> element
                a_tag = cell.find_element(By.CSS_SELECTOR, "a") if cell.find_elements(By.CSS_SELECTOR, "a") else None
                if a_tag:
                    row_data.append(a_tag.text.strip())
                    row_data.append(a_tag.get_attribute("href"))
                else:
                    row_data.append(cell.text.strip())
            data.append(row_data)
        return data
    
    # Save the result  to a csv file
    def save_to_csv(self, headers, rows, filename):
        directory = self.check_output_directory()
        filename = os.path.join(directory, filename)
        df = pd.DataFrame(rows, columns=headers)
        df.to_csv(filename, index=False)
    

    # Close the WebDriver instance
    def close_driver(self):
        self.driver.quit()

    # Create output directory if does not exist
    def check_output_directory(self):
        # Specify the directory where you want to save the screenshot
        directory = './screenshots'
        # Check if the directory exists
        if not os.path.exists(directory):
            # If the directory doesn't exist, create it
            os.makedirs(directory)
        date_str = datetime.now().strftime('%Y-%m-%d')
        directory = f'output/{date_str}'
        if not os.path.exists(directory):
            os.makedirs(directory)
        return directory
