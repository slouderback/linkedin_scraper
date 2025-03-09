from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

REMEMBER_PROMPT = 'remember-me-prompt__form-primary'

def login(driver, email=None, password=None, cookie = None, timeout=10):
    if cookie is not None:
        return _login_with_cookie(driver, cookie)


    driver.get("https://www.linkedin.com/login")
    _ = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

    email_elem = driver.find_element(By.ID,"username")
    email_elem.send_keys(email)

    password_elem = driver.find_element(By.ID,"password")
    password_elem.send_keys(password)
    password_elem.submit()

    if driver.current_url == 'https://www.linkedin.com/checkpoint/lg/login-submit':
        remember = driver.find_element(By.ID, REMEMBER_PROMPT)
        if remember:
            remember.submit()



def _login_with_cookie(driver, cookie):
    driver.get("https://www.linkedin.com/login")
    driver.add_cookie({
        "name": "li_at",
        "value": cookie
    })