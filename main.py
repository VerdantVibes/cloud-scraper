from uc_scraper import WebScraper
from concurrent.futures import ThreadPoolExecutor
from cloud_scraper import Cloud_Scraper
import string
import queue
import threading
import logging
import tempfile
import time
import getpass
import csv

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

max_workers = 3
per_thread = 10  # pages one thread execute
max_scrapeworkers = 10

data_array = {}
data_check = {}
new_data_array = {}
header = ["url"]
lock = threading.Lock()
worker_thread = threading.Lock()
websitescp_thread = threading.Lock()


# Save data from url using Cloud_Scraper
def process_cloudscraper_url(url, lock):
    scraper = Cloud_Scraper(url)
    scraper.run(lock)
    scraper.close_scraper()


# Scrape dats from each urls
def scrape_data(task_queue, lock):
    while not task_queue.empty():
        try:
            url = task_queue.get_nowait()
            process_cloudscraper_url(url, lock)
            task_queue.task_done()
        except queue.Empty:
            break
        except Exception as e:
            print(url)
            logging.error(f"scrape_data Error occurred: {e}")


# Scrpe url data
def worker(task_queue, url, user_data_dir, UserName):
    with worker_thread:
        time.sleep(2)
    while not task_queue.empty():
        try:
            _, keyword, start_page = task_queue.get_nowait()
            scraper = WebScraper(user_data_dir, UserName)
            scraper.scrape_website(
                url, keyword, data_array, start_page, per_thread, websitescp_thread
            )
            task_queue.task_done()
        except queue.Empty:
            break
        except Exception as e:
            logging.error(f"worker Error occurred: {e}")


# Create unique chromedriver
def create_unique_temp_directory():
    with lock:
        driver_temp_dir = tempfile.mkdtemp()
    return driver_temp_dir


# Running with thread logic
def parallel_controller(keywords):
    url = "https://registry.cno.org/Search/Search"
    task_queue = queue.Queue()

    for idx, keyword in enumerate(keywords):
        for value in range(1, 152, per_thread):
            task_queue.put((idx, keyword, value))

    UserName = getpass.getuser()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i in range(max_workers):
            user_data_dir = create_unique_temp_directory()
            executor.submit(worker, task_queue, url, user_data_dir, UserName)

    # Wait for all tasks to be processed
    task_queue.join()


# Generate lastname
def generate_keywords():
    keywords = []
    alphabets = string.ascii_lowercase
    vowels = ["a", "e", "i", "o", "u", "y", "w"]

    # Generate keywords combining alphabets and vowels
    for alpha1 in alphabets:
        for vowel in vowels:
            search_string = alpha1 + vowel
            if search_string not in keywords:
                keywords.append(search_string)

    for vowel in vowels:
        for alpha1 in alphabets:
            search_string = vowel + alpha1
            if search_string not in keywords:
                keywords.append(search_string)

    return keywords


# Scrape data
def main():
    # Generate Keywords for Last Name
    keywords = generate_keywords()
    # keywords = ["aa"]
    print(keywords)
    logging.info(f"Generated {len(keywords)} keywords")

    # Thread function to parallel webdriver functionality
    parallel_controller(keywords)

    task_queue = queue.Queue()
    # get detail data from date_array
    file_name = "check.csv"
    with open(file_name, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
    print("Saving... Please wait before close")

    url_list = list(data_array.keys())
    for url in url_list:
        if data_array[url]:
            with open(file_name, mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([url])

    data_checkurl = {}
    # Populate the task queue with unique URLs
    for url in url_list:
        if data_checkurl.get(url) == 1:
            continue
        else:
            data_checkurl[url] = 1
            task_queue.put(url)
    df = [
        "seq",
        "last",
        "first",
        "suff",
        "off",
        "firm",
        "addr1",
        "addr2",
        "city",
        "prov",
        "post",
        "phone",
        "fax",
        "fax_p",
        "ext",
        "status",
        "gend",
        "lic",
        "lic_p",
        "f",
        "b1",
        "b2",
        "i1",
        "i2",
        "i3",
        "i4",
        "email",
        "email_p",
        "email_s",
        "yog",
        "lang",
        "prof",
        "extra1_status",
        "extra2_initial_registration",
        "extra3_prescribe_fields",
        "extra4",
        "extra5_permit_issued",
        "extra6",
        "extra7",
        "ims",
        "pref",
    ]
    with open("scrape_data.csv", "a", newline="", encoding="utf-8") as nsf:
        writer = csv.writer(nsf)
        writer.writerow(df)
    # Create and start 4 scrapingdata threads

    scrape_lock = threading.Lock()
    with ThreadPoolExecutor(max_workers=max_scrapeworkers) as executor:
        for i in range(max_scrapeworkers):
            executor.submit(scrape_data, task_queue, scrape_lock)


# Do main function
if __name__ == "__main__":
    main()
