import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class RobotHandler:
    def __init__(self, driver):
        self.driver = driver

    def artificial_delay(self, min_seconds=1, max_seconds=3):
        """Random delay to mimic human behavior"""
        import random
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def check_for_captcha(self):
        """
        Enhanced CAPTCHA detection function that checks for multiple indicators
        """
        try:
            # Check for common CAPTCHA indicators
            captcha_indicators = [
                # Standard captcha element
                (By.ID, "captcha-challenge"),
                # Common CAPTCHA iframe
                (By.XPATH, "//iframe[contains(@src, 'captcha') or contains(@src, 'challenge')]"),
                # reCAPTCHA specific elements
                (By.XPATH, "//div[@class='g-recaptcha' or contains(@data-sitekey, 'recaptcha')]"),
                # Cloudflare CAPTCHA
                (By.ID, "cf-challenge-running"),
                # Common CAPTCHA container classes
                (By.XPATH, "//div[contains(@class, 'captcha') or contains(@class, 'challenge')]"),
                # Image elements that might be CAPTCHA
                (By.XPATH, "//img[contains(@src, 'captcha') or contains(@alt, 'captcha')]"),
                # LinkedIn specific verification screens
                (By.XPATH, "//div[contains(@class, 'verification-modal')]"),
                (By.XPATH, "//h1[contains(text(), 'Let') and contains(text(), 'know') and contains(text(), 'you')]"),
            ]
            
            # Check each indicator
            for locator_type, locator_value in captcha_indicators:
                try:
                    elements = self.driver.find_elements(locator_type, locator_value)
                    for element in elements:
                        if element.is_displayed():
                            print(f"CAPTCHA detected: {locator_type} {locator_value}")
                            return True
                except:
                    continue
                    
            # Check for unusual pages that might indicate security challenges
            current_url = self.driver.current_url
            if any(term in current_url for term in ['checkpoint', 'challenge', 'verify', 'captcha']):
                print(f"Possible CAPTCHA/verification page detected: {current_url}")
                return True
                
            # Check page title for verification indicators
            title = self.driver.title
            if any(term in title.lower() for term in ['security', 'verify', 'captcha', 'challenge', 'check']):
                print(f"Possible CAPTCHA page detected from title: {title}")
                return True
                
            return False
        except Exception as e:
            print(f"Error during CAPTCHA detection: {e}")
            # When in doubt, let the user check
            if "challenge" in self.driver.current_url or "captcha" in self.driver.current_url:
                return True
            return False
    
    def human_scroll(self, scroll_distance=None):
        """Scroll like a human with variable speed and pauses"""
        if scroll_distance is None:
            scroll_distance = random.randint(300, 700)
        
        
        steps = random.randint(5, 15)
        for _ in range(steps):
            increment = scroll_distance / steps
            self.driver.execute_script(f"window.scrollBy(0, {increment});")
            self.artificial_delay(0.1, 0.3)
    
    