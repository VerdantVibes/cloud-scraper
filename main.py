import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import os


class Cloud_Scraper:
    # class init
    def __init__(self, url):
        self.url = url
        self.scraper = cloudscraper.create_scraper()

    # scrape data and save it to //data = {}
    def scrape_data(self):
        response = self.scraper.get(self.url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.select_one("#general > div > div > table")
            rows = table.find_all("tr")
            # scrape table field
            data = {}
            for row in rows:
                columns = row.find_all("td")
                if len(columns) == 2:
                    key = columns[0].text.strip()
                    value = columns[1].text.strip()
                    data[key] = value

            # Scrape the Name
            name = soup.select_one("#mainContent > div:nth-child(1) > h1").text.strip()
            data["Name"] = name

            return data
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return None

    # save to excel file
    def save_to_excel(self, data):
        file_name = "scraped_data.xlsx"
        # make or add file part
        if os.path.exists(file_name):
            df = pd.read_excel(file_name)
        else:
            df = pd.DataFrame(
                columns=[
                    "Name",
                    "Category",
                    "Class",
                    "Registration Number",
                    "Registration Status",
                    "Initial Registration with CNO",
                ]
            )

        new_data = {
            "Name": data.get("Name"),
            "Category": data.get("Category"),
            "Class": data.get("Class"),
            "Registration Number": data.get("Registration Number"),
            "Registration Status": data.get("Registration Status"),
            "Initial Registration with CNO": data.get("Initial Registration with CNO"),
        }

        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_excel(file_name, index=False)

    def run(self):
        data = self.scrape_data()
        if data:
            self.save_to_excel(data)


# Example usage
url = "https://registry.cno.org/Search/Details/332d3902-ed7c-4275-b115-76eaa7cfaa2a"
scraper = Cloud_Scraper(url)
scraper.run()
