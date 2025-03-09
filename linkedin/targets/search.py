from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from linkedin.targets.types import Company, Group, Job, Person, Post, Product



class Search:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.jobs = []
        self.posts = []
        self.people = []
        self.companies = []
        self.groups = []
        self.products = []
        self.fields = {}
    def add_job(self, job):
        self.jobs.append(job)

    def add_post(self, post):
        self.posts.append(post)

    def add_person(self, person):
        self.people.append(person)

    def add_company(self, company):
        self.companies.append(company)

    def add_group(self, group):
        self.groups.append(group)

    def add_product(self, product):
        self.products.append(product)

    def add_field(self, name, target_id):
        self.fields[name] = target_id

    def execute_search(self, search_query):
        try:
            formatted_search_query = search_query.replace(" ", "%20")
            self.driver.get(f"https://www.linkedin.com/search/results/all/?keywords={formatted_search_query}&origin=GLOBAL_SEARCH_HEADER")
        except:
            print(f"Error searching query: {search_query}")
            return None
        
    def scrape_sidebar_fields(self):
        try:

            sidebar = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.scaffold-layout__sidebar")
            ))
            on_page_header = sidebar.find_element(By.XPATH, ".//h2[contains(text(), 'On this page')]")
            parent_section = on_page_header.find_element(By.XPATH, "./ancestor::section")
            buttons = parent_section.find_elements(By.TAG_NAME, "button")

            for button in buttons:
                field_text = button.text.strip()
                data_target = button.get_attribute("data-target-section-id")
                self.add_field(field_text, data_target)
                print(f"Found field: {field_text} with target id: {data_target}")
            return self.fields
        except Exception as e:
            print("Error scraping sidebar fields:", e)
            return {}
        

    def scrape_jobs_section(self, section_id):
        """
        Scrapes the Jobs section using more stable selectors.
        Returns a list of dictionaries with keys:
        - job_title
        - company
        - location
        - time_posted
        """

        # Wait until the section container loads by its stable ID.
        container = self.wait.until(EC.presence_of_element_located((By.ID, section_id)))
        
        # Use the data attribute to identify job cards:
        job_cards = container.find_elements(
            By.XPATH,
            ".//div[contains(@data-chameleon-result-urn, 'urn:li:job:') and contains(@data-view-name, 'search-entity-result-universal-template')]"
        )
        
        for card in job_cards:
            try:
                # Instead of using a class like 't-16', look for the first <a> element whose href contains 'currentJobId'
                job_title_elem = card.find_element(
                    By.XPATH, ".//a[contains(@href, 'currentJobId') and not(descendant::img)]"
                )
                job_title = job_title_elem.text.strip().replace(" \n, Verified", "")
                job_link  = job_title_elem.get_attribute("href")
            except Exception:
                print("Error getting job title")
                job_title = ""
                job_link = ""
            
            try:
                linked_area = card.find_element(By.XPATH, ".//div[contains(@class, 'linked-area')]/div[1]")
                details_container = linked_area.find_element(By.XPATH, "./div[2]/div[1]")

                company = details_container.find_element(By.XPATH, "./div[2]").text.strip()
                location = details_container.find_element(By.XPATH, "./div[3]").text.strip()
            except Exception as e:
                print("Error getting company or location:", e)
                company = ""
                location = ""


            try:
                # Look for an element that contains the text 'ago', which should be part of the time info.
                time_posted_elem = card.find_element(
                    By.XPATH,
                    ".//div[contains(@class, 'entity-result__insights')]/div[contains(., 'ago') and not(contains(., 'alumni'))]"
                )
                time_posted = time_posted_elem.text.strip().replace("\n • \nEasy Apply", "")
            except Exception:
                print("Error getting time posted")
                time_posted = ""
            self.add_job(Job(job_title, job_link, company, location, time_posted))

        return self.jobs

    def scrape_posts_section(self, section_id):
        """
        Scrapes the Posts section.
        Returns a Post object for each post.
        """
        container = self.wait.until(EC.presence_of_element_located((By.ID, section_id)))

        # Adjust this selector to target each post container. Here we assume posts use a class like "feed-shared-update-v2"
        post_cards = container.find_elements(By.CSS_SELECTOR, "div.feed-shared-update-v2")
        for card in post_cards:
            try:
                # poster_name = card.find_element(By.CSS_SELECTOR, 
                #     "a.update-components-actor__meta-link span.update-components-actor__title").text.strip()
                author_wrapper = card.find_element(By.CSS_SELECTOR, 
                    "a.update-components-actor__meta-link span.update-components-actor__title")
                author_name = author_wrapper.find_element(By.XPATH, "./span[1]/span[1]/span[1]").text.strip()
            except Exception:
                author_name = ""
            try:
                author_profile_photo_url = card.find_element(By.CSS_SELECTOR, 
                    "div.ivm-view-attr__img-wrapper img").get_attribute("src")
            except Exception:
                author_profile_photo_url = ""
            try:
                time_since_posted_wrapper = card.find_element(By.CSS_SELECTOR, "span.update-components-actor__sub-description")
                time_since_posted = time_since_posted_wrapper.find_element(By.XPATH, "./span[2]").text.strip()
            except Exception:
                time_since_posted = ""
            try:
                post_content = card.find_element(By.CSS_SELECTOR, "div.update-components-text").text.strip()
            except Exception:
                post_content = ""

            self.add_post(Post(author_name, author_profile_photo_url, time_since_posted, post_content))
        return self.posts

    def scrape_people_section(self, section_id):
        """
        Scrapes the People section.
        Returns a list of dictionaries with keys:
        - name
        - profile_photo_url
        - headline
        - location
        """
        container = self.wait.until(EC.presence_of_element_located((By.ID, section_id)))
        print("Scraping people section...")
        person_cards = container.find_elements(
            By.CSS_SELECTOR, 
            "div[data-chameleon-result-urn^='urn:li:member:']"
        )


        for card in person_cards:
            data_element = card.find_element(By.XPATH, "./div[1]/div[1]")

            profile_picture_wrapper = data_element.find_element(By.XPATH, "./div[1]")
            text_information_wrapper = data_element.find_element(By.XPATH, "./div[2]")


            try:
                name_link_wrapper = text_information_wrapper.find_element(By.XPATH, ".//a[contains(@href, 'miniProfileUrn')]")
                name = name_link_wrapper.find_element(By.XPATH, "./span[1]/span[1]").text.strip()
            except Exception:
                print("Error getting name")
                name = ""
            try:
                photo_a_element = profile_picture_wrapper.find_element(By.TAG_NAME, "a")

                profile_url = photo_a_element.get_attribute("href")
                profile_photo_url = photo_a_element.find_element(By.TAG_NAME, "img").get_attribute("src")
            except Exception:
                print("Error getting profile photo url")
                profile_photo_url = "No photo found"
            try:
                headline_wrapper_element = text_information_wrapper.find_element(By.XPATH, "./div[1]")
                headline_element = headline_wrapper_element.find_element(By.XPATH, "./div[2]")

                headline = headline_element.text.strip()
            except Exception:
                print("Error getting headline")
                headline = ""
            try:
                location = text_information_wrapper.find_element(By.XPATH, "./div[1]/div[3]").text.strip()
            except Exception:
                print("Error getting location")
                location = ""
            self.add_person(Person(name, profile_url, profile_photo_url, headline, location))
        return self.people
    
    def scrape_companies_section(self, section_id):
        """
        Scrapes the Companies section.
        Returns a list of dictionaries with keys:
        - name
        - profile_photo_url
        - headline
        - location
        """
        container = self.wait.until(EC.presence_of_element_located((By.ID, section_id)))
        print("Scraping companies section...")
        company_cards = container.find_elements(
            By.CSS_SELECTOR, 
            "div[data-chameleon-result-urn^='urn:li:company:']"
        )


        for card in company_cards:
            data_element = card.find_element(By.XPATH, "./div[1]/div[1]")

            profile_picture_wrapper = data_element.find_element(By.XPATH, "./div[1]")
            text_information_wrapper = data_element.find_element(By.XPATH, "./div[2]")


            try:
                name_link_wrapper = text_information_wrapper.find_element(By.XPATH, ".//a[contains(@href, 'https://www.linkedin.com/company/')]")
                
                company_name = name_link_wrapper.text.strip()
            except Exception:
                print("Error getting name")
                company_name = ""
            try:
                photo_a_element = profile_picture_wrapper.find_element(By.TAG_NAME, "a")

                profile_url = photo_a_element.get_attribute("href")
                profile_photo_url = photo_a_element.find_element(By.TAG_NAME, "img").get_attribute("src")
            except Exception:
                print("Error getting profile photo url")
                profile_photo_url = "No photo found"
            try:
                headline_wrapper_element = text_information_wrapper.find_element(By.XPATH, "./div[1]")
                headline_element = headline_wrapper_element.find_element(By.XPATH, "./div[2]")

                headline = headline_element.text.strip()
            except Exception:
                print("Error getting headline")
                headline = ""
            try:
                follower_count = text_information_wrapper.find_element(By.XPATH, "./div[1]/div[3]").text.strip()
            except Exception:
                print("Error getting follower_count")
                follower_count = ""
            try:
                description_wrapper = text_information_wrapper.find_element(By.XPATH, "./p")

                description = description_wrapper.text.strip()
            except Exception:
                print("Error getting description")
                description = ""
            self.add_company(Company(company_name, profile_url, profile_photo_url, headline, follower_count, description))
        return self.companies

            
    def search(self, search_query):
        _ = self.execute_search(search_query)

        # Scrape the sidebar to see what sections are present.
        sidebar_fields = self.scrape_sidebar_fields()
        
        # Map the sidebar field names to the corresponding scraper functions.
        scrape_function_map = {
            "Jobs": self.scrape_jobs_section,
            "Posts": self.scrape_posts_section,
            "People": self.scrape_people_section,
            "Companies": self.scrape_companies_section,
        }
        
        
        # Iterate through each field found in the sidebar.
        for field, section_id in sidebar_fields.items():
            if field in scrape_function_map:
                try:
                    # Click the sidebar button for this section.
                    button = self.driver.find_element(By.CSS_SELECTOR, f"button[data-target-section-id='{section_id}']")
                    button.click()
                    # Wait for the main section to load (by waiting for an element with the section's ID).
                    self.wait.until(EC.presence_of_element_located((By.ID, section_id)))
                    # Optionally scroll the section into view.
                    section = self.driver.find_element(By.ID, section_id)
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", section)
                    # Call the appropriate scraping function.
                    print(f"Scraping {field} section...")
                    _ = scrape_function_map[field](section_id)
                except Exception as e:
                    print(f"Error processing section '{field}': {e}")
        return