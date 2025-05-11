from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import time
from IPython.display import clear_output
from IPython.display import display, HTML
import copy
from data_base import *
from common_functions import *
import sys

import sys
import time

def countdown_timer(seconds):
	"""
	Displays a countdown timer in the same terminal line, clearing the line properly.

	:param seconds: Total number of seconds for the countdown.
	"""
	try:
		while seconds:
			hrs, rem = divmod(seconds, 3600)
			mins, secs = divmod(rem, 60)
			timer_display = f"{hrs:02d}:{mins:02d}:{secs:02d}"
			sys.stdout.write(f"\r\033[K⏳ Countdown: {timer_display}")  # \033[K clears the line from cursor to end
			sys.stdout.flush()
			time.sleep(1)
			seconds -= 1
		sys.stdout.write("\r\033[K✅ Countdown complete!")        
		time.sleep(1)
	except KeyboardInterrupt:
		sys.stdout.write("\r\033[K⛔ Countdown interrupted.")
		time.sleep(1)

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
	if '~' in name:
		team1, team2 = name.split('~')
	else:
		team1, team2 = name.split('-')
	# xpath_expression = f'//*[@title="Click for match detail!" and contains(.,"{team1}") and contains(.,"{team2}")] '
	xpath_expression = f'//div[contains(@class, "match--live") and contains(.,"{team1}") and contains(.,"{team2}")]'	
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

def merge_dict(current_dict, new_dict):
    """
    Merge two nested match dictionaries by sport and match name.

    - Top-level keys are sports.
    - Second-level keys are match names.
    - If a match already exists under a sport, it's skipped or updated.
    - New sports and matches are added.

    :param current_dict: Existing dictionary of matches.
    :param new_dict: New dictionary to merge into current_dict.
    :return: Merged dictionary.
    """
    for sport in new_dict:
        if sport not in current_dict:
            # Add the entire sport category if not present
            current_dict[sport] = new_dict[sport]
        else:
            for match_name in new_dict[sport]:
                if match_name not in current_dict[sport]:
                    # Add new match under existing sport
                    current_dict[sport][match_name] = new_dict[sport][match_name]
                else:
                    # Optional: overwrite if you want to update existing match data
                    # current_dict[sport][match_name] = new_dict[sport][match_name]
                    pass  # Leave existing data as is
    return current_dict

def update_dict(current_dict, dict_ready, initial_time, delay):
	"""
	Update the dictionary with new match data if the delay has passed.

	:param current_dict: Current dictionary of matches
	:param initial_time: Last update time
	:param delay: Time delay as timedelta
	:return: Updated dictionary, new initial_time
	"""
	global delta_time	
	if datetime.now() >= initial_time + delay:
		results = get_match_by_day_internal(delta_time, interval=1)  # Get matches for the current day
		new_dict = build_dict_match(results)         # Rebuild dictionary
		for sport_name in dict_ready.keys():			
			if '***' in sport_name:
				sport, name = sport_name.split('***')
			elif '-' in sport_name:
				sport, name = sport_name.split('-')
			current_dict[sport].pop(name)
		# update dict_ready
		copy_dict_ready = dict_ready.copy()
		for sport_name, time_saved in dict_ready.items():
			if datetime.now() > time_saved + timedelta(hours=2):
				copy_dict_ready.pop(sport_name)
		dict_ready = copy_dict_ready

		current_dict = merge_dict(current_dict, new_dict)
		initial_time = datetime.now()                    # Reset the initial time
		print(f"[{initial_time.strftime('%H:%M:%S')}] Dictionary updated.")		
	return current_dict, initial_time

def update_match(match_element, match, sport_name, name, dict_ready):	
	# update match status							
	match_status = match_element[0].find_element(By.CLASS_NAME, 'event__stage--block').text
	print("Match name: ", name, "Status: ", match_status)
	if match_status !='Finished':
		status = 'in progress'
	elif match_status =='Finished':
		status = 'completed'
		print("Match Finished deleted: ", name)
		dict_ready[sport_name + "***" + name] = datetime.now()		

	update_match_status({'match_id':match['match_id'], 'status':status})
	update_match_score(match_element[0], match['match_id'])	

def check_today_match_dict(dict_pending):	
	print(dict_pending)
	for sport_name, dict_match in dict_pending.items():
		print_section(sport_name)
		for match_name in dict_match.keys():
			print(match_name, dict_match.keys())

# Initial setup
local_time = datetime.now()
initial_time = datetime.utcnow()
delta_time = int((initial_time -  local_time).total_seconds()//3600)
# delay = timedelta(hours=1)
delay = timedelta(minutes=1)

def update_lives_matchs(driver):
	
	# Initial setup
	global delta_time, initial_time, delay
	# delay = 1 # time in hours to update match dict.
	dict_sports_url = load_json('check_points/sports_url_m2.json')
	results = get_match_by_day_internal(delta_time, interval=4)	
	dict_pending = build_dict_match(results)	
	# check_today_match_dict(dict_pending)
	details = {'section':'live'}
	dict_ready = {}	
	# local_time_naive = datetime.now()
	# utc_time_naive = datetime.utcnow()
	# current_date = datetime.now().date()
	
	# initial_time = datetime.now()
	while True:
		# try:
			for sport_name, dict_matchs in dict_pending.items():

				print_section(sport_name, space_= 10)				
				wait_update_page(driver, dict_sports_url[sport_name], "container__heading")# LOAD SPORT LINK				
				live_games_found = give_click_on_live(driver, sport_name) # give click in live section
				details.update({'sport':sport_name})

				for name, match in dict_matchs.items(): # navigate on matchs by sport
					if sport_name +"***"+ name not in dict_ready.keys():						
						# stop_validate()
						if live_games_found and (len(name.split('-')) == 2 or len(name.split('~')) == 2) :# DELETE SECOND PART							
							# print_section("Search in lives section ", space_ = 10)
							match_element = find_element_match(driver, name) # search match that contains team1 and team2						
							if match_element:
								update_match(match_element, match, sport_name, name, dict_ready)
							# else:
							# 	print("Match don't found in live section")			
			current_dict, initial_time = update_dict(dict_pending, dict_ready, initial_time, delay)							
			countdown_timer(180)
			# stop_validate()
		# except Exception as error:
		# 	print(error)
			# log_selenium_error(driver, error, details)

if __name__ == "__main__":	
	update_lives_matchs()