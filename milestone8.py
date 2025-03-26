from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from IPython.display import clear_output
from IPython.display import display, HTML
import copy
from data_base import *
from common_functions import *
# Function to display a value that constantly changes
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

# from main import database_enable
# from common_functions import utc_time_naive



def build_dict_match(results):
	dict_pending = {}
	for sport, league_name, league_country, match_date, match_time, name, match_id in results:
		if sport not in dict_pending.keys():
			dict_pending[sport] = {}

		dict_pending[sport][name] = {'match_id' : match_id, 'match_time' : match_time
							,'country_league' : league_country + '_' +league_name}
	return dict_pending

def update_match_score(match_element, match_id):	
	dict_match_detail_id = get_math_details_ids(match_id) # get match detail from database, two registers home-away
	
	line_match = ''
	for match_detail_id, home_flag in dict_match_detail_id.items():
		if home_flag:
			# Update home score
			result = match_element.find_element(By.CLASS_NAME, 'event__score.event__score--home').text
			params = {'match_detail_id': match_detail_id,                          
					'points': result}
			update_score(params)# UNCOMENT			
			line_match += f" Home: {result} "

		else:
			#Update visitor score
			result = match_element.find_element(By.CLASS_NAME, 'event__score.event__score--away').text
			params = {'match_detail_id': match_detail_id,
					'points': result }
			update_score(params)# UNCOMENT			
			line_match += f" Away: {result} "
	print_section(line_match, space_ = 10)

def find_element_match(driver, name):
	wait = WebDriverWait(driver, 10)
	row = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@title="Click for match detail!"]')))
	team1, team2 = name.split('-')
	# xpath_expression = f'//*[@title="Click for match detail!" and contains(.,"{team1}") and contains(.,"{team2}")] '
	xpath_expression = f'//div[contains(@class, "match--live") and contains(.,"{team1}") and contains(.,"{team2}")]'
	print("xpath_expression: ",xpath_expression)
	return driver.find_elements(By.XPATH, xpath_expression)

def give_click_on_live(driver, sport_name,section = "LIVE"):
	# CLICK ON LIVE BUTTON
	if sport_name =='GOLF':
		section_title = "Click for player card!"
	else:
		section_title = "Click for match detail!"

	wait = WebDriverWait(driver, 10)
	# get list of games section LIVE
	xpath_expression_game = '//*[@title="{}"]'.format(section_title)
	print("xpath_expression_game: ", xpath_expression_game)
	current_tab = driver.find_elements(By.XPATH, xpath_expression_game)

	# give click
	webdriver.ActionChains(driver).send_keys(Keys.HOME).perform()
	xpath_expression = f'//div[@class="filters__tab" and contains(.,"{section}")]'
	livebutton = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_expression)))
	livebutton.click()				# UNCOMENT
	time.sleep(0.3)
	# after click, check results or empy page.
	# Find all the matchs availables
	try:
		nomatchs = driver.find_element(By.CLASS_NAME, 'nmf__title')
		print(nomatchs.text)
		option = 1
	except:		
		current_tab = driver.find_elements(By.XPATH, xpath_expression_game)
		option = 2

	# Continue option 2
	if option == 2:
		if len(current_tab) == 0:

			current_tab = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_expression_game)))
		# else:
		# 	element_updated = wait.until(EC.staleness_of(current_tab[-1]))
		return True
	else:
		return False

def update_lives_matchs(driver):
	
	while True:
		dict_sports_url = load_json('check_points/sports_url_m2.json')
		# All that in infine loop, controlled by execution control file.
		results = get_match_by_day() # get match for current date.
		dict_pending = build_dict_match(results) # buil dict_pending, by sport and match
		print("Sports keys: ", dict_pending.keys())		
		dict_finished = {}
		local_time_naive = datetime.now()
		utc_time_naive = datetime.utcnow()
		current_date = datetime.now().date()

		# duration = 60
		count = 0
		count_break = 0
		
		dict_pending_len = {sport_name: len(dict_pending[sport_name]) for sport_name in dict_pending.keys()}

		while current_date == datetime.now().date() and len(dict_pending)!= 0:
			# Record the start time
			start_time = time.time()
			dict_pending_copy = copy.deepcopy(dict_pending)
			
			for sport_name, dict_matchs in dict_pending.items():			

				print("Match pending: ", len(dict_pending[sport_name]), '/', dict_pending_len[sport_name])
				print(dict_pending[sport_name])

				print_section(sport_name, space_= 10)
				# LOAD SPORT LINK
				wait_update_page(driver, dict_sports_url[sport_name], "container__heading")

				###################### LIVE SECTION ############################################    
				live_games_found = give_click_on_live(driver, sport_name)
				############################################################################### 
				utc_time_naive = datetime.utcnow()
				for name, match in dict_matchs.items(): # navigate on matchs by sport
					print("Match name: ", name)
					match_delta = (datetime.combine(datetime.min, match['match_time']) + timedelta(hours=2)).time()
					
					if live_games_found:# and utc_time_naive.time() >= match['match_time']\
						# and (len(name.split('-')) == 2):#\
						# and utc_time_naive.time() < match_delta:# Delete last condition
						print(name, "Match time: ", match['match_time'], utc_time_naive.time())
						print_section("Search in lives section ", space_ = 10)

						match_element = find_element_match(driver, name)
						
						if match_element:
							print("Match element: ", match_element[0].text)
							# update match status
							print("Update match :", name)
							# try:
							match_status = match_element[0].find_element(By.CLASS_NAME, 'event__stage--block').text
							print("Match name: ", name, "Status: ", match_status)
							if match_status !='Finished':
								status = 'in progress'
							elif match_status =='Finished':
								status = 'completed'
								dict_pending_copy[sport_name].pop(name)
								print("Match Finished delteted: ", name)
							# except:
							# 	status = 'R'
							# 	dict_pending_copy[sport_name].pop(name)
							# 	print("Match Finished delteted: ", name)

							update_match_status({'match_id':match['match_id'], 'status':status})
							update_match_score(match_element[0], match['match_id'])
							
						else:
							# Match don't found in live section.
							print("Search in results section")
							dict_pending_copy[sport_name].pop(name)
							
						count += 1 # DELETE
				count = 0
				
				if len(dict_pending_copy[sport_name]) == 0:
					dict_pending_copy.pop(sport_name)
				# stop_validate()
			#================= Load frecuency update live results==============#
			section_schedule = update_data()
			new_execution_schedule = section_schedule['LIVE_SECTION']['TIME']
			print("new_execution_schedule: ", new_execution_schedule)
			duration = int(new_execution_schedule.split('|')[1])
			print("Duration: ", duration)
			#==================================================================#
				
			elapsed_time = time.time() - start_time
			remaining_time = max(0, duration - elapsed_time)
			dict_pending = dict_pending_copy
			if len(dict_pending) == 0:
				time.sleep(duration)
			display_dynamic_value(remaining_time)
			# Clear the output of the current cell
			clear_output(wait=True)
			count_break += 1
		
			
		# if count_break == 4:
			
			
		# print(list_element.get_attribute('innerHTML'))
		# print("#"*20)
		# print(list_element.get_attribute('outerHTML'))


