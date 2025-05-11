from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import time
import psycopg2
import shutil

from common_functions import *
from data_base import *

def buil_dict_map_values(driver):
	block = driver.find_element(By.CLASS_NAME, 'ui-table__header')
	cell_names = block.find_elements(By.XPATH,'.//div')
	dict_map_cell = {}
	for index, cell_name in enumerate(cell_names[2:]):
		cell_name = cell_name.get_attribute('title').replace(' ', '_')    
		dict_map_cell[index] = cell_name
	return dict_map_cell 

def get_teams_info_part1(driver):
	wait = WebDriverWait(driver, 10)
	# teams_availables = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ui-table__row')))
	xpath_expression = '//*[@id="tournament-table-tabs-and-content"]/div/div/div/div/div/div/span'	
	# all_cells = driver.find_elements(By.XPATH, xpath_expression)
	# print("All cells found: ", len(all_cells))
	try:
		all_cells = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_expression)))	
		dict_map_cell = buil_dict_map_values(driver)
	except:
		print("-not dict-map-cell-")
	teams_availables = driver.find_elements(By.CLASS_NAME, 'ui-table__row')	
	# time.sleep(5)
	dict_teams_availables = {}

	for team in teams_availables:
		team_name = team.find_element(By.XPATH, './/div[@class="tableCellParticipant"]').text
		team_position = team.find_element(By.XPATH, './/div[@class="tableCellRank"]').text
		team_position = int(re.search(r'\d+',team_position).group(0))
		games_hist = team.find_element(By.XPATH, './/div[@class="table__cell table__cell--form"]').text.split('\n')
		
		team_url = team.find_element(By.XPATH, './/a[@class="tableCellParticipant__name"]')
		team_statistic = team.find_elements(By.XPATH, './/span[@class=" table__cell table__cell--value   "]')    
		dict_statistic = {}
		print("-", team_name, end = ' ')
		for index, cell_value in enumerate(team_statistic):
			dict_statistic[dict_map_cell[index]] = cell_value.text
		
		dict_teams_availables[team_name] = {'team_url': team_url.get_attribute('href'), 'statistics':dict_statistic,\
										   'position':team_position, 'last_results': games_hist}
	return dict_teams_availables

def get_teams_info_part2(driver, league_inf, team_info):
	block_ligue_team = driver.find_element(By.CLASS_NAME, 'container__heading')
	# sport = block_ligue_team.find_element(By.XPATH, './/h2[@class= "breadcrumb"]/a[1]').text
	try:
		team_country = block_ligue_team.find_element(By.XPATH, './/h2[@class= "breadcrumb"]/a[2]').text
	except:
		team_country = block_ligue_team.find_element(By.XPATH, './/h2[@class= "breadcrumb"]/span[2]').text
	team_name = block_ligue_team.find_element(By.CLASS_NAME,'heading__title').text
	team_name = clean_field(team_name)	
	try:
		stadium = block_ligue_team.find_element(By.CLASS_NAME, 'heading__info').text
	except:
		stadium = ''
	image_url = block_ligue_team.find_element(By.XPATH, './/div[@class= "heading"]/img').get_attribute('src')
	image_path = random_name_logos(team_name, folder = 'images/logos/')
	save_image(driver, image_url, image_path)
	logo_path = image_path.replace('images/logos/','')
	# team_id = random_id_text(league_inf['sport_name'] + league_inf['league_name'] + team_name)
	team_id = generate_uuid()
	instance_id = generate_uuid()
	meta_dict = str({'statistics':team_info['statistics'], 'last_results':team_info['last_results']})
	team_info = {"team_id":team_id,"team_position":team_info['position'], "team_country":team_country,"team_desc":'', 'team_logo':logo_path,\
			 'team_name': team_name,'sport_id': league_inf['sport_id'], 'league_id':league_inf['league_id'], 'season_id':league_inf['season_id'],\
			 'instance_id':instance_id, 'team_meta':meta_dict, 'stadium':stadium, 'player_meta' :''}
	return team_info

# def navigate_through_teams(driver, sport_id, league_id, tournament_id, season_id, section = 'standings'):
# 	base_dir = 'check_points/{}/'.format(section)
# 	list_files = os.listdir(base_dir)
	
