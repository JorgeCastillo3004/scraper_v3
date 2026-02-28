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

#####################################################################
#					TENNIS PLAYER INFO EXTRACTION 					#
#####################################################################
def get_player_data_tennis(driver):
	dict_player_full_info = get_all_player_info_tennis(driver)    

	profile_block = driver.find_element(By.CLASS_NAME, 'container__heading')
	player_country = profile_block.find_element(By.XPATH, './/span[@class="breadcrumb__text"]').text
	if 'age' in dict_player_full_info.keys():
		date_str = dict_player_full_info['age'].split()[1].replace('(','').replace(')','')
		player_dob = datetime.strptime(date_str, "%d.%m.%Y")
	else:
		player_dob = datetime.strptime('01.01.1900', "%d.%m.%Y") 

	player_name = profile_block.find_element(By.XPATH, './/div[@class="heading__name"]').text
	player_name = clean_field(player_name)

	image_url = profile_block.find_element(By.XPATH, './/img').get_attribute('src')
	image_path = random_name_logos(player_name, folder = 'images/players/')	
	save_image(driver, image_url, image_path)
	player_photo = image_path.replace('images/players/','')
	
	player_id = random_id_text( player_country + player_name)
	player_dict = {'player_id':player_id, 'player_country':player_country, 'player_dob':player_dob, 'player_name':player_name,\
	 'player_photo':player_photo, 'player_position':''}
	return player_dict

def get_all_player_info_tennis(driver):
	player_block = driver.find_element(By.XPATH, '//div[@class="heading__info"]')
	lines = player_block.find_elements(By.XPATH, './/div[contains(@class, "heading__info")]')  # [contains(text(), "Age")]/span'
	dict_info = {}
	for line in lines:
		print("Curren_line: ",line.text, "#")
		if len(line.text) != 0 and ":" in line.text:
			tag, field = line.text.split(":")
			dict_info[tag] = field
	dict_info
	return dict_info

#####################################################################
#					GOLF PLAYER INFO EXTRACTION 					#
#####################################################################
def get_player_data_golf(driver):
    dict_player_full_info = get_all_player_info_golf(driver)    

    profile_block = driver.find_element(By.XPATH, '//div[@class="tournamentHeader__participantHeaderWrap"]')
    player_country = driver.find_element(By.XPATH, '//span[@class="golfSummaryTab__flag"]/span').get_attribute("title")
    if 'Date of Birth' in dict_player_full_info.keys():
        date_str = dict_player_full_info['Date of Birth'].replace(' ', '')
        print("date_str: ", date_str)
        player_dob = datetime.strptime(date_str, "%d.%m.%Y")
    else:
        player_dob = datetime.strptime('01.01.1900', "%d.%m.%Y") 

    player_name = profile_block.find_element(By.XPATH, './/div[@class="tournamentHeader__participantNameWrap"]').text
    player_name = clean_field(player_name)

    image_url = profile_block.find_element(By.XPATH, './/img').get_attribute('src')
    image_path = random_name_logos(player_name, folder = 'images/players/')	
    save_image(driver, image_url, image_path)
    player_photo = image_path.replace('images/players/','')

    player_id = random_id_text( player_country + player_name)
    player_dict = {'player_id':player_id, 'player_country':player_country, 'player_dob':player_dob, 'player_name':player_name,\
     'player_photo':player_photo, 'player_position':''}
    return player_dict

def get_all_player_info_golf(driver):
    dict_info = {}
    try:
        player_block = driver.find_element(By.XPATH, '//div[@class="tournamentHeader__participantHeaderWrap"]')
        lines = player_block.find_elements(By.XPATH, './/div[contains(@class, "tournamentHeader__participantHeaderInfo")]')
        
        for line in lines:
            print("Curren_line: ",line.text, "#")
            if len(line.text) != 0 and ":" in line.text:
                tag, field = line.text.split(":")
                dict_info[tag] = field
        return dict_info
    except:        
        return dict_info

