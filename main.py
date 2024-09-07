from uc_scraper import WebScraper
from concurrent.futures import ThreadPoolExecutor
from cloud_scraper import Cloud_Scraper
import pandas as pd
import string
import queue
import threading
import logging
import tempfile

lock = threading.Lock()
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

data_array = {}

def create_unique_temp_directory():
    with lock:
        driver_temp_dir = tempfile.mkdtemp()
    return driver_temp_dir
per_thread = 15 # pages one thread execute
def worker(task_queue, url, user_data_dir):
    while not task_queue.empty():
        try:
            idx, keyword, start_page = task_queue.get_nowait()
            scraper = WebScraper(user_data_dir)
            logging.info(f"Thread {idx} processing keyword: {keyword}, {start_page}")
            scraper.scrape_website(url, keyword, data_array, start_page, per_thread)
            task_queue.task_done()
        except queue.Empty:
            break
        except Exception as e:
            logging.error(f"Error occurred: {e}")

def parallel_controller(keywords):
    url = "https://registry.cno.org/Search/Search"
    task_queue = queue.Queue()

    # # Enqueue all tasks
    # for idx, keyword in enumerate(keywords):
    #     task_queue.put((idx, keyword))
    for idx, keyword in enumerate(keywords):
        for value in range(1, 151, per_thread):
            task_queue.put((idx, keyword, value))

    # Use ThreadPoolExecutor to manage parallel execution
    max_workers = 5
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i in range(max_workers):
            user_data_dir = create_unique_temp_directory()
            executor.submit(worker, task_queue, url, user_data_dir)

    # Wait for all tasks to be processed
    task_queue.join()

def generate_keywords():
    keywords = []
    alphabets = string.ascii_lowercase
    vowels = ['a', 'e', 'i', 'o', 'u', 'y', 'w']
    
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

# save data using Cloud_Scraper
def process_cloudscraper_url(url, data_list, lock):
    print(url)
    scraper = Cloud_Scraper(url)
    data = scraper.run()
    
    with lock:
        data_list.append({
            "seq": len(data_list) + 1,
            "first": data.get("FirstName"),
            "last": data.get("LastName"),
            "b1": data.get("Category"),
            "lic": data.get("Registration Number"),
            "status": data.get("Registration Status"),
            "addr1": data.get("Address1"),
            "city": data.get("City"),
            "prov": data.get("Prov"),
            "post": data.get("Post"),
            "phone": data.get("Phone"),
            "extra1_status": data.get("Extra1"),
            "extra2_initial_registration": data.get("Start Date"),
            "extra3_prescribe_fields": data.get("End Date"),
            "extra4": data.get("Class"),
            "extra5_permit_issued": data.get("Initial Registration with CNO"),
            "extra6": data.get("Specialty Certificate"),
            "extra7": data.get("Status"),
        })



def scrape_data(task_queue, data_list, lock):
    while not task_queue.empty():
        try:
            url = task_queue.get_nowait()
            process_cloudscraper_url(url, data_list, lock)
            task_queue.task_done()
        except queue.Empty:
            break
        except Exception as e:
            logging.error(f"Error occurred: {e}")

def main():
    # Generate Keywords for Last Name
    keywords = generate_keywords()
    # keywords = ["aa"]
    print(keywords)
    logging.info(f"Generated {len(keywords)} keywords")
    
    # Thread function to parallel webdriver functionality
    parallel_controller(keywords)
    
    data_list = []
    task_queue = queue.Queue()
    # get detail data from date_array
    url_list = list(data_array.keys())
    for url in url_list:
        task_queue.put(url)
    
    # Create and start 4 scrapingdata threads
    max_scrapeworkers = 10
    with ThreadPoolExecutor(max_workers=max_scrapeworkers) as executor:
        for i in range(max_scrapeworkers):
            executor.submit(scrape_data, task_queue, data_list, lock)
        
    df = pd.DataFrame(
        columns=[
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
    )
    print("finished")
    for new_data in data_list:
        try:
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
    
    df.to_excel("scraped_data.xlsx", index=False)

if __name__ == "__main__":
    main()
