from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from datetime import date, timedelta, datetime
from selenium import webdriver
import random
import string
import requests
import json
import os
import re
import time
import uuid

local_time_naive = datetime.now()
utc_time_naive = datetime.utcnow()
time_difference_naive = utc_time_naive - local_time_naive

days = {'monday': 0,
        'tuesday': 1,
        'wednesday': 2,
        'thursday': 3,
        'friday': 4,
        'saturday': 5,
        'sunday': 6}

#####################################################################
#                   CHECK POINTS BLOCK                              #
#####################################################################
def int_folders():
    if not os.path.exists('check_points'):
        os.mkdir('check_points')
    if not os.path.exists('check_points/news/'):
        os.mkdir("check_points/news/")
    if not os.path.exists('check_points/results/'):
        os.mkdir("check_points/results/")
    if not os.path.exists('check_points/fixtures/'):
        os.mkdir("check_points/fixtures/")
    if not os.path.exists('check_points/standings/'):
        os.mkdir("check_points/standings/")
    if not os.path.exists('check_points/leagues_season/'):
        os.mkdir("check_points/leagues_season/")
    if not os.path.exists('check_points/issues/'):
        os.mkdir("check_points/issues/")
    if not os.path.exists('images'):
        os.mkdir("images")
    if not os.path.exists('images/logos'):
        os.mkdir('images/logos')
    if not os.path.exists('images/players'):
        os.mkdir('images/players')
    if not os.path.exists('images/news'):
        os.mkdir("images/news")
    if not os.path.exists('images/news/small_images'):
        os.mkdir("images/news/small_images/")
    if not os.path.exists('images/news/full_images'):
        os.mkdir("images/news/full_images/")
    if not os.path.isfile('check_points/CONFIG.json'):
        CONFIG = {"get_news_m1": True,  # Activate M1
            "sports_link": False,       # 
            "update_links": True,       #
            "get_news": False,          # Get news from each sport
            "DATA_BASE": False}         # Save in data base
        save_check_point('check_points/CONFIG.json', CONFIG)

def get_sports_links_news(driver):
    wait = WebDriverWait(driver, 1)
    buttonmore = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'arrow.topMenuSpecific__moreIcon')))

    mainsports = driver.find_elements(By.XPATH, '//div[@class="topMenuSpecific__items"]/a')

    dict_links = {}

    for link in mainsports[1:]:     
        sport_name = '_'.join(link.text.split())
        sport_url = link.get_attribute('href')
        if sport_name != '':            
            dict_links[sport_name] = sport_url  
    buttonmore.click()

    list_links = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'topMenuSpecific__dropdownItem')))
    list_links = driver.find_elements(By.CLASS_NAME, 'topMenuSpecific__dropdownItem')

    for link in list_links:
        sport_name = '_'.join(link.text.split())
        sport_url = link.get_attribute('href')      
        if sport_name == '':
            sport_name = sport_url.split('/')[-2].upper()
        dict_links[sport_name] = sport_url

    buttonminus = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'arrow.topMenuSpecific__moreIcon')))
    buttonminus.click()
    return dict_links

def load_json(filename):
    # Opening JSON file
    with open(filename, 'r') as openfile:        
        json_object = json.load(openfile)
    return json_object

def save_check_point(filename, dictionary):
    json_object = json.dumps(dictionary, indent=4)
    with open(filename, "w") as outfile:
        outfile.write(json_object)

def load_check_point(filename):
    # Opening JSON file
    if os.path.isfile(filename):
        with open(filename, 'r') as openfile:        
            json_object = json.load(openfile)
    else:
        json_object = {}
    return json_object

def check_previous_execution(file_path = 'check_points/scraper_control.json'):
    if os.path.isfile(file_path):
        dict_scraper_control = load_json(file_path)
    else:
        dict_scraper_control = {}
    return dict_scraper_control

def launch_navigator_chrome(url, headless = True):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-application-cache")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-infobars")
    # options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-web-security")
    options.add_argument("--incognito")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")     
    # options.add_experimental_option("excludeSwitches", ["enable-automation"]) ----
    options.add_experimental_option("useAutomationExtension", False)
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')  ---  
    # chrome_path = os.getcwd()+'/chrome_files'
    # print("chrome_path: ", chrome_path)
    # options.add_argument(r"user-data-dir={}".format(chrome_path))
    # options.add_argument(r"profile-directory=Profile1")

    drive_path = Service('/usr/local/bin/chromedriver')

    driver = webdriver.Chrome(service=drive_path,  options=options)
    driver.get(url)
    return driver

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
    return driver

