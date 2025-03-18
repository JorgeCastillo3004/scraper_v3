from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from selenium import webdriver
from datetime import datetime
import pandas as pd
import random
import time
import json
import re
import os
from selenium.webdriver.support.ui import Select
from datetime import date, timedelta
import string

from common_functions import *
from data_base import *
from milestone1 import *
from milestone2 import *
from milestone3 import *
from milestone4 import *
# from milestone5 import *
from milestone6 import *
from milestone7 import *
from milestone8 import *

CONFIG = load_json('check_points/CONFIG.json')
database_enable = CONFIG['DATA_BASE']
if database_enable:
	con = getdb()

def main():
	main_extract_news_enable = False  	# 1
	create_leagues_flag = True 	    # 2
	teams_creation_flag = False	  	    # 3
	results_extraction_flag = False		# 4
	fixture_extraction_flag = False		# 5
	players_flag = False 				# 6
	live_games_flag = False	
	dict_sports = load_json('check_points/sports_url_m2.json')
	
	if main_extract_news_enable:
		main_extract_news(driver, ["FOOTBALL", "TENNIS", "GOLF", "BASKETBALL", "AMERICAN_SPORTS", "MOTORSPORT", "HOCKEY", "RUGBY_UNION", "COMBAT_SPORTS"], MAX_OLDER_DATE_ALLOWED = 30)
		#  s "FOOTBALL", "TENNIS", "BASKETBALL", "FEATURES", "AMERICAN_SPORTS",  "GOLF",Ready
	if create_leagues_flag:
		# create_leagues(driver, ["BOXING"])
		create_leagues(driver, ["MOTOR SPORT"])
		# ["FOOTBALL", "BASKETBALL","BASEBALL", "AM. FOOTBALL", "HOCKEY", "TENNIS","GOLF", "BOXING",'FORMULA 1']

	if teams_creation_flag:
		teams_creation(driver, ["FOOTBALL", "BASKETBALL","BASEBALL", "AM. FOOTBALL", "HOCKEY"])

	if results_extraction_flag:
		results_fixtures_extraction(driver, ["FORMULA 1"], name_section = 'results')		
		# results_fixtures_extraction(driver, ["FOOTBALL", "BASKETBALL","BASEBALL", "AM. FOOTBALL", "HOCKEY"], name_section = 'results')

	if fixture_extraction_flag:
		#"TENNIS","GOLF"
		results_fixtures_extraction(driver, ["FOOTBALL", "BASKETBALL","BASEBALL", "AM. FOOTBALL", "HOCKEY"], name_section = 'fixtures')

	if players_flag:
		players(driver, ["FOOTBALL", "BASKETBALL","BASEBALL", "AM. FOOTBALL", "HOCKEY"])

	if live_games_flag:
		update_lives_matchs(driver)
		# live_games(driver, ["FOOTBALL", "TENNIS", "BASKETBALL", "HOCKEY",
		# 			  "BASEBALL","BOXING", "VOLLEYBALL"])

if __name__ == "__main__":  	
	driver = launch_navigator('https://www.flashscore.com', headless = True)
	login(driver, email_= "jignacio@jweglobal.com", password_ = "Caracas5050@\n")
	main()
	# if database_enable:
	con.close()
	# driver.quit()