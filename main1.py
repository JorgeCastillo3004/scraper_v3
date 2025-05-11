from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime
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
from milestone6 import *


def main_others():
	driver = launch_navigator('https://www.flashscore.com', headless = True)
	login(driver, email_= "jignacio@jweglobal.com", password_ = "Caracas5050@\n")
	day_execution_s1 = -1
	day_execution_s2 = -1
	day_execution_s3 = -1
	day_execution_s4 = -1
	day_execution_s5 = -1
	day_execution_s6 = -1
	execute_ready_s1 = False
	execute_ready_s2 = False
	execute_ready_s3 = False
	execute_ready_s4 = False
	execute_ready_s5 = False
	execute_ready_s6 = False

	list_s1 = []
	list_s2 = []
	list_s3 = []
	list_s4 = []
	list_s5 = []
	list_s6 = []
	old_execution_schedule_s1 = '*'
	old_execution_schedule_s2 = '*'
	old_execution_schedule_s3 = '*'
	old_execution_schedule_s4 = '*'
	old_execution_schedule_s5 = '*'
	old_execution_schedule_s6 = '*'
	section_schedule = update_data()
	while True:
		print("Start check: ")
		new_execution_schedule_s1 = section_schedule['EXTRACT_NEWS']['TIME']
		if new_execution_schedule_s1 != old_execution_schedule_s1:
			execution_schedule_s1 = new_execution_schedule_s1
			old_execution_schedule_s1 = execution_schedule_s1
			day_execution_s1 = -1
		enable_execution_s1, day_execution_s1, execute_ready_s1, execution_schedule_s1 = execute_section(execution_schedule_s1, day_execution_s1, execute_ready_s1)
		
		if enable_execution_s1:
			print("Execution news enable: ")
			main_extract_news(driver, section_schedule['EXTRACT_NEWS']['SPORTS'], section_schedule['EXTRACT_NEWS']['MAX_OLDER_DATE_ALLOWED'])			
			list_s1.append(datetime.now().time().strftime('%H:%M:%S'))
			print(list_s1, '\n')
			print("Show last executed time")

		new_execution_schedule_s2 = section_schedule['CREATE_LEAGUES']['TIME']
		if new_execution_schedule_s2 != old_execution_schedule_s2:
			execution_schedule_s2 = new_execution_schedule_s2
			old_execution_schedule_s2 = execution_schedule_s2
			day_execution_s2 = -1
		enable_execution_s2, day_execution_s2, execute_ready_s2, _ = execute_section(execution_schedule_s2, day_execution_s2, execute_ready_s2)
		if enable_execution_s2:
			create_leagues(driver, section_schedule['CREATE_LEAGUES']['SPORTS'])
			list_s2.append(datetime.now().time().strftime('%H:%M:%S'))
			print(list_s2, '\n')

		new_execution_schedule_s3 = section_schedule['CREATE_TEAMS']['TIME']
		if new_execution_schedule_s3 != old_execution_schedule_s3:
			execution_schedule_s3 = new_execution_schedule_s3
			old_execution_schedule_s3 = execution_schedule_s3
			day_execution_s3 = -1
		enable_execution_s3, day_execution_s3, execute_ready_s3, _ = execute_section(execution_schedule_s3, day_execution_s3, execute_ready_s3)
		if enable_execution_s3:
			teams_creation(driver, section_schedule['CREATE_TEAMS']['SPORTS'])
			list_s3.append(datetime.now().time().strftime('%H:%M:%S'))
			print(list_s3, '\n')

		new_execution_schedule_s4 = section_schedule['GET_RESULTS']['TIME']
		if new_execution_schedule_s4 != old_execution_schedule_s4:
			execution_schedule_s4 = new_execution_schedule_s4
			old_execution_schedule_s4 = execution_schedule_s4
			day_execution_s4 = -1
		enable_execution_s4, day_execution_s4, execute_ready_s4, execution_schedule_s4 = execute_section(execution_schedule_s4, day_execution_s4, execute_ready_s4)	
		if enable_execution_s4:
			results_fixtures_extraction(driver, section_schedule['GET_RESULTS']['SPORTS'], name_section = 'results')
			list_s4.append(datetime.now().time().strftime('%H:%M:%S'))
			print(list_s4, '\n')

		new_execution_schedule_s5 = section_schedule['GET_FIXTURES']['TIME']
		if new_execution_schedule_s5 != old_execution_schedule_s5:
			execution_schedule_s5 = new_execution_schedule_s5
			old_execution_schedule_s5 = execution_schedule_s5
			day_execution_s5 = -1
		enable_execution_s5, day_execution_s5, execute_ready_s5, execution_schedule_s5 = execute_section(execution_schedule_s5, day_execution_s5, execute_ready_s5)
		if enable_execution_s5:
			results_fixtures_extraction(driver, section_schedule['GET_FIXTURES']['SPORTS'], name_section = 'fixtures')
			list_s5.append(datetime.now().time().strftime('%H:%M:%S'))
			print(list_s5, '\n')

		new_execution_schedule_s6 = section_schedule['GET_PLAYERS']['TIME']
		if new_execution_schedule_s6 != old_execution_schedule_s6:
			execution_schedule_s6 = new_execution_schedule_s6
			old_execution_schedule_s6 = execution_schedule_s6
			day_execution_s6 = -1
		enable_execution_s6, day_execution_s6, execute_ready_s6, execution_schedule_s6 = execute_section(execution_schedule_s6, day_execution_s6, execute_ready_s6)
		if enable_execution_s6:
			players(driver, section_schedule['GET_PLAYERS']['SPORTS'])
			list_s6.append(datetime.now().time().strftime('%H:%M:%S'))
			print(list_s6, '\n')

		time.sleep(5)
		section_schedule = update_data()
		print("o-", end='')		

if __name__ == "__main__":	
	main_others()