#####################################################################
#					BOXING PLAYER INFO EXTRACTION 					#
#####################################################################
def get_player_data_boxing(driver):
    dict_player_full_info = get_all_player_info_boxing(driver)    

    profile_block = driver.find_element(By.XPATH, '//div[@class="container__heading"]')
    player_country = profile_block.find_element(By.XPATH, './/span[@class="breadcrumb__text"]').text
    if 'age' in dict_player_full_info.keys():
        date_str = dict_player_full_info['age'].split()[1].replace('(','').replace(')','')
        player_dob = datetime.strptime(date_str, "%d.%m.%Y")
    else:
        player_dob = datetime.strptime('01.01.1900', "%d.%m.%Y") 

    player_name = profile_block.find_element(By.XPATH, './/div[@class="heading__name"]').text
    player_name = clean_field(player_name)

    image_url = profile_block.find_element(By.XPATH, './/img').get_attribute('src')
    image_path = random_name_logos(player_name, folder = 'images/players/')	
    save_image(driver, image_url, image_path)
    player_photo = image_path.replace('images/players/','')

    player_id = random_id_text( player_country + player_name)
    player_dict = {'player_id':player_id, 'player_country':player_country, 'player_dob':player_dob, 'player_name':player_name,\
     'player_photo':player_photo, 'player_position':''}
    return player_dict

def get_all_player_info_boxing(driver):
    player_block = driver.find_element(By.XPATH, '//div[@class="container__heading"]')
    lines = player_block.find_elements(By.XPATH, './/div[contains(@class, "heading__info")]')  # [contains(text(), "Age")]/span'
    dict_info = {}
    for line in lines:
        print("Curren_line: ",line.text, "#")
        if len(line.text) != 0 and ":" in line.text:
            tag, field = line.text.split(":")
            dict_info[tag] = field
    return dict_info

#####################################################################
#					SQUAD INFO EXTRACTION 							#
#####################################################################

def get_all_player_info(driver):
	player_block = driver.find_element(By.CLASS_NAME, 'playerHeader__wrapper')
	lines = player_block.find_elements(By.XPATH, './/div[@class="playerInfoItem"]')

	dict_info = {}
	value = ''
	count = 0
	for line in lines:
		value_text = ''
		key = line.find_element(By.XPATH, './/strong').text.lower()
		key = re.sub(r':\s+', '', key)
		values = line.find_elements(By.XPATH, './/span')
		for index, value in enumerate(values):
			if index == 0:
				value_text = value.text
			else:
				value_text = value_text + value.text
		dict_info[key] = value_text	
	return dict_info

def get_player_data(driver):
	# sleep_time = random.uniform(2, 3.5)
	# Sleep for the generated time
	# time.sleep(sleep_time)
	dict_player_part1 = get_all_player_info(driver)

	profile_block = driver.find_element(By.ID, 'player-profile-heading')
	player_country = profile_block.find_element(By.XPATH, './/div/h2/span[2]').text

	print("Player keys info: ")
	print(dict_player_part1)
	if 'age' in dict_player_part1.keys():		
		# date_str = dict_player_part1['age'].split()[1].replace('(','').replace(')','')
		birth_date = re.findall(r'\d+\.\d+\.\d+', dict_player_part1['age'])
		if len(birth_date)!= 0:
			date_str = birth_date[0]
			player_dob = datetime.strptime(date_str, "%d.%m.%Y")
		del dict_player_part1['age']
	else:
		player_dob = datetime.strptime('01.01.1900', "%d.%m.%Y")		

	player_name = profile_block.find_element(By.CLASS_NAME, 'playerHeader__nameWrapper').text
	
	image_url = profile_block.find_element(By.XPATH, './/div/div/div/img').get_attribute('src')
	# image_path = random_name(folder = 'images/players/')
	image_path = random_name_logos(player_name, folder = 'images/players/')
	save_image(driver, image_url, image_path)
	player_photo = image_path.replace('images/players/','')
	print("New changes: ")
	try:
		player_position = profile_block.find_element(By.XPATH, './/div/strong').text
	except:
		player_position = profile_block.find_element(By.XPATH, './/div[@class="playerTeam"]/strong').text
		
	# player_position = profile_block.find_element(By.CLASS_NAME, 'typo-participant-info-bold').text	
	player_id = random_id()
	player_dict = {'player_id':player_id, 'player_country':player_country, 'player_dob':player_dob, 'player_name':player_name,\
	 'player_photo':player_photo, 'player_position':player_position, 'player_meta': str(dict_player_part1)}
	return player_dict