# 	for file_name in list_files:
# 		file_name = os.path.join(base_dir, file_name)
# 		dict_teams = load_check_point(file_name)
# 		count = 0
# 		for team_name, team_info in dict_teams.items():

# 			print("Save team statistics in database")
			
# 			wait_update_page(driver, team_info['team_url'], 'heading')

# 			dict_team = get_teams_info_part2(driver, sport_id, league_id, season_id, team_info)			
# 			dict_team['tournament_id'] = tournament_id
# 			print("Save in database teams info")			
# 			save_team_info(dict_team)
# 			dict_team['player_meta'] = ''
# 			save_league_team_entity(dict_team)

# 			squad_button = driver.find_element(By.CLASS_NAME, 'tabs__tab.squad')
# 			squad_url = squad_button.get_attribute('href')
# 			wait_update_page(driver, squad_url, 'heading')
# 			dict_squad = get_squad_dict(driver)
# 			navigate_through_players(driver, dict_squad)
# 			count += 1
# 			if count == 3:
# 				break ### URGENT DELETE #######
# 		# Remove processed file
# 		os.remove(file_name)

def create_folders(sport_name, country_league):
	# CREATE A FOLDER FOR EACH SPORT
	if not os.path.exists('check_points/leagues_season/{}/'.format(sport_name)):
		os.mkdir('check_points/leagues_season/{}/'.format(sport_name))

	# BUILD FILE NAME USED TO SAVE TEAM INFO	
	json_name = 'check_points/leagues_season/{}/{}.json'.format(sport_name, country_league)
	return json_name

def check_duplicate_save_team(dict_teams_db, dict_team, sport_id, team_name):
	print_section("dict team")
	print(dict_team)
	try:
		country_id = dict_team['country_id']
		team_name = dict_team['team_name']
		# dict_country = dict_teams_db[sport_id][country_id]							
		dict_team_db = dict_teams_db[sport_id][country_id][team_name]
		print("Team saved previously, showing dict team")
		print(dict_team_db)
	except:
		dict_team_db = {}

	if len(dict_team_db) != 0:
		print("TEAM HAS BEEN SAVED PREVIOUSLY")
		team_id = dict_teams_db[sport_id][country_id][team_name]['team_id']							
	else:
		print(" TEAM DON'T FOUND IN DATA_BASE")								
		print("SEARCH IN DATA BASE BY COUNTRY AND NAME")
		team_id_db = get_list_id_teams(sport_id, dict_team['country_id'], dict_team['team_name'])
		if len(team_id_db) == 0:
			print("TEAM CREATED AND SAVED IN DATA BASE")			
			save_team_info(dict_team)
			save_league_team_entity(dict_team)
			team_id = dict_team['team_id']
		else:
			print("TEAM HAS BEEN SAVED PREVIOUSLY")
			team_id = team_id_db[0]
	return team_id

def load_team_country_id(dict_team):
	country_id = get_country_id(dict_team['team_country'])								
	if not country_id:
		country_id = insert_country(dict_team['country'])
	return country_id

def print_sport_verification(sport_name, dict_sport_id):
	print(f"Sport {sport_name} was not created") if sport_name not in dict_sport_id.keys() else None
	print("sport_name in dict_sport_id.keys(): ", sport_name in dict_sport_id.keys())

def extract_save_team_info(driver, team_info_url, dict_teams_db, league_info, sport_id, team_name):
	wait_update_page(driver, team_info_url['team_url'], 'heading') # LOAD TEAM URL
	dict_team = get_teams_info_part2(driver, league_info, team_info_url) # GET TEAM INFO PART2: team_name, team_country, complete other fields.
	dict_team['country_id'] = load_team_country_id(dict_team) # CHECK IF COUNTRY_ID FROM TEAM IS IN DB, IF NOT CREATE IT
	team_id = check_duplicate_save_team(dict_teams_db, dict_team, sport_id, team_name) # SAVE TEAM IN BASE, CHECK DUPLICATE IN DB USING dict_teams_db
	return team_id

