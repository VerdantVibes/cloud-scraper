import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import os
import re


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
            tables = soup.select("#general table")

            # Iterate through each table and check for the headers you're interested in
            for table in tables:
                headers = table.find_all("th")
                if (
                    headers
                    and "Specialty Certificate" in headers[0].text
                    and "Status" in headers[1].text
                ):
                    # Table with the right headers found, now extract the data
                    rows = table.find_all("tr")
                    for row in rows[1:]:  # Skip the header row
                        cols = row.find_all("td")
                        if len(cols) == 2:  # Check if the row has exactly two columns
                            data["Specialty Certificate"] = cols[0].text.strip()
                            data["Status"] = cols[1].text.strip()
                            break  # Break after finding the first match

            # Scrape the Name
            name = soup.select_one("#mainContent > div:nth-child(1) > h1").text.strip()
            name_parts = name.split()
            data["FirstName"] = name_parts[0]
            data["LastName"] = (
                " ".join(name_parts[2:]) if len(name_parts) > 2 else name_parts[1]
            )

            # Scrape Extra1
            extra1 = soup.select_one(
                "#mainContent > div:nth-child(1) > h2 > a"
            ).text.strip()
            data["Extra1"] = extra1

            rn_employment_section = soup.find("h2", string="RN Employment")
            if rn_employment_section:
                empolyment_rn = 1
            else:
                rn_employment_section = soup.find("h2", string="RPN Employment")
            if rn_employment_section:
                # Traverse to the parent div which contains the required information
                employment_div = rn_employment_section.find_parent("div", class_="well")

                # Extract address information from the first column
                address_info = (
                    employment_div.find("div", class_="col-md-6").find("p").contents
                )
                data["Address1"] = address_info[4].strip()  # Extract the address line
                CityProv = address_info[6].strip()
                if ", " in CityProv:
                    city, prov = CityProv.split(", ")
                    data["City"] = city
                    data["Prov"] = prov
                else:
                    # Handle the case where there is no comma
                    data["City"] = CityProv
                    data["Prov"] = "" 
                data["Post"] = address_info[8].strip()  # Extract the postal code
                Phone = address_info[12].strip()
                if Phone:
                    phone_digits = re.sub(r"\D", "", Phone)
                    data["Phone"] = phone_digits  # Extract the phone number

                # Extract Start Date from the second column
                start_date_div = employment_div.find("div", class_="col-md-3")
                data["Start Date"] = start_date_div.find_next("br").next_sibling.strip()

                # Extract End Date from the third column (if available)
                end_date_div = start_date_div.find_next_sibling("div")
                end_date = (
                    end_date_div.find_next("br").next_sibling.strip()
                    if end_date_div.find_next("br").next_sibling
                    and end_date_div.find_next("br").next_sibling.strip()[0].isdigit()
                    else ""
                )
                data["End Date"] = end_date.strip() if end_date else ""

            return data
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return None

    # save to excel file
    def save_to_excel(self, data):
        file_name = "scraped_data.xlsx"
        # make or add file part
        if os.path.exists(file_name):
            df_existing = pd.read_excel(file_name)
            if "seq" in df_existing.columns:
                next_seq = df_existing["seq"].max() + 1
            else:
                next_seq = 1
            df = pd.read_excel(file_name)
        else:
            next_seq = 1
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

        new_data = {
            "seq": next_seq,
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
        }

        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_excel(file_name, index=False)

    def run(self):
        data = self.scrape_data()
        return data
        # if data:
            # self.save_to_excel(data)


# Example usage
# url = "https://registry.cno.org/Search/Details/332d3902-ed7c-4275-b115-76eaa7cfaa2a"
# scraper = Cloud_Scraper(url)
# scraper.run()
