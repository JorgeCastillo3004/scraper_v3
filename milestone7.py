from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import psycopg2
import shutil
from IPython.display import clear_output

from common_functions import *
from data_base import *
from milestone6 import *
from milestone8 import give_click_on_live

def display_dynamic_value(remaining_time):    
    value = 0
    while value < remaining_time:
        # Update the value
        value += 1
        # Display the value
#         display(HTML(f"<h1>{remaining_time - value}</h1>"))
        print("{:.2f}".format(remaining_time - value), end=' ')
        time.sleep(1)
        # Wait for a short period of time before updating again        
#         clear_output(wait=True)

def get_live_result(row):
	try:
		# work for: FOOTBALL
		home_participant = row.find_element(By.XPATH, './/*[contains(@class, "event__homeParticipant")]').text.strip()
		away_participant = row.find_element(By.XPATH, './/*[contains(@class, "event__awayParticipant")]').text.strip()
	except:
		# work for: BASKETBALL, 
		home_participant = row.find_element(By.XPATH, './/*[contains(@class, "event__participant--home")]').text.strip()
		away_participant = row.find_element(By.XPATH, './/*[contains(@class, "event__participant--away")]').text.strip()

	home_result = row.find_element(By.XPATH, './/*[contains(@class, "event__score--home")]').text.strip()
	away_result = row.find_element(By.XPATH, './/*[contains(@class, "event__score--away")]').text.strip()


	match_id = random_id()
	result_dict = {'match_id':match_id,'match_date':'','start_time':'', 'end_time':'',\
						'name':home_participant + '~' + away_participant,'home':home_participant,'visitor':away_participant,\
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

def get_live_match(driver, sport_name='FOOTBALL', max_count=10):
	if sport_name=='FOOTBALL':
		sport_name = 'soccer'
	else:
		sport_name = sport_name.lower()		
	
	rows = driver.find_elements(By.XPATH, '//div[@class="sportName {}"]/div'.format(sport_name))
	enable_load = False
	list_match = []
	for index, row in enumerate(rows):
		count = 0
		while count < max_count:
			try:
				try:			
					title = row.find_element(By.XPATH, './/span[contains(@class, "headerLeague__title-text")]').text.strip()			
					enable_load = False
					league_name = row.find_element(By.XPATH, './/a[@class="headerLeague__title"]').text
					league_country= row.find_element(By.XPATH, './/span[@class="headerLeague__category-text"]').text			
					pinned_element = row.find_element(By.XPATH, './/div[@data-testid="wcl-headerLeague"]')
					
					is_pinned = pinned_element.get_attribute("data-pinned") == "true"
					# is_pinned = True # DELETE

					if is_pinned:
						enable_load = True
						# print("PIN ACTIVATED")
					count = max_count
				except:
					# try:
					if enable_load:
						game_results = get_live_result(row)				
						game_results['league_name'] = league_name
						game_results['league_country'] = league_country
						game_results['status'] = update_status(row)
						print(f"HOME {game_results['home']}  {game_results['home_result']} VISITOR: {game_results['visitor']}  {game_results['visitor_result']}")
						print(f"STATUS: {game_results['status']}")
						list_match.append(game_results)				
					count = max_count
			except:
				count += 1
				print(f"error in ger info from row inside 'get_live_match' count: {count}")
	return list_match

def update_status(row, max_count = 10):
	# match_status = row.find_element(By.CLASS_NAME, 'event__stage').text
	count = 0
	while count < max_count:
		try:
			match_status = row.find_element(By.XPATH, './/div[@class="event__stage"]').text
			count = max_count
		except:			
			print(f"Try again find event stage, count: {count}")
			time.sleep(1)
			count += 1
	if match_status !='Finished':
		status = 'in progress'
	elif match_status =='Finished':
		status = 'completed'
	return status
		
# def give_click_on_live_golf(driver):

def live_games(driver, list_sports):
	dict_sports_url = load_json('check_points/sports_url_m2.json')

	while True:
		current_date = datetime.now().date()#.strftime('%H:%M:%S')
		print_section(" Current_date:{current_date} \n ")
		# date = dt_object.date()
		# time = dt_object.time()

		#############################################################
		# 				MAIN LOOP OVER LIST SPORTS 					#
		#############################################################
		start_time = time.time()
		print("start_time: ", start_time)
		for sport_name in list_sports:
			clear_output(wait=True)
			print_section("LIVE SECTION: " + sport_name, space_ = 50)

			#################################################
			# LOAD SPORT LINK
			wait_update_page(driver, dict_sports_url[sport_name], "container__heading")

			###################### LIVE SECTION ############################################
			# CLICK ON LIVE BUTTON

			live_games_found = give_click_on_live(driver, sport_name)
			###############################################################################
			# count = 0 # COMENT
			# while count < 1000: # COMENT
			if live_games_found:

				list_live_match = get_live_match(driver, sport_name=sport_name)
				print("Total math found: ",len(list_live_match))
				print_section("SEARCHING LIVE MATCH", space_ = 50)
				for match_info in list_live_match:
					# check if match is in database.
					# match_info = {'match_id': '3e18306d-f3b6-4787-a7f7-d49d3cee2de5', 'match_date': '', 'start_time': '', 'end_time': '',
					# 			'name': 'Genk~Club Brugge KV', 'home': 'Genk', 'visitor': 'Club Brugge KV', 'home_result': '3',
					# 				'visitor_result': '4', 'place': '', 'league_name': 'Jupiler Pro League', 'league_country': 'BELGIUM',
					# 				'status':'in progress'} # DELETE
					print(match_info)
					match_id = get_match_id(match_info['league_country'],
						match_info['league_name'], current_date, match_info['name']) # query to data base
					
					# match_id = '616126asd'
					print("Match id: ", match_id)
					# stop_validate2("SECCION MATCH INFO LOOP")
					# If match found proced to update values in database.
					if match_id:
						dict_match_detail_id = get_math_details_ids(match_id) # UNCOMENT
						print_section("MATCH FOUND PROCCED TO UPDATE VALUES.")
						print(dict_match_detail_id)
						# print("dict_match_detail_id: ", dict_match_detail_id)
						# dict_match_detail_id = {'KAFHD3536':True, 'dkdfkd': False}

						for match_detail_id, home_flag in dict_match_detail_id.items():
							if home_flag:
								print("Update home score")
								params = {'match_detail_id': match_detail_id,
										'points': match_info['home_result'] }
								update_score(params)# UNCOMENT
							else:
								print("Update visitor score")
								params = {'match_detail_id': match_detail_id,
										'points': match_info['visitor_result'] }
								update_score(params)# UNCOMENT
						update_match_status({'match_id':match_info['match_id'], 'status':match_info['status']}) # UNCOMENT
						print("Updated") # COMENT
					# count += 1
					# time.sleep(15)
			# stop_validate("PASSING TO NEXT SPORT: ")
		end_time = time.time()
		elapsed_time = end_time - start_time
		print("Complete time: ", elapsed_time)
			###################### LOOP OVER LIVE MATCHS #######################	
		display_dynamic_value(60)