def save_check_update_country_league_file(dict_country_league_season, sport_name,
		 team_name,country_league, team_info_url, team_id, dict_check_point, json_name):
	#####################################################################################
	#      SAVE TEAM INFO IN DICT dict_country_league_season (one file by each league)  #
	#####################################################################################
	dict_country_league_season[team_name] = {'team_id':team_id, 'team_url':team_info_url['team_url']}
	dict_check_point['M3'] = {'SPORT_NAME':sport_name, 'LEAGUE':country_league, 'TEAM':team_name}
	save_check_point('check_points/global_check_point.json', dict_check_point)
	save_check_point(json_name, dict_country_league_season)

def teams_creation(driver, list_sports):
	print_section(" TEAMS CREATION")	
	# LOAD SPORT CONFIGURATION, ENABLE, INDIVIDUAL OR TEAM
	conf_enable_sport = check_previous_execution(file_path = 'check_points/CONFIG_M2.json')	
	
	# LOAD LEAGUES INFO FROM PREVIOUS STEP
	leagues_info_json = load_check_point('check_points/leagues_info.json')
	dict_sport_id = get_dict_sport_id()	# GET DICT SPORT FROM DATABASE

	dict_check_point = load_check_point('check_points/global_check_point.json')
	enable_sport = False
	enable_league = False
	enable_team = False

	#############################################################
	# 				MAIN LOOP OVER LIST SPORTS 					#
	#############################################################
	
	for sport_name in list_sports:
		
		print_sport_verification(sport_name, dict_sport_id) # CHECK IF SPORT WAS CREATED IN THE MILESTONE 2 (LEAGUES CREATION)
		if enable_extraction(dict_check_point, 'M3', 'SPORT_NAME', sport_name):
			enable_sport = True
		
		if not sport_name in ['TENNIS', 'GOLF'] and sport_name in dict_sport_id.keys() and enable_sport:

			sport_id = dict_sport_id[sport_name]
			dict_teams_db = get_dict_league_ready(sport_id = sport_id) # football id =  086475fd-053f-4f13-a2cb-f8670b22169d

			for country_league, league_info in leagues_info_json[sport_name].items():
				country_id = complete_league_info(league_info, sport_name, country_league, dict_sport_id)
				
				#################################################
				json_name = create_folders(sport_name, country_league)

				if enable_extraction(dict_check_point, 'M3', 'LEAGUE', country_league):
					enable_league = True

				if 'standings' in list(league_info.keys()) and enable_league: # and not os.path.isfile(json_name):  # CHECK IF THE FILE EXISTS; IF IT DOESN'T, IT MEANS IT HASN'T BEEN PROCESSED.
					# LOAD LEAGUE STANDING SECTION AND WAIT UNTIL LOAD
					print("#"*30, "START PROCESS LEAGUE {}".format(country_league), "#"*30)
					wait_update_page(driver, league_info['standings'], "container__heading")					
					
					dict_teams_availables = get_teams_info_part1(driver) # GET TEAM INFO PART1: team url, statistics, team position, last results
					print(f"NUMBER OF TEAMS FOUND: {len(dict_teams_availables)}")					
					dict_country_league_season = {}
					for team_name, team_info_url in dict_teams_availables.items():
						
						if enable_extraction(dict_check_point, 'M3', 'TEAM', team_name):
							enable_team = True
						if enable_team:
							count = 0
							while count < 5:
								print(f"count: {count}")
								try:									
									team_id = extract_save_team_info(driver, team_info_url, dict_teams_db, league_info, sport_id, team_name)
									save_check_update_country_league_file(dict_country_league_season, sport_name,
		 								team_name,country_league, team_info_url, team_id, dict_check_point, json_name)
									count = 5
								except:
									count = count +1																		
									print("Error in team extraction, max tries reached.") if count == 5 else None

					# Save file sport_country_league_season.jso					
					print("#"*30, f" TEAMS FROM LEAGUE {country_league, } ADDED {len(dict_country_league_season)}", "#"*30)
					
		if sport_name in dict_check_point['M3'].keys():
			del dict_check_point['M3'][sport_name]
			save_check_point('check_points/global_check_point.json', dict_check_point)
		# driver.quit()
		# except WebDriverException as e:
		# 	log_selenium_error(driver, e, details)