def get_squad_list(driver, sport_id = 'barketball'):
    if sport_id.lower() == 'football':
        sport_id = 'soccer'
    else:
        sport_id = sport_id.lower()
    # Function to get positions and url for each player
    class_name = '//div[@class="lineup lineup--{}"]'.format(sport_id)
    print("class_name: ", class_name)
    lineups_blocks = driver.find_element(By.XPATH, class_name)

    player_links = lineups_blocks.find_elements(By.XPATH, './/a[@class="lineup__cell lineup__cell--name"]')

    player_links = [link.get_attribute('href') for link in player_links]
    return player_links

def navigate_through_players(driver, country_league, team_name, season_id, team_id, list_squad, global_check_point, sport_name):
	enable_player = False
	for index, player_link in enumerate(list_squad):
		print("Current link: ", player_link)
		if player_link != 'https://www.flashscore.com/football/':
			##########  ENABLE CHECK POINT PLAYER ############################
			if global_check_point[sport_name]['M6']['player'] != '':
				if global_check_point[sport_name]['M6']['player'] == player_link:
					enable_player = True
			else:
				enable_player = True
			#################################################################		

			if enable_player:			
				wait_update_page(driver, player_link, 'container__heading')
				player_dict = get_player_data(driver)			
				player_dict['season_id'] = season_id
				player_dict['team_id'] = team_id			
				# name_ = player_dict['player_country'] + '_' + player_dict['player_name']		
				player_dict['player_name'] = player_dict['player_name'].replace("'", " ")		
				players_ready = check_player_duplicates(player_dict['player_country'], player_dict['player_name'], player_dict['player_dob'])
				print('-e-', len(players_ready))
				if len(players_ready) == 0:
					# players_ready.append(name_)
					if database_enable:
						print("New player created ")
						save_player_info(player_dict) # player
				else:
					# Load previous player id
					player_dict['player_id'] = players_ready[0]

				# SECTION CHECK TEAM PLAYER ENTITY
				team_player_entitiy = check_team_player_entitiy(player_dict['season_id'], player_dict['team_id'], player_dict['player_id'])
				print("Check team player entity: ", len(team_player_entitiy))
				if len(team_player_entitiy)== 0:
					save_team_players_entity(player_dict) # team_players_entity
				global_check_point[sport_name]['M6']['player'] = player_link
				save_check_point('check_points/global_check_point.json', global_check_point)
		else:
			issues_dict = load_check_point('check_points/issues/issues_player.json')
			if len(issues_dict) == 0:
				key = 0
			else:
				key = list(issues_dict.keys())[-1] + 1
			issues_dict[key] = {'sport':sport_name,'league':country_league,'team':team_name, 'index':index}
			save_check_point('check_points/issues/issues_player.json', issues_dict)

	global_check_point[sport_name]['M6']['player'] = ''
	save_check_point('check_points/global_check_point.json', global_check_point)
		
	# 	break
	# break

def get_check_point(dict_players_ready, sport_id, country_league, team_name):
	if sport_id in list(dict_players_ready.keys()):
		if country_league in list(dict_players_ready[sport_id].keys()):
			if team_name in list(dict_players_ready[sport_id][country_league].keys()):
				list_players_ready = dict_players_ready[sport_id][country_league][team_name]
			else:
				dict_players_ready[sport_id][country_league][team_name] = []
		else:		
			dict_players_ready[sport_id][country_league] = {}
			dict_players_ready[sport_id][country_league][team_name] = []
	else:
		dict_players_ready[sport_id] = {}
		dict_players_ready[sport_id][country_league] = {}
		dict_players_ready[sport_id][country_league][team_name] = []
	return dict_players_ready

