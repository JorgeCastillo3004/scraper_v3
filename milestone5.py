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

def get_time_date_format(date, section ='results'):
	if section == 'results':
		year_ = datetime.now().year -1
	else:
		year_ = datetime.now().year

	cleaned_text = re.findall(r'\d+\.\d+\.\s+\d+\:\d+', date)[0]
	
	dt_object = datetime.strptime(cleaned_text, '%d.%m. %H:%M')
	dt_object = dt_object.replace(year=year_)
	# Extract date and time
	date = dt_object.date()
	time = dt_object.time()
	return date, time

def get_result(row):
	match_date = row.find_element(By.CLASS_NAME, 'event__time').text	
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
	link_id = re.findall(r'id="[a-z]_\d_(.+?)\"', html_block)[0]
	url_details = "https://www.flashscore.com/match/{}/#/match-summary/match-summary".format(link_id)
	match_id = random_id()
	result_dict = {'match_id':match_id,'match_date':match_date,'start_time':'', 'end_time':'',\
					'name':home_participant + '-' + away_participant,'home':home_participant,'visitor':away_participant,\
					'home_result':home_result,  'visitor_result':away_result, 'link_details':url_details,'place':''}
	return result_dict

def get_unique_key(id_section_new, list_keys):
	id_section_new = id_section_new.replace(' ','_').replace('/','*-*')
	# Sections with the same name.
	if id_section_new in list_keys:
		id_section_base = id_section_new
		count_sub_rounds = 1
		id_section_new = id_section_base +'_' +str(count_sub_rounds)
		while id_section_new in list_keys:
			count_sub_rounds += 1
			id_section_new = id_section_base +'_' +str(count_sub_rounds)
	return id_section_new

def extract_info_results(driver, start_index, results_block, section_name, country_league):
	global count_sub_section, event_number, current_section_name, current_id_section, dict_rounds, new_section_name
	for processed_index, row in enumerate(results_block[start_index:]):	
		print(processed_index, end =' - ')
		try:
			HTML = row.get_attribute('outerHTML')
			# print(HTML, '\n'*2)
			class_name_section = re.findall(r'icon--flag.event__title fl_\d+', HTML)[0].replace(' ', '.')
			# new_section_name = row.find_element(By.CLASS_NAME, class_name_section).text
			# new_section_name = new_section_name.replace(' ', '_').replace('\n', '_').replace('/','*-*')
			os.mkdir("check_points/{}/{}".format(section_name, country_league))
			# print("End Section 1")
		except:
			try:
				# print("Init Section 2")
				result = get_result(row)
				dict_rounds[current_id_section][event_number] = result
				event_number += 1				
				# print("End Section 2")
			except:
				# Get Rounds block
				# print("Init Section 3")
				try:
					# Only get section name or ROUND name
					id_section_new = row.find_element(By.CLASS_NAME, 'event__title--name').text.replace(' ','_').replace('/','*-*')
					#id_section = row.find_element(By.CLASS_NAME, 'event__round event__round--static').text.replace(' ','_')
				except:
					# Else get all available text					
					id_section_new = get_unique_key(row.text, dict_rounds.keys())
				# print("End Section 3")
				if count_sub_section != 0:
					# save current dict
					# stop_validate()
					file_name = 'check_points/{}/{}/{}.json'.format(section_name, country_league, current_id_section)
					# print("file_name: ", file_name)
					# print("confirm file exist: ", os.path.isfile(file_name))
					# print("dict_rounds: ",dict_rounds)
					save_check_point(file_name, dict_rounds[current_id_section])
					webdriver.ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
				
				current_id_section = id_section_new
				current_section_name = country_league # new_section_name
				dict_rounds[id_section_new] = {}
				count_sub_section += 1
				event_number = 0
	return start_index + processed_index

def click_show_more_rounds(driver, current_results, section_name):
	wait = WebDriverWait(driver, 10)
	webdriver.ActionChains(driver).send_keys(Keys.END).perform()
	webdriver.ActionChains(driver).send_keys(Keys.PAGE_UP).perform()
	webdriver.ActionChains(driver).send_keys(Keys.PAGE_UP).perform()
	time.sleep(1.5)
	print("Action click more rounds: ---")
	show_more_list = driver.find_elements(By.CLASS_NAME, 'event__more.event__more--static')
	old_len = len(current_results)
	xpath_expression = '//div[@class="leagues--static event--leagues {}"]/div/div'.format(section_name)
	if len(show_more_list) != 0:
		show_more = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'event__more.event__more--static')))
		time.sleep(0.3)
		show_more.click()
		# Wait until upload page
		new_len = old_len 
		while new_len == old_len:
			time.sleep(0.3)			
			new_len = len(driver.find_elements(By.XPATH, xpath_expression))
		# wait.until(EC.staleness_of(current_results[1]))
		return True
	else:
		return False

