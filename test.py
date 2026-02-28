from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
# # from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait

# # from selenium.webdriver.support.ui import Select
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By

import time


def launch_navigator(url, headless= True, enable_profile=False):
    geckodriver_path = "/usr/local/bin/geckodriver" 

    # Configurar las opciones del navegador
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-browser-side-navigation')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    if headless:
        print('Mode headless')
        options.add_argument('--headless')
    if enable_profile:
        profile_path = "/home/jorge/.mozilla/firefox/lf4ga6zv.default-release"
        profile = FirefoxProfile(profile_path)
        options.profile = profile
    service = Service(geckodriver_path)
    driver = webdriver.Firefox(options=options)    
    driver.get(url)
    driver.execute_script("document.body.style.zoom='50%'")    
    time.sleep(5)
    return driver

url = 'https://www.ite.es/'

driver = launch_navigator(url, headless= False, enable_profile=False)
