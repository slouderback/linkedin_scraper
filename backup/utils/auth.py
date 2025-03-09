import json
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# from utils.robot_handler import RobotHandler

# class LinkedInAuth:
#     def __init__(self, driver, username=None, password=None, use_cookies=True, cookies_file="linkedin_cookies.json"):
#         self.driver = driver
#         self.username = username
#         self.password = password
#         self.use_cookies = use_cookies
#         self.cookies_file = cookies_file
#         self.robot_handler = RobotHandler(self.driver)
#         # Initialize authentication
#         if self.use_cookies and os.path.exists(self.cookies_file):
#             self.load_cookies()
#         elif username and password:
#             self.login()
#         else:
#             print("No login credentials or cookies provided. You'll need to log in manually.")
#             input("Press Enter after logging in manually...")
    
#     def login(self):
#         """Log in to LinkedIn with flexible handling of pre-filled email"""
#         self.driver.get("https://www.linkedin.com/login")
        
        
#         # Check what type of login screen we're dealing with
#         try:
#             # First, try to find any password field (this is common in both flows)
#             password_field = None
#             for possible_selector in [
#                 (By.ID, "password"),
#                 (By.NAME, "session_password"),
#                 (By.CSS_SELECTOR, "input[type='password']")
#             ]:
#                 try:
#                     password_field = self.driver.find_element(possible_selector)
#                     print(f"Found password field using selector: {possible_selector}")
#                     break
#                 except NoSuchElementException:
#                     continue
            
#             if not password_field:
#                 raise NoSuchElementException("Password field not found")
            
#             # Now check if there's a username field or if it's pre-filled
#             username_field = None
#             for possible_selector in [
#                 (By.ID, "username"),
#                 (By.NAME, "session_key"),
#                 (By.CSS_SELECTOR, "input[type='text']"),
#                 (By.CSS_SELECTOR, "input[type='email']")
#             ]:
#                 try:
#                     username_field = self.driver.find_element(*possible_selector)
#                     print(f"Found username field using selector: {possible_selector}")
#                     break
#                 except NoSuchElementException:
#                     continue
            
#             # If we found a username field, enter the username
#             if username_field:
#                 # Check if field is empty or needs to be cleared
#                 current_value = username_field.get_attribute('value')
#                 if current_value:
#                     if current_value != self.username:
#                         # Clear and fill if different
#                         username_field.clear()
#                         self.robot_handler.artificial_delay(0.5, 1)
#                         username_field.send_keys(self.username)
#                 else:
#                     # Field is empty, just fill it
#                     username_field.send_keys(self.username)
#             else:
#                 # No username field found - check if there's text showing the pre-filled email
#                 pre_filled_elements = self.driver.find_elements(By.CSS_SELECTOR, ".login__form_input_container")
#                 pre_filled_found = False
                
#                 for element in pre_filled_elements:
#                     if element.text and '@' in element.text:
#                         print(f"Found pre-filled email: {element.text}")
#                         pre_filled_found = True
#                         # If the pre-filled email doesn't match our username, we need to change it
#                         if self.username not in element.text:
#                             try:
#                                 # Try to find a "Change" link or button
#                                 change_link = self.driver.find_element(By.XPATH, 
#                                     "//*[contains(text(), 'Change') or contains(text(), 'Not you?')]")
#                                 change_link.click()
#                                 self.robot_handler.artificial_delay(2, 3)
#                                 # Now we should have username and password fields
#                                 username_field = self.driver.find_element(By.ID, "username")
#                                 username_field.send_keys(self.username)
#                             except NoSuchElementException:
#                                 print("Pre-filled email doesn't match and couldn't find 'Change' button.")
#                                 print("Please log in manually with correct credentials.")
#                                 input("Press Enter after logging in manually...")
#                                 return
#                         break
                
#                 if not pre_filled_found:
#                     print("No username field or pre-filled email found. UI might have changed.")
        
#         except Exception as e:
#             print(f"Error handling username field: {e}")
            
#             # Enter password
#             password_field.send_keys(self.password)
#             self.robot_handler.artificial_delay(1, 3)
            
#             # Find and click the sign in button
#             signin_button = None
#             for button_selector in [
#                 (By.XPATH, "//button[@type='submit']"),
#                 (By.XPATH, "//button[contains(text(), 'Sign in')]"),
#                 (By.CSS_SELECTOR, "button[data-id='sign-in-form__submit-btn']"),
#                 (By.CSS_SELECTOR, ".login__form_action_container button")
#             ]:
#                 try:
#                     signin_button = self.driver.find_element(*button_selector)
#                     print(f"Found sign-in button using selector: {button_selector}")
#                     break
#                 except NoSuchElementException:
#                     continue
            
#             if not signin_button:
#                 raise NoSuchElementException("Sign in button not found")
            
#             signin_button.click()
            
#         except Exception as e:
#             print(f"Error during login process: {e}")
#             print("Please log in manually.")
#             input("Press Enter after logging in manually...")
#             return
        
#         # Check for CAPTCHA after login attempt
#         if self.robot_handler.check_for_captcha():
#             input("CAPTCHA detected! Please solve it manually and press Enter to continue...")
        
#         self.robot_handler.artificial_delay(4, 7)
        
#         # Verify login was successful
#         if not self._is_logged_in():
#             print("Login might have failed. Please check the browser.")
#             input("Press Enter to continue if you've logged in manually...")
        
#         if self.use_cookies:
#             self.save_cookies()
    
#     def save_cookies(self):
#         """Save cookies to file for future use"""
#         print("Saving cookies after login...")
#         cookies = self.driver.get_cookies()
#         with open(self.cookies_file, 'w') as f:
#             json.dump(cookies, f)
    
#     def load_cookies(self):
#         """Load cookies from file"""
#         self.driver.get("https://www.linkedin.com")
#         with open(self.cookies_file, 'r') as f:
#             cookies = json.load(f)
#             for cookie in cookies:
#                 self.driver.add_cookie(cookie)
        
#         self.driver.refresh()
        
#         if not self._is_logged_in():
#             print("Cookies expired. Logging in with credentials...")
#             if self.username and self.password:
#                 self.login()
#             else:
#                 input("Login required. Please log in manually and press Enter when done...")
    
#     def _is_logged_in(self):
#         """Check if user is logged in"""
#         try:
#             WebDriverWait(self.driver, 5).until(
#                 EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'mynetwork')]"))
#             )
#             return True
#         except:
#             return False
    