def confirm_results(driver, section_name, max_count = 10):
	wait = WebDriverWait(driver, 10)
	xpath_expression = '//div[@class="leagues--static event--leagues {}"]/div/div'.format(section_name)
	count = 0
	wait_element = True
	while wait_element:
		try:
			not_results = driver.find_element(By.ID, 'no-match-found')
			print('case no results')
			wait_element = False
			return []
		except:
			results_block = driver.find_elements(By.XPATH, xpath_expression)
			if len(results_block)!= 0:
				results_block = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_expression)))
				wait_element = False                
				return results_block
			if count == max_count:
				print(stop)
		time.sleep(0.3)

def navigate_through_rounds(driver, country_league, section_name = 'results'):
	global count_sub_section, event_number, dict_rounds	
	last_procesed_index = 0
	current_results = confirm_results(driver, section_name, max_count = 10)
	print("Total current results: ", len(current_results))
	count_sub_section = 0
	event_number = 0
	dict_rounds = {}
	
	while last_procesed_index < len(current_results):
		print("last_procesed_index: ", last_procesed_index)

		last_procesed_index = extract_info_results(driver, last_procesed_index, current_results, section_name, country_league)
		# more_rounds_loaded = click_show_more_rounds(driver, current_results, section_name) # UNCOMENT ## URGENT DELETE
		more_rounds_loaded = False ### URGENT DELETE
		print("Len list results not updated: ", len(current_results))
		if more_rounds_loaded:
			# Update of list of current results
			current_results = driver.find_elements(By.XPATH, xpath_expression)
		print("Len list results updated: ", len(current_results))
		last_procesed_index += 1

def get_match_info(driver, event_info):
	# Extract details about matchs
	match_country = driver.find_element(By.XPATH, '//span[@class="tournamentHeader__country"]').text.split(":")[0]
	event_info['match_country'] = match_country
	match_info_elements = driver.find_elements(By.XPATH, '//div[@class="matchInfoData"]/div')
	for element in match_info_elements:        
		field_name = element.find_element(By.CLASS_NAME, 'matchInfoItem__name').text.replace(':','')
		field_value = element.find_element(By.CLASS_NAME, 'matchInfoItem__value').text
		event_info[field_name] = field_value
	return event_info

def wait_load_details(driver, url_details):
	wait = WebDriverWait(driver, 10)
	block_info = driver.find_elements(By.XPATH,'//div[@class="matchInfoData"]')
	driver.get(url_details)
	if len(block_info) == 0:
		element = wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@class="matchInfoData"]')))
	else:
		wait.until(EC.staleness_of(block_info[0]))

def get_statistics_game(driver):
	wait = WebDriverWait(driver, 10)
	button_stats = driver.find_element(By.XPATH, '//button[contains(.,"Stats")]')
	button_stats.click()	
	# statistics = driver.find_elements(By.XPATH, '//div[@data-testid="wcl-statistics"]')
	statistics = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@data-testid="wcl-statistics"]')))
	statistics_info = {}
	for indicator in statistics:		
		stat_name = indicator.find_element(By.XPATH, './/div[@data-testid="wcl-statistics-category"]').text #data-testid="wcl-simpleText1		
		statistic_values = indicator.find_elements(By.XPATH, './/div[@data-testid="wcl-statistics-value"]')		

		for value in statistic_values:			
			if 'homeValue' in value.get_attribute('outerHTML'):
				stat_home = value.text
			if 'awayValue' in value.get_attribute('outerHTML'):
				stat_away = value.text

		statistics_info[stat_name] = {'home' : stat_home, 'away' : stat_away}
	return statistics_info