def login(driver, email_= "jignacio@jweglobal.com", password_ = "Caracas5050@"):
    wait = WebDriverWait(driver, 10)

    try:
        # Accept cookies
        accept_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        accept_button.click()
    except:
        print("Continue...")
    # Click on login
    login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'header__icon.header__icon--user')))
    # login_button = driver.find_element(By.CLASS_NAME, 'header__icon.header__icon--user')
    login_button.click()
    # Select login mode
    continue_email = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ui-button.ui-formButton.social__button.email")))
    continue_email.click()

    email = driver.find_element(By.ID,'email')
    email.clear()
    email = wait.until(EC.visibility_of_element_located((By.ID,'email')))
    email.send_keys(email_)

    password_element = driver.find_element(By.ID,'passwd')
    password_element.clear()
    password_element.send_keys(password_)
    xpath_expression = '//button[contains(., "Log In")]'
    logig = driver.find_element(By.XPATH, xpath_expression)
    logig.click()
    time.sleep(6)
    print("Login...", '\n')
    driver.execute_script("document.body.style.zoom='50%'")
    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()

def wait_update_page(driver, url, class_name):

    wait = WebDriverWait(driver, 10)
    current_tab = driver.find_elements(By.CLASS_NAME, class_name)
    driver.get(url)

    if len(current_tab) == 0:
        current_tab = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, class_name)))
    else:
        element_updated = wait.until(EC.staleness_of(current_tab[0]))   

def wait_load_detailed_news(driver, url_news):  
    wait = WebDriverWait(driver, 10)
    class_name = 'fsNews'
    title = driver.find_elements(By.CLASS_NAME, class_name)
    driver.get(url_news)
    if len(title) == 0:
        title = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, class_name)))
    else:
        wait.until(EC.staleness_of(title[0]))

def get_mentions(driver):
    mention_list = ''
    mentions = driver.find_elements(By.XPATH, '//div[@class="fsNewsArticle__mentions"]/a')
    for mention in mentions:
        if mention_list == '':
            mention_list = mention.text
        else:
            mention_list = mention_list +', '+mention.text
    return mention_list

def save_image(driver, image_url, image_path):
    print("image_path: ", image_path)
    img_data = requests.get(image_url).content

    with open(image_path, 'wb') as handler:
        handler.write(img_data)

def process_date(date):
    date_format = "%d.%m.%Y %H:%M:%S"
    if 'min ago' in date:       
        min_ = int(re.findall(r'(\d+)\ min ago', date)[0])        
        news_time_post = local_time_naive - timedelta(minutes=min_)
    elif ' h ago' in date:
        hours_ = int(re.findall(r'(\d+)\ h ago', date)[0])        
        news_time_post = local_time_naive - timedelta(hours=hours_)
    elif 'Yesterday' in date:
        previous_day = local_time_naive - timedelta(days=1)
        time_post = re.findall(r'\d+:\d+', date)[0]+':00'
        time_post = datetime.strptime(time_post, "%H:%M:%S")
        news_time_post = datetime(
            previous_day.year,
            previous_day.month,
            previous_day.day,
            time_post.hour,
            time_post.minute,
            time_post.second,
        )
    elif 'Just now' in date:
        news_time_post = local_time_naive
    else:       
        date = date +':00'
        news_time_post = datetime.strptime(date, date_format)   

    news_utc_time = news_time_post + time_difference_naive
    return news_utc_time

def random_name(folder = 'news_images', termination = '.jpg'):
    file_name = ''.join(random.choice(string.ascii_lowercase) for i in range(16))
    return os.path.join(folder,file_name + termination)

def img_path(title, folder = 'news_images',termination = '.jpg'):
    title = title[0:20].replace(' ','_')
    return os.path.join(folder,title + termination)

def random_name_logos(league_team, folder = 'news_images', termination = '.jpg'):
    file_name = ''.join(random.choice(string.ascii_lowercase) for i in range(4))
    digits = ''.join([str(random.randint(0, 9)) for i in range(1)])
    file_name = '_' + file_name + digits
    league_team = '_'.join(league_team.replace('-', '_').replace('/', '_').lower().split())
    return os.path.join(folder,(league_team) + file_name + termination)

def random_id():
    rand_id = ''.join(random.choice(string.ascii_lowercase) for i in range(4))
    rand_id = rand_id + str(random.choice([0, 9]))
    digits = ''.join([str(random.randint(0, 9)) for i in range(4)])
    return rand_id+digits

def generate_uuid():    
    return uuid.uuid4()

def random_id_text(textinput):
    textinput = textinput.replace(' ', '')
    unique_code = 0
    for char in textinput:
        unique_code = unique_code*6 + ord(char)
    unique_code = str(unique_code)    
    if len(unique_code) < 10:        
        unique_code = (10 - len(unique_code))*'0' + unique_code        
    else:
        unique_code = unique_code[-10:]
    return unique_code

def random_id_short():
    rand_id = ''.join(random.choice(string.ascii_lowercase) for i in range(4))
    digits = ''.join([str(random.randint(0, 9)) for i in range(4)])
    return rand_id+digits

