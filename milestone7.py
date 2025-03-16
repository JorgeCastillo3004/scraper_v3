from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import psycopg2
import shutil

from common_functions import *
from data_base import *
from milestone6 import *


def get_live_result(row):
	try:
		home_participant = row.find_element(By.CLASS_NAME, 'event__participant.event__participant--home.fontExtraBold').text
	except:
		home_participant = row.find_element(By.CLASS_NAME, 'event__participant.event__participant--home').text
	try:    
		away_participant = row.find_element(By.CLASS_NAME, 'event__participant.event__participant--away.fontExtraBold').text
	except:
		away_participant = row.find_element(By.CLASS_NAME, 'event__participant.event__participant--away').text

	home_result = row.find_element(By.CLASS_NAME, 'event__score.event__score--home').text
	away_result = row.find_element(By.CLASS_NAME, 'event__score.event__score--away').text
	html_block = row.get_attribute('outerHTML')
	match_id = random_id()
	result_dict = {'match_id':match_id,'match_date':'','start_time':'', 'end_time':'',\
						'name':home_participant + '-' + away_participant,'home':home_participant,'visitor':away_participant,\
						'home_result':home_result,  'visitor_result':away_result, 'place':''}
	return result_dict

# def give_click_on_live(driver, sport_name):
# 	# CLICK ON LIVE BUTTON
# 	if sport_name =='GOLF':
# 		section_title = "Click for player card!"
# 	else:
# 		section_title = "Click for match detail!"

# 	wait = WebDriverWait(driver, 10)
# 	# get list of games section all
# 	xpath_expression_game = '//div[@title="{}"]'.format(section_title)
# 	current_tab = driver.find_elements(By.XPATH, xpath_expression_game)

# 	# give click
# 	xpath_expression = '//div[@class="filters__tab" and contains(.,"LIVE")]'
# 	livebutton = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_expression)))
# 	livebutton.click()
# 	time.sleep(0.3)
# 	# after click, check results or empy page.
# 	try:
# 		nomatchs = driver.find_element(By.CLASS_NAME, 'nmf__title')
# 		print(nomatchs.text)
# 		option = 1
# 	except:		
# 		current_tab = driver.find_elements(By.XPATH, xpath_expression_game)
# 		option = 2

# 	# Continue option 2
# 	if option == 2:
# 		if len(current_tab) == 0:

# 			current_tab = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_expression_game)))
# 		# else:
# 		# 	element_updated = wait.until(EC.staleness_of(current_tab[-1]))
# 		return True
# 	else:
# 		return False

def get_live_match(driver, sport_name='FOOTBALL'):
	if sport_name=='FOOTBALL':
		sport_name = 'soccer'
	else:
		sport_name = sport_name.lower()
	
	rows = driver.find_elements(By.XPATH, '//div[@class="sportName {}"]/div'.format(sport_name))	
	enable_load = False
	list_match = []
	for index, row in enumerate(rows):
		try:			
			title = row.find_element(By.XPATH, './/div[@class="event__titleBox"]')
			enable_load = False
			league_country = row.find_element(By.XPATH, './/span[@class="event__title--type"]').text 
			league_name= row.find_element(By.XPATH, './/span[@class="event__title--name"]').text
			HTML = row.get_attribute('outerHTML')
			if 'pin--active"' in HTML:
				enable_load = True
		except:
			try:				
				if enable_load:
					game_results = get_live_result(row)
					HTML = row.get_attribute('outerHTML')
					game_results['league_name'] = league_name
					game_results['league_country'] = league_country
					list_match.append(game_results)
			except:
				pass
	return list_match

# def give_click_on_live_golf(driver):

def live_games(driver, list_sports):
	dict_sports_url = load_json('check_points/sports_url_m2.json')
	current_date = datetime.now().date()#.strftime('%H:%M:%S')
	print("Current_date: ", current_date, '\n')
	# date = dt_object.date()
	# time = dt_object.time()

	#############################################################
	# 				MAIN LOOP OVER LIST SPORTS 					#
	#############################################################
	start_time = time.time()
	print("start_time: ", start_time)
	for sport_name in list_sports:

		print_section("LIVE SECTION: " + sport_name, space_ = 50)

		#################################################
		# LOAD SPORT LINK
		wait_update_page(driver, dict_sports_url[sport_name], "container__heading")

		###################### LIVE SECTION ############################################
		# CLICK ON LIVE BUTTON
		if sport_name =='GOLF':
			section_title = "Click for player card!"
		else:
			section_title = "Click for match detail!"
		live_games_found = give_click_on_live(driver, section_title)
		###############################################################################
		# count = 0 # COMENT
		# while count < 1000: # COMENT
		if live_games_found:

			list_live_match = get_live_match(driver, sport_name=sport_name)
			print(len(list_live_match))
			print_section("SEARCHING LIVE MATCH", space_ = 50)
			for match_info in list_live_match:
				print(match_info)
				# get match id				
				match_id = get_match_id(match_info['league_country'],
					match_info['league_name'], current_date, match_info['name'])		
				match_id = '616126asd' 																	
				print("Match id: ", match_id)
				# Get score_id home and score_id visitor
				# {match_detail_id_visitor: False, match_detail_id_home:True}
				if match_id:
					dict_match_detail_id = get_math_details_ids(match_id) # UNCOMENT
					print("dict_match_detail_id: ", dict_match_detail_id)
					dict_match_detail_id = {'KAFHD3536':True, 'dkdfkd': False}

					for match_detail_id, home_flag in dict_match_detail_id.items():
						if home_flag:
							# Update home score
							params = {'match_detail_id': match_detail_id,
									'points': match_info['home_result'] }
							update_score(params)# UNCOMENT
						else:
							# Update visitor score
							params = {'match_detail_id': match_detail_id,
									'points': match_info['visitor_result'] }
							update_score(params)# UNCOMENT
					print("Updated") # COMENT
				# count += 1
				# time.sleep(15)
	end_time = time.time()
	elapsed_time = end_time - start_time
	print("Complete time: ", elapsed_time)
		###################### LOOP OVER LIVE MATCHS #######################	

