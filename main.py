import argparse
import dataclasses
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from linkedin.base import login
from linkedin.targets.network import Network
from linkedin.targets.search import Search
from linkedin.utils.data_export import export_data
from linkedin.targets.types import Connection

def load_template(template_file):
    """Load scraping template from JSON file"""
    with open(template_file, 'r') as f:
        return json.load(f)

def main():
    print("Parsing arguments")
    parser = argparse.ArgumentParser(description="LinkedIn Profile Scraper")
    # Required arguments
    parser.add_argument("--template", type=str, required=True, help="Path to template JSON file")
    parser.add_argument("--username", type=str, help="LinkedIn username/email")
    parser.add_argument("--password", type=str, help="LinkedIn password")
    
    args = parser.parse_args()
    
    print("Loading template")
    try:
        template = load_template(args.template)
        page = template.get("page", "")
        query = template.get("query", "")
        fields = template.get("fields", {})
        limit = template.get("limit", 20)
        
        if not page or not fields or not limit:
            print("Error: Template must contain 'page', 'fields', and 'limit'")
            return
    except Exception as e:
        print(f"Error loading template: {e}")
        return
    
    print("Initializing driver")
    driver = webdriver.Chrome()

    print("Logging in")
    login(driver, args.username, args.password)

    input("Please complete any security checks and press Enter to continue...")
    if page == "connections":
        # get connections
        print("Getting connections")
        my_network = Network(driver)
        connections: list[Connection] = my_network.find_connections(fields, limit)
        formatted_connections = [dataclasses.asdict(elem) for elem in connections]
        export_data(formatted_connections)

    elif page == "search":
        print("Getting search")
        my_search = Search(driver)
        my_search.search(query, fields)

        formatted_jobs = [dataclasses.asdict(elem) for elem in my_search.jobs]
        formatted_posts = [dataclasses.asdict(elem) for elem in my_search.posts]
        formatted_people = [dataclasses.asdict(elem) for elem in my_search.people]
        formatted_companies = [dataclasses.asdict(elem) for elem in my_search.companies]
        export_data(formatted_jobs + formatted_posts + formatted_people + formatted_companies)

if __name__ == "__main__":
    main()



