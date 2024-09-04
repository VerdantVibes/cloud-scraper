from uc_scraper import WebScraper
from concurrent.futures import ThreadPoolExecutor
import string
import queue
import threading
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def worker(task_queue, url):
    while not task_queue.empty():
        try:
            idx, keyword = task_queue.get_nowait()
            scraper = WebScraper()
            logging.info(f"Thread {threading.current_thread().name} processing keyword: {keyword}")
            scraper.scrape_website(url, keyword, idx)
            task_queue.task_done()
        except queue.Empty:
            break
        except Exception as e:
            logging.error(f"Error occurred: {e}")

def parallel_controller(keywords):
    url = "https://registry.cno.org/Search/Search"
    task_queue = queue.Queue()

    # Enqueue all tasks
    for idx, keyword in enumerate(keywords):
        task_queue.put((idx, keyword))

    # Use ThreadPoolExecutor to manage parallel execution
    max_workers = 4
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for _ in range(max_workers):
            executor.submit(worker, task_queue, url)

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

def main():
    # Generate Keywords for Last Name
    keywords = generate_keywords()
    print(keywords)
    logging.info(f"Generated {len(keywords)} keywords")
    
    # Thread function to parallel webdriver functionality
    parallel_controller(keywords)

if __name__ == "__main__":
    main()
