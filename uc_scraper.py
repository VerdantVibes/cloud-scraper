import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from undetected_chromedriver.options import ChromeOptions

# Set up Chrome options to ignore images and CSS
chrome_options = ChromeOptions()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--incognito")
# chrome_options.add_argument("--headless")  # Run headless if you don't need to see the browser
prefs = {
    "profile.managed_default_content_settings.images": 2,
    "profile.managed_default_content_settings.stylesheets": 2,
}
chrome_options.add_experimental_option("prefs", prefs)

# Initialize undetected ChromeDriver
driver = uc.Chrome(options=chrome_options)

try:
    # Visit the website
    driver.get("https://registry.cno.org/Search/Search")

    time.sleep(5)
    # Find the input field and enter the keyword "aa"
    last_name_input = driver.find_element(By.CSS_SELECTOR, "#LastName")
    last_name_input.send_keys("aa")

    # Find the button and click it
    search_button = driver.find_element(By.CSS_SELECTOR, "#NAME")
    search_button.click()

    # Wait for the results page to load
    time.sleep(5)  # Adjust sleep time as necessary

    # Get the page source of the results page
    result_html = driver.page_source

    # Print or save the result HTML
    print(result_html)

finally:
    # Close the browser
    driver.quit()