def stop_validate():
    user_input = input("Type y to continue s to stop: ")
    if user_input == 'y':
        user_confirmation = True
    if user_input == 's':
        print(stop)

def print_section(section, space_ = 50):
    line_sport = "#" + " "*(space_ - int(len(section)/2)) + section + " "*(space_ - int(len(section)/2)) + "#"
    print('\n')
    print("#"*len(line_sport))
    print(line_sport)
    print("#"*len(line_sport), '\n')

def clean_field(text):
    return text.replace("'", "\''")

def clean_text(text):
    return ' '.join(text.split())

def execute_section(execution_schedule, day_execution, execute_ready):
    # global day_execution, execute_ready
    enable_execution = False    
    if 'montly' in execution_schedule and not execute_ready:
        interval, day_exe, time_str = execution_schedule.split("|")
        if datetime.now().day == day_exe:
            time_execution = datetime.strptime(time_str, '%H:%M:%S')
            if datetime.now().time() > time_execution.time() and datetime.now().time() < (time_execution + timedelta(minutes=1)).time():
                # print(time_execution)
                enable_execution = True
                execute_ready = True

    if 'weekly' in execution_schedule and not execute_ready:
        interval, day_exe, time_str = execution_schedule.split("|")
        time_execution = datetime.strptime(time_str, '%H:%M:%S')
        # print("time_execution: ", time_execution, type(time_execution))
        if datetime.now().weekday() == days[day_exe] and datetime.now().time() > time_execution.time() and datetime.now().time() < (time_execution + timedelta(minutes=1)).time():
            enable_execution = True
            execute_ready = True
            day_execution = datetime.now().day

    if 'daily' in execution_schedule and not execute_ready:     
        # print("Case daily")
        _, time_str = execution_schedule.split("|")     
        time_execution = datetime.strptime(time_str, '%H:%M:%S')
        if datetime.now().time() >= time_execution.time() and datetime.now().time() < (time_execution + timedelta(minutes=1)).time():
            enable_execution = True
            execute_ready = True
            day_execution = datetime.now().day
    
    if datetime.now().day != day_execution:     
        execute_ready = False
        day_execution = -1

    #################################################################
    #           SECTION SECONDS-MINUTES                             #
    #################################################################
    if 'minute' in execution_schedule:
        # print("Case daily")
        part1, time_str = execution_schedule.split("|")     
        time_execution = datetime.strptime(time_str, '%H:%M:%S')
        if datetime.now().time() >= time_execution.time() and datetime.now().time() < (time_execution + timedelta(minutes=1)).time():
            enable_execution = True
            execute_ready = False
            time_execution = time_execution + timedelta(minutes=1)
            execution_schedule = part1 +'|'+str(time_execution.time())          
            # day_execution = datetime.now().day
    if 'seconds' in execution_schedule:
        
        if len(execution_schedule.split("|")) == 2:
            part1, seconds_str = execution_schedule.split("|")          
            option = 1
        if len(execution_schedule.split("|")) == 3:
            part1, seconds_str, time_str = execution_schedule.split("|")
            option = 2
        
        if option == 1:         
            time_execution = datetime.now()         
            enable_execution = True
            execute_ready = False               
            time_execution = time_execution + timedelta(seconds = int(seconds_str))
            execution_schedule = part1 +'|' + seconds_str +'|'+ time_execution.time().strftime('%H:%M:%S')          
                
        if option == 2:
            time_execution = datetime.strptime(time_str, '%H:%M:%S')            
            if datetime.now().time() >= time_execution.time() and datetime.now().time() < (time_execution + timedelta(seconds = 10)).time():
                enable_execution = True
                execute_ready = False
                time_execution = time_execution + timedelta(seconds = int(seconds_str))             
                execution_schedule = part1 +'|' + seconds_str +'|'+ time_execution.time().strftime('%H:%M:%S') 
                

        # print("Salida de la funcion: ", "#"*30)
        # print("enable_execution: ", enable_execution, "Current time: ", datetime.now().time(), "execution_schedule: ", execution_schedule)
            

    return enable_execution, day_execution, execute_ready, execution_schedule

def update_data(folder = ''):
    file_path = os.path.join(folder, 'execution_control.json')
    with open(file_path, 'r') as file:
        section_schedule = json.load(file)
    return section_schedule

def f1_puntuation(posicion_str):
    try:
        posicion = int(posicion_str.rstrip('.'))
    except:
        posicion = 0
    if posicion == 1:
        return 25
    elif posicion == 2:
        return 18
    elif posicion == 3:
        return 15
    elif posicion == 4:
        return 12
    elif posicion == 5:
        return 10
    elif posicion == 6:
        return 8
    elif posicion == 7:
        return 6
    elif posicion == 8:
        return 4
    elif posicion == 9:
        return 2
    elif posicion == 10:
        return 1
    else:
        return 0

int_folders()
