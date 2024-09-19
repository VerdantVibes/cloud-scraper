import cloudscraper
from ptm_format import splitfullname, fit_phone
from bs4 import BeautifulSoup
import csv
import threading


class Cloud_Scraper:
    # class init
    def __init__(self, url):
        self.url = url
        self.scraper = cloudscraper.create_scraper()

    # Get current line
    def get_last_seq_number(self, file_path):
        def read_last_non_empty_line(file_path):
            with open(file_path, "rb") as f:
                f.seek(-2, 2)  # Go to the second last byte
                while f.read(1) != b"\n":  # Until EOL is found
                    f.seek(-2, 1)  # Go back another byte
                    if f.tell() == 0:
                        f.seek(0)
                        break
                last_line = f.readline().decode().strip()
                while not last_line:
                    last_line = f.readline().decode().strip()
            return last_line

        def extract_seq_from_line(line):
            if line:
                parts = line.split(",")
                if parts and parts[0].isdigit():
                    return int(parts[0])
            return 0

        last_line = read_last_non_empty_line(file_path)
        return extract_seq_from_line(last_line)

    # Scrape data and save it to //data = {}
    def scrape_data(self, lock):
        try:
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
                        data[key] = value.upper()
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
                            if (
                                len(cols) == 2
                            ):  # Check if the row has exactly two columns
                                data["Specialty Certificate"] = (
                                    cols[0].text.strip().upper()
                                )
                                data["Status"] = cols[1].text.strip().upper()
                                break  # Break after finding the first match

                # Scrape the Name
                name = soup.select_one("#mainContent > div:nth-child(1) > h1")
                if name:
                    name_text = name.text.strip()
                    # Split the name into parts
                    first_name, last_name, suffix = splitfullname(name_text)
                    # Last name is the last factor
                    data["LastName"] = last_name.upper()
                    # First name is everything except the last name
                    data["FirstName"] = first_name.upper()

                # Scrape Extra1
                extra1 = soup.select_one("#mainContent > div:nth-child(1) > h2 > a")
                if extra1:
                    data["Extra1"] = extra1.text.strip().upper()

                rn_employment_section = soup.find("h2", string="RN Employment")
                if rn_employment_section:
                    empolyment_rn = 1
                else:
                    rn_employment_section = soup.find("h2", string="RPN Employment")
                if rn_employment_section:
                    # Traverse to the parent div which contains the required information
                    employment_div = rn_employment_section.find_parent(
                        "div", class_="well"
                    )

                    # Extract address information from the first column
                    if employment_div:
                        address_contents = employment_div.find_all(
                            "div", class_="col-md-6"
                        )
                        data_firm = []
                        data_add1 = []
                        data_city = []
                        data_prov = []
                        data_post = []
                        data_phone = []
                        data_startdate = []
                        data_enddate = []
                        for address_content in address_contents:
                            firm_content = address_content.find("b")
                            if firm_content:
                                data_firm.append(firm_content.text.strip())
                            else:
                                data_firm.append("")
                            address_info = address_content.find("p").contents
                            data_add1.append(
                                address_info[4].strip()
                            )  # Extract the address line
                            CityProv = address_info[6].strip()
                            if ", " in CityProv:
                                parts = CityProv.split(", ")
                                city = parts[0]
                                prov = (
                                    parts[1]
                                    if len(parts) > 1 and parts[1] != ""
                                    else (parts[2] if len(parts) > 2 else None)
                                )
                                data_city.append(city)
                                data_prov.append(prov)
                            else:
                                # Handle the case where there is no comma
                                data_city.append(CityProv)
                                data_prov.append("")
                            try:
                                post_data = address_info[8].strip()
                                if post_data:
                                    post_data = post_data.replace(" ", "").upper()
                                    data_post.append(
                                        post_data
                                    )  # Extract the postal code, remove spaces, and convert to uppercase
                                else:
                                    data_post.append("")
                            except:
                                data_post.append("")
                            Phone = address_info[12].strip()
                            if Phone:
                                phone_digits = fit_phone(Phone)
                                data_phone.append(
                                    phone_digits
                                )  # Extract the phone number
                            else:
                                data_phone.append("")

                        # Iterate over the div elements to extract start and end dates
                        date_divs = employment_div.find_all("div", class_="col-md-3")
                        # Iterate over the div elements to extract start and end dates
                        for div in date_divs:
                            strong_tag = div.find("strong")
                            if strong_tag and "Start Date" in strong_tag.text:
                                # Extract the start date by navigating through the <br> tag
                                start_date = strong_tag.find_next(
                                    "br"
                                ).next_sibling.strip()
                                data_startdate.append(start_date)
                            elif strong_tag and "End Date" in strong_tag.text:
                                # Extract the end date by navigating through the <br> tag
                                try:
                                    end_data_div = strong_tag.find_next("br")
                                    if end_data_div:
                                        end_date = (
                                            strong_tag.find_next(
                                                "br"
                                            ).next_sibling.strip()
                                            if strong_tag.find_next_sibling(
                                                "br"
                                            ).next_sibling
                                            else ""
                                        )
                                        if end_date:
                                            data_enddate.append(end_date)
                                except:
                                    data_enddate.append("")
                        # New lists to store the modified data
                        new_firm = []
                        new_add1 = []
                        new_city = []
                        new_prov = []
                        new_post = []
                        new_phone = []
                        new_startdate = []
                        new_enddate = []
                        # Process each entry in the input lists
                        for i in range(len(data_firm)):
                            # Split the phone numbers for the ith firm
                            phones = data_phone[i].split(";")
                            # Create new entries for each phone number
                            for phone in phones:
                                new_firm.append(data_firm[i].upper())
                                new_add1.append(data_add1[i].upper())
                                new_city.append(data_city[i].upper())
                                new_prov.append(data_prov[i].upper())
                                new_post.append(data_post[i].upper())
                                new_phone.append(
                                    phone.strip().upper()
                                )  # Strip to remove any extra spaces
                                new_startdate.append(data_startdate[i].upper())
                                new_enddate.append(data_enddate[i].upper())
                        for i in range(len(new_firm)):
                            with lock:
                                last_line = self.get_last_seq_number("scrape_data.csv")
                                res_data = [
                                    last_line + 1,
                                    data.get("LastName"),
                                    data.get("FirstName"),
                                    "",
                                    "",
                                    new_firm[i],
                                    new_add1[i],
                                    "",
                                    new_city[i],
                                    new_prov[i],
                                    new_post[i],
                                    new_phone[i],
                                    "",
                                    "",
                                    "",
                                    data.get("Registration Status"),
                                    "",
                                    data.get("Registration Number"),
                                    "",
                                    "",
                                    data.get("Category"),
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    data.get("Extra1"),
                                    new_startdate[i],
                                    new_enddate[i],
                                    data.get("Class"),
                                    data.get("Initial Registration with CNO"),
                                    data.get("Specialty Certificate"),
                                    data.get("Status"),
                                    "",
                                    "",
                                ]
                                with open(
                                    "scrape_data.csv", "a", newline="", encoding="utf-8"
                                ) as nsf:
                                    writer = csv.writer(nsf)
                                    writer.writerow(
                                        res_data
                                    )  # Append res_data as a new row in the CSV file
                        if len(new_firm) == 0:
                            with lock:
                                last_line = self.get_last_seq_number("scrape_data.csv")
                                res_data = [
                                    last_line + 1,
                                    data.get("LastName"),
                                    data.get("FirstName"),
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    data.get("Registration Status"),
                                    "",
                                    data.get("Registration Number"),
                                    "",
                                    "",
                                    data.get("Category"),
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    data.get("Extra1"),
                                    "",
                                    "",
                                    data.get("Class"),
                                    data.get("Initial Registration with CNO"),
                                    data.get("Specialty Certificate"),
                                    data.get("Status"),
                                    "",
                                    "",
                                ]
                                with open(
                                    "scrape_data.csv", "a", newline="", encoding="utf-8"
                                ) as nsf:
                                    writer = csv.writer(nsf)
                                    writer.writerow(
                                        res_data
                                    )  # Append res_data as a new row in the CSV file
                    else:
                        with lock:
                            last_line = self.get_last_seq_number("scrape_data.csv")
                            res_data = [
                                last_line + 1,
                                data.get("LastName"),
                                data.get("FirstName"),
                                "",
                                "",
                                "",
                                "",
                                "",
                                "",
                                "",
                                "",
                                "",
                                "",
                                "",
                                "",
                                data.get("Registration Status"),
                                "",
                                data.get("Registration Number"),
                                "",
                                "",
                                data.get("Category"),
                                "",
                                "",
                                "",
                                "",
                                "",
                                "",
                                "",
                                "",
                                "",
                                "",
                                "",
                                data.get("Extra1"),
                                "",
                                "",
                                data.get("Class"),
                                data.get("Initial Registration with CNO"),
                                data.get("Specialty Certificate"),
                                data.get("Status"),
                                "",
                                "",
                            ]
                            with open(
                                "scrape_data.csv", "a", newline="", encoding="utf-8"
                            ) as nsf:
                                writer = csv.writer(nsf)
                                writer.writerow(
                                    res_data
                                )  # Append res_data as a new row in the CSV file
                else:
                    with lock:
                        last_line = self.get_last_seq_number("scrape_data.csv")
                        res_data = [
                            last_line + 1,
                            data.get("LastName"),
                            data.get("FirstName"),
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            data.get("Registration Status"),
                            "",
                            data.get("Registration Number"),
                            "",
                            "",
                            data.get("Category"),
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            data.get("Extra1"),
                            "",
                            "",
                            data.get("Class"),
                            data.get("Initial Registration with CNO"),
                            data.get("Specialty Certificate"),
                            data.get("Status"),
                            "",
                            "",
                        ]
                        with open(
                            "scrape_data.csv", "a", newline="", encoding="utf-8"
                        ) as nsf:
                            writer = csv.writer(nsf)
                            writer.writerow(res_data)

                print(f"Sucess-----{self.url}-------")
            else:
                print(f"failed to cloud_scraper--------{self.url}----------")
                return None
        except:
            print(f"failed to cloud_scraper------{self.url}---------")
            return None

    # Run Scraper
    def run(self, lock):
        self.scrape_data(lock)

    # Close scraper
    def close_scraper(self):
        self.scraper.close()


# lock = threading.Lock()
# url = "https://registry.cno.org/Search/Details/0a90160a-4ab8-4155-a83c-be5dc1b8a3cc"
# scraper = Cloud_Scraper(url)
# scraper.run(lock)
# scraper.close_scraper()
