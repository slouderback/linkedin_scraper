import time
import json
import csv
import random
import os
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from utils.auth import LinkedInAuth
from utils.robot_handler import RobotHandler

class LinkedInScraper:
    def __init__(self, username=None, password=None, use_cookies=True, cookies_file="linkedin_cookies.json"):
        self.driver = self._setup_driver()
        # Initialize the auth module
        self.auth = LinkedInAuth(
            driver=self.driver,
            username=username,
            password=password,
            use_cookies=use_cookies,
            cookies_file=cookies_file
        )
        self.robot_handler = RobotHandler(self.driver)
    
    def _setup_driver(self):
        options = Options()
        options.add_argument("--disable-notifications")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def manual_verification_check(self):
        """
        Allow the user to manually verify if they can continue
        """
        print("\nChecking if manual verification is needed...")
        print("Current URL:", self.driver.current_url)
        print("Page title:", self.driver.title)
        
        response = input("Is there a CAPTCHA or verification challenge visible? (y/n): ")
        if response.lower() in ['y', 'yes']:
            input("Please solve the CAPTCHA/verification and press Enter when done...")
            return True
        return False
    
    def verify_with_screenshot(self):
        """
        Take a screenshot and ask user to verify if there's a CAPTCHA
        """
        try:
            screenshot_path = "verification_check.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"\nScreenshot saved to {screenshot_path}")
            
            response = input("Is there a CAPTCHA or verification needed? (y/n): ")
            if response.lower() in ['y', 'yes']:
                input("Please solve the CAPTCHA/verification and press Enter when done...")
                return True
            return False
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return self.manual_verification_check()
    

    def scrape_page(self, url, field_selectors, container_selector, pagination_method="next_button", max_pages=3):
        """
        Scrape LinkedIn page based on provided selectors
        
        Args:
            url: LinkedIn page URL to scrape
            field_selectors: Dictionary mapping field names to CSS/XPath selectors
            container_selector: CSS selector for the container of each result item
            pagination_method: Method to navigate to next page ("next_button" or "scroll")
            max_pages: Maximum number of pages to scrape
        
        Returns:
            List of dictionaries containing scraped data
        """
        self.driver.get(url)
        
        # Enhanced verification check with screenshot
        if self.robot_handler.check_for_captcha():
            input("Please solve any security challenges and press Enter to continue...")
        
        all_results = []
        pages_scraped = 0
        
        while pages_scraped < max_pages:
            self.robot_handler.human_scroll()
            
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            
            # Use the provided container selector
            print(f"Using container selector: {container_selector}")
            containers = soup.select(container_selector)
            
            if not containers:
                print(f"No results found using selector: {container_selector}")
                print("Page might have different structure or no results.")
                # Take a screenshot to help debug the selector
                self.driver.save_screenshot(f"debug_page_{pages_scraped}.png")
                print(f"Debug screenshot saved as debug_page_{pages_scraped}.png")
                
                # Try alternative common selectors
                alternative_selectors = [
                    "li.reusable-search__result-container",
                    "li.mn-connection-card",
                    "div.entity-result",
                    "div.search-result",
                    "li.search-result"
                ]
                
                for alt_selector in alternative_selectors:
                    print(f"Trying alternative selector: {alt_selector}")
                    alt_containers = soup.select(alt_selector)
                    if alt_containers:
                        print(f"Found {len(alt_containers)} results using alternative selector: {alt_selector}")
                        containers = alt_containers
                        container_selector = alt_selector  # Update for future pages
                        break
                
                if not containers:
                    break
            
            print(f"Found {len(containers)} items on page {pages_scraped + 1}")
            
            for container in containers:
                data = {}
                for field, selector in field_selectors.items():
                    print(f"Processing field: {field} with selector: {selector}")
                    try:
                        if selector.startswith("//"):  # XPath
                            # Using selenium for XPath
                            container_html = str(container)
                            # Create a temporary element in the DOM
                            script = f"var tempDiv = document.createElement('div'); tempDiv.innerHTML = `{container_html}`; return tempDiv;"
                            temp_elem = self.driver.execute_script(script)
                            try:
                                element = temp_elem.find_element(By.XPATH, selector)
                                if field.endswith("_link") and element.get_attribute("href"):
                                    data[field] = element.get_attribute("href")
                                else:
                                    data[field] = element.text.strip()
                            except:
                                data[field] = None
                        else:  # CSS selector
                            element = container.select_one(selector)
                            if element:
                                if field.endswith("_link"):
                                    if field == "photo_link":
                                        data[field] = element.get("src")
                                    else:
                                        data[field] = element.get("href")
                                elif field.endswith("_img") or field.endswith("_image"):
                                    img = element.find("img")
                                    data[field] = img.get("src") if img else None
                                else:
                                    # Extract text and process it
                                    text = element.text.strip()
                                    if field == "connected_date" and "connected on " in text:
                                        text = text.replace("connected on ", "")
                                    data[field] = text
                            else:
                                data[field] = None
                    except Exception as e:
                        print(f"Error extracting {field}: {e}")
                        data[field] = None
            
                if data:
                    all_results.append(data)
            
            # Check for CAPTCHA again before pagination
            if self.robot_handler.check_for_captcha():
                input("CAPTCHA detected before pagination! Please solve it manually and press Enter to continue...")
            
            # Handle pagination based on specified method
            try:
                if pagination_method == "next_button":
                    # Try different possible next button selectors
                    next_button_selectors = [
                        "//button[contains(@aria-label, 'Next')]",
                        "//button[contains(text(), 'Next')]",
                        "//button[contains(@class, 'artdeco-pagination__button--next')]",
                        "//li[contains(@class, 'artdeco-pagination__button--next')]/button",
                        "//button/span[text()='Next']/parent::button",
                        "//span[contains(text(), 'Next')]/parent::button"
                    ]
                    
                    next_button = None
                    for selector in next_button_selectors:
                        try:
                            next_button = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                            break
                        except:
                            continue
                    
                    if next_button:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                        next_button.click()
                    else:
                        print("No next button found. Ending pagination.")
                        break
                        
                elif pagination_method == "scroll":
                    # Scroll multiple times to trigger infinite loading
                    last_height = self.driver.execute_script("return document.body.scrollHeight")
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    
                    if new_height == last_height:
                        print("No more content loaded on scroll. Ending pagination.")
                        break
                else:
                    # Custom pagination method if provided
                    print(f"Unsupported pagination method: {pagination_method}")
                    break
            except Exception as e:
                print(f"Pagination error: {e}")
                break
            
            # Check for CAPTCHA again after pagination
            if self.robot_handler.check_for_captcha():
                input("CAPTCHA detected after pagination! Please solve it manually and press Enter to continue...")
            
            pages_scraped += 1
            print(f"Scraped page {pages_scraped}/{max_pages}")
        
        return all_results
    
    def save_to_json(self, data, filename="linkedin_data.json"):
        """Save scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to {filename}")
    
    def save_to_csv(self, data, filename="linkedin_data.csv"):
        """Save scraped data to CSV file"""
        if not data:
            print("No data to save.")
            return
        
        keys = data[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        print(f"Data saved to {filename}")
    
    def close(self):
        """Close the browser"""
        self.driver.quit()

def load_template(template_file):
    """Load scraping template from JSON file"""
    with open(template_file, 'r') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Profile Scraper")
    parser.add_argument("--url", type=str, required=True, help="LinkedIn URL to scrape")
    parser.add_argument("--template", type=str, required=True, help="Path to template JSON file")
    parser.add_argument("--output", type=str, default="linkedin_data", help="Output filename without extension")
    parser.add_argument("--format", type=str, choices=["json", "csv", "both"], default="both", help="Output format")
    parser.add_argument("--pages", type=int, default=3, help="Maximum number of pages to scrape")
    parser.add_argument("--pagination", type=str, choices=["next_button", "scroll"], default="next_button", 
                        help="Pagination method")
    parser.add_argument("--username", type=str, help="LinkedIn username/email")
    parser.add_argument("--password", type=str, help="LinkedIn password")
    parser.add_argument("--no-cookies", action="store_true", help="Don't use saved cookies")
    
    args = parser.parse_args()
    
    # Load template
    try:
        template = load_template(args.template)
        field_selectors = template.get("field_selectors", {})
        container_selector = template.get("container_selector", "")
        
        if not field_selectors or not container_selector:
            print("Error: Template must contain 'field_selectors' and 'container_selector'")
            return
    except Exception as e:
        print(f"Error loading template: {e}")
        return
    
    # Initialize scraper
    scraper = LinkedInScraper(
        username=args.username, 
        password=args.password, 
        use_cookies=not args.no_cookies
    )
    
    try:
        # Scrape the data
        data = scraper.scrape_page(
            url=args.url,
            field_selectors=field_selectors,
            container_selector=container_selector,
            pagination_method=args.pagination,
            max_pages=args.pages
        )
        
        # Save the data
        if args.format in ["json", "both"]:
            scraper.save_to_json(data, f"{args.output}.json")
        
        if args.format in ["csv", "both"]:
            scraper.save_to_csv(data, f"{args.output}.csv")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        scraper.close()

# Example template JSON file (connections_template.json):
"""
{
    "container_selector": "li.mn-connection-card",
    "field_selectors": {
        "name": "span.mn-connection-card__name",
        "headline": "span.mn-connection-card__occupation",
        "profile_link": "a.mn-connection-card__link",
        "photo_link": "div.presence-entity__image"
    }
}
"""

# Example template JSON file (search_template.json):
"""
{
    "container_selector": "li.reusable-search__result-container",
    "field_selectors": {
        "name": ".app-aware-link span[aria-hidden='true']",
        "headline": ".entity-result__primary-subtitle",
        "company": ".entity-result__secondary-subtitle",
        "location": ".entity-result__secondary-subtitle ~ .entity-result__secondary-subtitle",
        "profile_link": ".app-aware-link"
    }
}
"""

if __name__ == "__main__":
    main()