def players(driver, list_sports):
	leagues_info_json = load_check_point('check_points/leagues_info.json')	
	dict_sport_id = get_dict_sport_id()	# GET DICT SPORT FROM DATABASE
	inverted_dict = {value: key for key, value in dict_sport_id.items()}
	
	#############################################################
	# 				SECTION TO LOAD CHECK POINT					#
	#############################################################

	global_check_point = load_check_point('check_points/global_check_point.json')
	# if 'M6' in global_check_point.keys():			
	# 	sport_point = global_check_point['M6']['sport']
	# 	league_point = global_check_point['M6']['league']
	# 	team_point  = global_check_point['M6']['team_name']		
	# else:
	# 	global_check_point['M6'] = {}
	# 	sport_point = ''
	# 	league_point = ''
	# 	team_point  = ''
	# 	global_check_point['M6']['player'] = ''

	enable_sport = False
	enable_league = False
	enable_team = False

	#############################################################
	# 				MAIN LOOP OVER LIST SPORTS 					#
	#############################################################
	for sport_name in list_sports:		
		print_section(sport_name, space_ = 50)
		if sport_name in global_check_point.keys():
			if 'M6' in global_check_point[sport_name].keys():				
				league_point = global_check_point[sport_name]['M6']['league']
				team_point  = global_check_point[sport_name]['M6']['team_name']				
			else:
				global_check_point[sport_name]['M6'] = {}
				sport_point = ''
				league_point = ''
				team_point  = ''
				global_check_point[sport_name]['M6']['player'] = ''
		else:
			global_check_point[sport_name] = {}
			global_check_point[sport_name]['M6'] = {}
			league_point = ''
			team_point  = ''
			global_check_point[sport_name]['M6']['player'] = ''

		print("LIST OF SPORTS IN JSON INFO")
		print(leagues_info_json.keys())
		
		for country_league, league_info in leagues_info_json[sport_name].items():
			print_section(country_league, space_ = 30)
			##########  ENABLE CHECK POINT LEAGUE #############
			print("country_league: ", country_league)
			if league_point != '':
				if league_point == country_league:
					enable_league = True
			else:
				enable_league = True
			#################################################				
			# for team_name, country_league_urls in league_info.items():
			##########  ENABLE CHECK POINT LEAGUE #############
			# if league_point != '':
			# 	if league_point == country_league:
			# 		enable_league = True
			# else:
			# 	enable_league = True
			#################################################
			path_leagues_teams_info = 'check_points/leagues_season/{}/{}.json'.format(sport_name, country_league)
			

			#     ENEABLE SEARCH IF FILE EXIST AND ENABLE CHECK POIN    #
			if os.path.isfile(path_leagues_teams_info) and enable_league:
				
				#############################################################
				print("Start extraction for league: ", country_league)
				global_check_point[sport_name]['M6']['league'] = country_league
				#############################################################
				# 				LOAD TEAMS INFO 		 					#
				#############################################################
				dict_country_league_season = load_check_point(path_leagues_teams_info)

				for team_name, team_info in dict_country_league_season.items():						
					print_section(team_name, space_ = 20)
					##########  ENABLE CHECK POINT TEAM #############
					if team_point != '':
						if team_point == team_name:
							enable_team = True
					else:
						enable_team = True
					#################################################
					if enable_team:
						# NAVIGATE THROUGH TEAMS
						global_check_point[sport_name]['M6']['team_name'] = team_name
						wait_update_page(driver, team_info['team_url'], "container__heading")
						print(" START PLAYER EXTRACTION")
						print(team_info['team_url'])
						# LOAD SQUAD URL, LOADED FROM TEAM INFO
						try:
							squad_button = driver.find_element(By.CLASS_NAME, 'tabs__tab.squad')
						except:
							try:
								squad_button = driver.find_element(By.XPATH, '//a[@title="Squad"]')
							except:
								break
						squad_url = squad_button.get_attribute('href')

						# WAIT UNTIL COMPLETE LOAD
						wait_update_page(driver, squad_url, 'heading')
						# sport_name = inverted_dict[sport_id]

						# GET LIST OF PLAYERS AVAILABLES
						list_squad = get_squad_list(driver, sport_id = sport_name)

						# NAVIGATE AND EXTRACT INFO FROM EACH PLAYER LINK
						navigate_through_players(driver, country_league, team_name, league_info['season_id'],\
											 team_info['team_id'], list_squad, global_check_point, sport_name)
						# global_check_point['M6'] = {'sport':sport_name, 'league':country_league, 'team_name':team_name}
				
	del global_check_point[sport_name]['M6']
	save_check_point('check_points/global_check_point.json', global_check_point)


