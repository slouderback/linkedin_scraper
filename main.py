
# # Example template JSON file (connections_template.json):
# """
# {
#     "container_selector": "li.mn-connection-card",
#     "field_selectors": {
#         "name": "span.mn-connection-card__name",
#         "headline": "span.mn-connection-card__occupation",
#         "profile_link": "a.mn-connection-card__link",
#         "photo_link": "div.presence-entity__image"
#     }
# }
# """

# # Example template JSON file (search_template.json):
# """
# {
#     "container_selector": "li.reusable-search__result-container",
#     "field_selectors": {
#         "name": ".app-aware-link span[aria-hidden='true']",
#         "headline": ".entity-result__primary-subtitle",
#         "company": ".entity-result__secondary-subtitle",
#         "location": ".entity-result__secondary-subtitle ~ .entity-result__secondary-subtitle",
#         "profile_link": ".app-aware-link"
#     }
# }
# """

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

    # Optional arguments
    parser.add_argument("--format", type=str, choices=["json", "csv", "both"], default="both", help="Output format")

    
    args = parser.parse_args()
    
    # Load template
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

    # log in
    print("Logging in")
    login(driver, args.username, args.password)

    # wait for enter key
    input("Please complete any security checks and press Enter to continue...")
    # # get connections
    # print("Getting connections")
    # my_network = Network(driver)
    # connections: list[Connection] = my_network.find_connections(fields, limit)
    # export_data(connections)

    # get search
    print("Getting search")
    my_search = Search(driver)
    my_search.search(query)

    print(f"Fields: {my_search.fields}")
    # print(f"Jobs: {my_search.jobs}")
    # print(f"Posts: {my_search.posts}")
    print(f"People: {my_search.people}")
    # print(f"Companies: {my_search.companies}")
    # print(f"Groups: {my_search.groups}")
    # print(f"Products: {my_search.products}")

    data_to_export = my_search.posts
    formatted_data = [dataclasses.asdict(elem) for elem in data_to_export]
    export_data(formatted_data)

if __name__ == "__main__":
    main()



