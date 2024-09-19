from concurrent.futures import ThreadPoolExecutor
from cloud_scraper import Cloud_Scraper
import queue
import threading
import logging
import csv
import pandas as pd

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

max_scrapeworkers = 10
data_check = {}


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


# Backup from "check.csv"
def main():
    task_queue = queue.Queue()

    chunksize = 10000  # Adjust this value based on your system's memory capacity
    url_list = []

    # Read the file in chunks
    for chunk in pd.read_csv("check.csv", usecols=["url"], chunksize=chunksize):
        # Extend the url_list with URLs from the current chunk
        url_list.extend(chunk["url"].tolist())

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
