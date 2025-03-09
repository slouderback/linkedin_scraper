from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .types import Connection



class Network:
    def __init__(self, driver, connections=None):
        self.driver = driver
        self.connections = connections or []

    def add_connection(self, connection):
        self.connections.append(connection)

    def find_connections(self, fields, limit) -> list[Connection]:
        try:
            self.driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")

            # Wait for the connection list to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[componentkey="ConnectionsPage_ConnectionsList"]'))
            )

            connection_list_container = self.driver.find_element(By.CSS_SELECTOR, '[componentkey="ConnectionsPage_ConnectionsList"]')

            # Retrieve all child elements with data-view-name="connections-list"
            all_connections = connection_list_container.find_elements(By.CSS_SELECTOR, '[data-view-name="connections-list"]')

            print(f"Found {len(all_connections)} connections")

            connection_details = []

            for connection in all_connections:
                try:
                    # Name
                    name_element = connection.find_element(By.CSS_SELECTOR, 'a[data-view-name="connections-profile"] p a')
                    name = name_element.text.strip()

                    # Headline
                    headline_element = connection.find_element(By.CSS_SELECTOR, 'a[data-view-name="connections-profile"] p + p')
                    headline = headline_element.text.strip()

                    # Profile link
                    profile_link = name_element.get_attribute('href')

                    # Photo link (handling SVG placeholders)
                    photo_element = connection.find_element(By.CSS_SELECTOR, 'a[data-view-name="connections-profile"] figure img')
                    photo_link = photo_element.get_attribute('src')

                    connected_date_element = connection.find_element(By.XPATH, ".//p[contains(text(), 'connected on')]")
                    connected_date = connected_date_element.text.replace('connected on ', '').strip()


                    connection_data = Connection(
                        name=name if "name" in fields else None,
                        headline=headline if "headline" in fields else None,
                        profile_link=profile_link if "profile_link" in fields else None,
                        photo_link=photo_link if "photo_link" in fields else None,
                        connected_date=connected_date if "connected_date" in fields else None
                    )

                    connection_details.append(connection_data)

                except Exception as e:
                    print(f"Error extracting connection details: {e}")

            # print(f"Found {len(connection_details)} connections")
            return connection_details

        except:
            print("Error finding connections")
            return None