def get_complete_match_info(driver, country_league, sport_id, league_id, season_id, dict_country_league_season, \
										dict_country_league_check_point, dict_leagues_ready, section = 'results'):
	
	league_folder = 'check_points/{}/{}/'.format(section, country_league)
	if os.path.exists(league_folder):
		round_files = os.listdir(league_folder)
	else:
		round_files = []

	print(round_files, '\n')
	# load round ready:
	try:
		list_rounds_ready = dict_leagues_ready[country_league]
	except:
		list_rounds_ready = []
	
	for round_file in round_files:
		if not round_file.split('/')[-1] in list_rounds_ready:
			file_path = os.path.join(league_folder, round_file)
			print(file_path)
			round_info = load_json(file_path)        
			for event_index, event_info in round_info.items():

				url_details = event_info['link_details']
				wait_load_details(driver, url_details)
				event_info = get_match_info(driver, event_info)
				if section  =='results':
					event_info['statistic_info'] = get_statistics_game(driver)
				else:
					event_info['statistic_info'] = ''

				event_info['league_id'] = league_id
				event_info['match_date'], event_info['start_time'] = get_time_date_format(event_info['match_date'], section ='results')	
				event_info['end_time'] = event_info['start_time']
				# print("event_info: ", event_info)
				try:
					team_id_home = dict_country_league_season[event_info['home']]['team_id']
					team_id_visitor = dict_country_league_season[event_info['visitor']]['team_id']
				except:
					print("###"*80,"TEAM DON'T FOUND IN LIST OF FILES #########")
					break

				try:
					event_info['stadium_id'] = dict_country_league_season[event_info['visitor']]['stadium_id']
					print(" "*30, "STADIUM READY")
				except:
					print(" "*30, "STADIUM CREATED")
					event_info['stadium_id'] = random_id()

					if 'CAPACITY' in list(event_info.keys()):
						capacity = int(''.join(event_info['CAPACITY'].split()))
					else:
						capacity = 0

					if 'VENUE' in list(event_info.keys()):
						name_stadium = event_info['VENUE']
					else:
						name_stadium = ''

					dict_stadium = {'stadium_id':event_info['stadium_id'],'country':event_info['match_country'],\
								 'capacity':capacity,'desc_i18n':'', 'name':name_stadium, 'photo':''}
								 # ATTENDANCE
					dict_country_league_season[event_info['home']]['stadium_id'] = event_info['stadium_id']
					json_name = 'check_points/leagues_season/{}_{}.json'.format(sport_id, country_league)
					save_check_point(json_name, dict_country_league_season)					
					print(dict_stadium)
					if database_enable:
						print("############ Save stadium info ###################")
						save_stadium(dict_stadium)

				match_detail_id = random_id()
				score_id = random_id()
				dict_home = {'match_detail_id':match_detail_id, 'home':True, 'visitor':False, 'match_id':event_info['match_id'],\
							'team_id':team_id_home, 'points':event_info['home_result'], 'score_id':score_id}
				match_detail_id = random_id()
				score_id = random_id()
				dict_visitor = {'match_detail_id':match_detail_id, 'home':False, 'visitor':True, 'match_id':event_info['match_id'],\
							'team_id':team_id_visitor, 'points':event_info['visitor_result'], 'score_id':score_id}				

				print("Event info:")
				print(event_info)
				if database_enable:
					save_math_info(event_info)
					if section  =='results':
						save_details_math_info(dict_home)
						save_details_math_info(dict_visitor)
						save_score_info(dict_home)
						save_score_info(dict_visitor)
					print("s... db ", end='')
			list_rounds_ready.append(round_file.split('/')[-1])
			dict_leagues_ready[country_league] = list_rounds_ready
			dict_country_league_check_point[sport_id] = dict_leagues_ready
			save_check_point('check_points/country_leagues_results_ready.json', dict_country_league_check_point)
	if os.path.exists(league_folder):
		print("folder_path to delete: ", league_folder)
		shutil.rmtree(league_folder)

def pending_to_process(dict_country_league_check_point, sport_id, country_league):
	list_sports = list(dict_country_league_check_point.keys())
	if sport_id in list_sports:
		if country_league in list(dict_country_league_check_point[sport_id].keys()):
			return False, dict_country_league_check_point[sport_id]
		else:
			return True, dict_country_league_check_point[sport_id]
	else:
		return True, {}

def results_fixtures_extraction_v2(driver, name_section = 'results'):
	sports_dict = load_check_point('check_points/leagues_info.json')
	# dict_teams_db = {}
	dict_country_league_check_point = load_check_point('check_points/country_leagues_results_ready.json')
	for sport_id, sport_dict in sports_dict.items():
		# dict_teams_db = get_dict_teams(sport_id = 'FOOTBALL') # add return stadium result
		for country_league, country_league_urls in sport_dict.items():
			league_pending, dict_leagues_ready = pending_to_process(dict_country_league_check_point, sport_id, country_league)
			file_country_league_season = 'check_points/leagues_season/{}_{}.json'.format(sport_id, country_league)
			print(file_country_league_season)
			
			if os.path.isfile(file_country_league_season):
				print("Start extraction...")				
				dict_country_league_season = load_check_point(file_country_league_season)				
				print("Navigate navigate_through_rounds")
				wait_update_page(driver, country_league_urls[name_section], "container__heading")
				navigate_through_rounds(driver, country_league, section_name = name_section)
				get_complete_match_info(driver, country_league, sport_id, country_league_urls['league_id'],country_league_urls['season_id'],\
							 dict_country_league_season, dict_country_league_check_point, dict_leagues_ready, section='fixtures')
				# sport_dict[country_league] = []

CONFIG = load_json('check_points/CONFIG.json')
database_enable = CONFIG['DATA_BASE']
if database_enable:
	con = getdb()

# if __name__ == "__main__":  	
# 	driver = launch_navigator('https://www.flashscore.com', database_enable)
# 	login(driver, email_= "jignacio@jweglobal.com", password_ = "Caracas5050@\n")	
# 	main_m5(driver)
# 	if database_enable:
# 		con.close()
# 	driver.quit()