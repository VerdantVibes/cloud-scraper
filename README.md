# Nurse Registry Web Scraper

![Web Scraping](https://img.shields.io/badge/Web%20Scraping-Python-blue)
![Python](https://img.shields.io/badge/Python-3.7%2B-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)


A highly efficient and multithreaded web scraper to collect and process nurse data from a targeted nurse registry website.

## **Table of Contents**

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Detailed Overview of uc_scraper.py](#detailed-overview-of-uc_scraperpy)
- [Detailed Overview of cloud_scraper.py](#detailed-overview-of-cloud_scraperpy)
- [Detailed Overview of ptm_format.py](#detailed-overview-of-ptm_formatpy)
- [Configuration](#configuration)

## ***Introduction***

The project is designed to scrape data from a specific nurse registry website. Using advanced multithreading techniques, the project aims to efficiently scrape and store data in a CSV file, breaking down the task into smaller parallel tasks for optimized performance.

## ***Features***

- **Multithreaded Scraping**: Leverages Python's `concurrent.futures.ThreadPoolExecutor` for efficient multithreading.
- **Data Storage**: Stores scraped data into CSV files for easy access and analysis.
- **Dynamic User-Agent**: Uses temporary directories for unique web scraping sessions.
- **Keyword Generation**: Automatically generates keyword combinations to search through the nurse registry.
- **Retry Mechanism**: Implements retry logic in case of failures during data scraping.

## ***Installation***
**Install required dependencies**
Make sure you have Python 3.7+ and pip installed.

```sh
pip install -r requirements.txt
```

## ***Usage***
1. **Run the Scraper**
Simply execute the main.py script to start the scraping process:
    ```sh
    python main.py
    ```

2. **Configuration**
You can adjust the number of threads and other settings within the main.py script to fit your requirements.

## ***Project Structure***
```sh
nurse-web-scraper/
│    
├── uc_scraper.py
├── cloud_scraper.py
├── main.py
├── ptm_format.py
├── requirements.txt
└── README.md
```

`main.py`: Main script that orchestrates the entire scraping process.<br>
`uc_scraper.py`: Script for scraping using the undetected Chromedriver, focusing on extracting data from the registry tables.<br>
`cloud_scraper.py:` Script for scraping using a cloud-based scraper.<br>
`ptm_format.py`: Utility functions for name splitting and phone formatting.<br>
`requirements.txt`: File containing all the required Python packages.<br>
`README.md`: Documentation<br>

## ***Detailed Overview of uc_scraper.py***
The `uc_scraper.py` file contains the WebScraper class, which utilizes the undetected Chromedriver to scrape nurse data. Here’s a breakdown of its functionality:

### **Initialization:**

- `__init__`: Sets up the WebScraper instance with a WebDriver and WebDriverWait.
- `initialize_driver`: Configures and initializes the undetected Chromedriver with specific options.

### **Web Scraping Methods:**

- `scrape_table`: Extracts data from the HTML table in the webpage.
- `scrape_website`: Navigates through the pages of the website to perform searches and collect data, implementing retry logic in case of failures.

### **Utility Methods:**

- `close_driver`: Closes the WebDriver instance.

## ***Detailed Overview of cloud_scraper.py***
The `cloud_scraper.py` file contains the `Cloud_Scraper` class, which uses `cloudscraper` to bypass anti-bot measures and scrape nurse data. Here's a breakdown of its functionality:

### Initialization:

- `__init__`: Sets up the Cloud_Scraper instance with a cloudscraper instance and URL.
- `Dynamic User-Agent`: Uses the cloudscraper library to create a scraper instance that dynamically changes the User-Agent to avoid detection.

### Helper Method: 

- `get_last_seq_number`: Reads the last non-empty line from a file to determine the current sequence number for appending data.
    - Uses nested helper functions read_last_non_empty_line and extract_seq_from_line for reading and processing the sequence number.
### Web Scraping Method:

- `scrape_data`: Scrapes data from the specified URL and processes the HTML content using BeautifulSoup to extract relevant data fields. The extracted data is then stored in a dictionary and written to a CSV file. The method handles a variety of data points including name, specialty certificate, status, and employment details:
    - Extracts table data.
    - Scrapes name, specialty, and status information.
    - Extracts employment details with address, phone number, and dates.
    - Writes the data to `scrape_data.csv`.
### Run and Close Methods:

- `run`: Initiates the scraping process, typically wrapped with a lock for thread-safety.
- `close_scraper`: Closes the cloudscraper instance.

## ***Detailed Overview of ptm_format.py***
The `ptm_format.py` file contains utility functions for processing names and phone numbers. Here's a breakdown of its functionality:

- Function `splitfullname(fullname)`:

    - Splits the provided full name into first name, last name, and suffix.
    - Handles various prefixes (e.g., "Dr.", "Mr.") and suffixes (e.g., "Jr", "III").
    - Accounts for multiple word last names (e.g., "Van", "De La").
- Function `fit_phone(Phone)`:

    - Normalizes and formats phone numbers to a consistent digit-only format.
    - Removes extraneous characters and normalizes additional occurrences of country code prefixes (e.g., "+1", "1").
## ***Configuration***
### Parameters
- `per_thread`: Number of pages a single thread will process.
- `max_workers`: Maximum number of worker threads for website scraping.
- `max_scrapeworkers`: Maximum number of worker threads for data scraping.
### Logging
Logs are generated to provide insight into the scraping process, errors, and overall progress.

### CSV Output
Scraped data is saved into a file named scrape_data.csv. Make sure to delete or rename this file if you want to start a fresh scrape to avoid appending existing data.

### *Happy Scraping!* 🕸️
