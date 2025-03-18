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

local_time_naive = datetime.now()
utc_time_naive = datetime.utcnow()
time_difference_naive = utc_time_naive - local_time_naive

def get_time_date_format(date, section ='results'):
    print('Input date format: ', date)
    # if section == 'results':
    #   year_ = datetime.now().year -1
    # else:
    #   year_ = datetime.now().year
    year_ = datetime.now().year
    try:
        cleaned_text = re.findall(r'\d+\.\d+\.\d+\s+\d+\:\d+', date)[0]
        dt_object = datetime.strptime(cleaned_text, '%d.%m.%Y %H:%M')
    except:
        try:
            cleaned_text = re.findall(r'\d+\.\d+\.\s+\d+\:\d+', date)[0]
            dt_object = datetime.strptime(cleaned_text, '%d.%m. %H:%M')
            dt_object = dt_object.replace(year=year_)
        except:
            cleaned_text = ''.join(re.findall(r'(\d+\.\d+\.)\-\d+\.\d+\.(\d+)', date)[0])
            dt_object = datetime.strptime(cleaned_text, '%d.%m.%Y')
    dt_object = dt_object + time_difference_naive
    # Extract date and time
    date = dt_object.date()
    time = dt_object.time()
    return date, time

def get_result(row, country_id, section = 'results'):
    print("################ INSIDE GET RESULT ################")
    print("Row: ", row.text)
    home_xpath_expression = ".//div[contains(@class, 'homeParticipant')]"
    away_xpath_expression = ".//div[contains(@class, 'awayParticipant')]"
    match_date = row.find_element(By.CLASS_NAME, 'event__time').text    
    try:
        # home_participant = row.find_element(By.CLASS_NAME, 'event__participant.event__participant--home.fontExtraBold').text        
        home_participant = row.find_element(By.XPATH, home_xpath_expression).text
    except:
        home_participant = row.find_element(By.CLASS_NAME, 'event__participant.event__participant--home').text
    try:
        away_participant = row.find_element(By.XPATH, away_xpath_expression).text
        # away_participant = row.find_element(By.CLASS_NAME, 'event__participant.event__participant--away.fontExtraBold').text
    except:
        away_participant = row.find_element(By.CLASS_NAME, 'event__participant.event__participant--away').text

    if section == 'results':
        home_result = row.find_element(By.CLASS_NAME, 'event__score.event__score--home').text
        away_result = row.find_element(By.CLASS_NAME, 'event__score.event__score--away').text
    else:
        home_result = ''
        away_result = ''
    html_block = row.get_attribute('outerHTML')
    link_id = re.findall(r'id="[a-z]_\d_(.+?)\"', html_block)[0]
    url_details = "https://www.flashscore.com/match/{}/#/match-summary/match-summary".format(link_id)
    match_id = random_id()
    result_dict = {'match_id':match_id,'match_date':match_date,'start_time':'', 'end_time':'',\
                    'name':home_participant + '-' + away_participant,'home':home_participant,'visitor':away_participant,\
                    'home_result':home_result,  'visitor_result':away_result, 'link_details':url_details,'place':'',
                    'country_id':country_id}
    print("Result dict: ", result_dict)
    
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

def extract_info_results_old(driver, start_index, results_block, section_name, country_league, list_rounds):
    global count_sub_section, event_number, current_id_section, dict_rounds, new_section_name
    dict_rounds = {}
    round_enable = False
    for processed_index, row in enumerate(results_block[start_index:]):     
        try:
            # SECTION MAIN TITLE, ONLY FIND TITLE, IT IS NOT USED
            HTML = row.get_attribute('outerHTML')
            title_section = re.findall(r'icon--flag.event__title fl_\d+', HTML)[0].replace(' ', '.')
        except:
            try:
                # SECTION TO FIND MATCH INFO, EXTRACT DETAILS               
                result = get_result(row, section_name = section_name)
                if round_enable:                    
                    dict_rounds[current_round_name][event_number] = result
                    event_number += 1
            except:
                # SECTION TO FIND ROUND NAME.
                try:
                    round_name = row.find_element(By.CLASS_NAME, 'event__title--name').text.replace(' ','_').replace('/','*-*')

                except:
                    round_name = get_unique_key(row.text, dict_rounds.keys())
                # SECTION TO CHECK ROUND SAVED PREVIOUSLY
                round_name = '_'.join(round_name.split())
                print("round_name: ", round_name)               
                if round_name in list_rounds:
                    round_enable = False
                else:
                    print("New round: ", round_name)
                    round_enable = True             
                # IF round dictionary IS FILLED PROCEED TO SAVE DICT FOR PROCESSING IN THE NEXT STAGE
                if len (dict_rounds)!= 0 and len(dict_rounds[current_round_name]) != 0:                 
                    list_rounds.append(current_round_name)                  
                    file_name = 'check_points/{}/{}/{}.json'.format(section_name, country_league, current_round_name)
                    folder_name = 'check_points/{}/{}/'.format(section_name, country_league)                    
                    print(file_name)
                    if not os.path.exists(folder_name):
                        os.mkdir(folder_name)
                    save_check_point(file_name, dict_rounds[current_round_name])
                    webdriver.ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
                # RESTAR NEW DICTIONARY AND UPDATE CURRENT NAMES
                current_round_name = round_name
                dict_rounds[current_round_name] = {}
                count_sub_section += 1
                event_number = 0
    print(round_enable)
    return start_index + processed_index, round_enable

def extract_info_results(driver, start_index, results_block, section_name, country_league, list_rounds_ready, country_id):

    print("Total rows: ",len(results_block))
     # list to save round name, index_start index_end
    dict_rounds_index = {}
    all_list_results = []
    count = 0
    #########################################################
    #               LOOP OVER ALL MATCH                     #
    #########################################################
    for processed_index, result in enumerate(results_block[start_index:]):
        print(result.text.replace('\n',' '))
        HTML = result.get_attribute('outerHTML')
        if 'event__round event__round--static' in HTML or 'event__header' in HTML: # TAKE ROUND NAME            
            if count == 1:
                list_index[1] = processed_index
                dict_rounds_index[round_name] = list_index
                count = 0
            if count == 0:
                list_index = [0, 0]
                round_name = get_unique_key(result.text, dict_rounds_index.keys())
                list_index[0] = processed_index + 1
                if not 'event__header' in HTML:
                    count = 1
        if 'Click for match detail!' in HTML: # EXTRACT MATCH INFO
            result = get_result(result, country_id, section = section_name)
            print("Result: ", result)
            all_list_results.append(result)
        else:
            all_list_results.append('')

    #######################################################################
    #  SAVE FILES BY ROUNDS AND ORGANIZE THEM ACCORDING TO THE MATCH      #
    #######################################################################
    if len(dict_rounds_index) != 0:
        for round_name, index_star_end in dict_rounds_index.items():            
            if not round_name in list_rounds_ready:
                # CREATE FOLDER AND FILE NAME.
                file_name = 'check_points/{}/{}/{}.json'.format(section_name, country_league, round_name)
                folder_name = 'check_points/{}/{}/'.format(section_name, country_league)        
                if not os.path.exists(folder_name):
                    os.mkdir(folder_name)
                # CREATE DICT WITH ALL ENVENTS INFO.
                event_number = 0
                dict_round = {}
                for index in range(index_star_end[0], index_star_end[1]):                   
                    if all_list_results[index] !='':
                        dict_round[event_number] = all_list_results[index]
                        event_number += 1
                # SAVE ROUND DICT
                save_check_point(file_name, dict_round)             
                envent_number = 0
                round_enable = True
            else:
                round_enable = False
    #######################################################################
    #                       CASE 2 UNIQUE ROUND                           #
    ####################################################################### 
    else:
        event_number = 0
        dict_round = {}
        for index, match_info in enumerate(all_list_results):
            if match_info != '':
                dict_round[index] = match_info

        # CREATE FOLDER AND FILE NAME.
        file_name = 'check_points/{}/{}/{}.json'.format(section_name, country_league, 'UNIQUE')
        folder_name = 'check_points/{}/{}/'.format(section_name, country_league)        
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
        
        # SAVE ROUND DICT
        round_enable = True
        save_check_point(file_name, dict_round)

    return start_index + processed_index, round_enable

def click_show_more_rounds(driver, current_results, section_name):
    wait = WebDriverWait(driver, 10)
    webdriver.ActionChains(driver).send_keys(Keys.END).perform()
    time.sleep(0.3)
    webdriver.ActionChains(driver).send_keys(Keys.PAGE_UP).perform()
    time.sleep(0.3)
    webdriver.ActionChains(driver).send_keys(Keys.PAGE_UP).perform()
    time.sleep(1.5)
    print("Action click more rounds: ---")
    show_more_list = driver.find_elements(By.CLASS_NAME, 'event__more.event__more--static')
    old_len = len(current_results)
    xpath_expression = '//div[@class="leagues--static event--leagues {}"]/div/div'.format(section_name)
    max_try = 0
    if len(show_more_list) != 0:
        show_more = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'event__more.event__more--static')))
        time.sleep(0.3)
        show_more.click()
        # Wait until upload page
        new_len = old_len 
        while new_len == old_len and max_try < 10:
            time.sleep(0.3)         
            new_len = len(driver.find_elements(By.XPATH, xpath_expression))
            max_try +=1
            print("-*-", end='')
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

def navigate_through_rounds(driver, country_league, country_id,  list_rounds ,section_name = 'results'):
    global count_sub_section, event_number  
    xpath_expression = '//div[@class="leagues--static event--leagues {}"]/div/div'.format(section_name)
    last_procesed_index = 0
    current_results = confirm_results(driver, section_name, max_count = 10)
    print("Total current results: ", len(current_results))
    count_sub_section = 0
    event_number = 0    
    
    while last_procesed_index < len(current_results):
        more_rounds_loaded = False
        print("last_procesed_index: ", last_procesed_index)
        
        last_procesed_index, click_more_enable = extract_info_results(driver, last_procesed_index,
                             current_results, section_name, country_league, list_rounds, country_id)
        click_more_enable = False
        if click_more_enable:
            more_rounds_loaded = click_show_more_rounds(driver, current_results, section_name) # UNCOMENT ## URGENT DELETE      
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

    # GET MATCH DATE COMPLETE.
    event_info['match_date'] = driver.find_element(By.CLASS_NAME, 'duelParticipant__startTime').text

    for element in match_info_elements:        
        field_name = element.find_element(By.CLASS_NAME, 'matchInfoItem__name').text.replace(':','')
        field_value = element.find_element(By.CLASS_NAME, 'matchInfoItem__value').text
        event_info[field_name] = field_value
    return event_info

def wait_load_details(driver, url_details):
    wait = WebDriverWait(driver, 10)
    block_info_before = driver.find_elements(By.XPATH,'//div[@class="matchInfoData"]')
    driver.get(url_details)
    try:
        wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@class="matchInfoData"]')))
    except:
        block_info_after = driver.find_elements(By.XPATH,'//div[@class="matchInfoData"]')

    if len(block_info_before) == 0:
        try:
            element = wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@class="matchInfoData"]')))
            return True
        except:
            return False
    else:
        wait.until(EC.staleness_of(block_info_before[0]))
        return True

def get_statistics_game(driver):
    wait = WebDriverWait(driver, 10)
    button_stats = driver.find_elements(By.XPATH, '//button[contains(.,"Stats")]')
    statistics_info = {}
    if len(button_stats)!=0:        
        button_stats[0].click() 
        # statistics = driver.find_elements(By.XPATH, '//div[@data-testid="wcl-statistics"]')
        statistics = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@data-testid="wcl-statistics"]')))
        
        for indicator in statistics:        
            stat_name = indicator.find_element(By.XPATH, './/div[@data-testid="wcl-statistics-category"]').text #data-testid="wcl-simpleText1       
            statistic_values = indicator.find_elements(By.XPATH, './/div[@data-testid="wcl-statistics-value"]')     

            for value in statistic_values:          
                if 'homeValue' in value.get_attribute('outerHTML'):
                    stat_home = value.text
                if 'awayValue' in value.get_attribute('outerHTML'):
                    stat_away = value.text

            statistics_info[stat_name] = {'home' : stat_home, 'away' : stat_away}
    return str(statistics_info)

def get_links_participants(driver):
    # main_m2(driver)
    home_links, away_links = [], []
    block_participants = driver.find_element(By.CLASS_NAME,'duelParticipant')
    block_participants.text
    # //*[contains(@class, 'home')]

    home_participant = block_participants.find_element(By.XPATH, './/div[contains(@class, "home")]')    
    participant_links = home_participant.find_elements(By.XPATH, './/a[@class="participant__participantLink"]')

    for link in participant_links:      
        home_links.append(link.get_attribute('href'))

    away_participant = block_participants.find_element(By.XPATH, './/div[contains(@class, "away")]')    
    participant_links = away_participant.find_elements(By.XPATH, './/a[@class="participant__participantLink"]')

    for link in participant_links:
        away_links.append(link.get_attribute('href'))

    return home_links, away_links

def save_participants_info(driver, player_links, sport_id, league_id, season_id, dict_players_ready):
    
    if len(player_links)==1:
        wait_update_page(driver, player_links[0], 'container__heading')
        player_dict = get_player_data_tennis(driver)        
        player_dict['season_id'] = season_id        
        player_dict['team_id'] = player_dict['player_id']
        player_dict['team_country'] = player_dict['player_country']
        player_dict['team_desc'] = ''
        player_dict['team_logo'] = player_dict['player_photo']
        player_dict['team_name'] = player_dict['player_name']
        player_dict['sport_id'] = sport_id
        player_dict['instance_id'] = random_id()
        player_dict['player_meta'] = ''
        player_dict['team_meta'] = ''
        player_dict['team_position'] = 0
        player_dict['league_id'] = league_id
        print("Save player info in database")

        team_name = player_dict['player_name']
        print("Save player info:")
        if not team_name in list((dict_players_ready.keys() ) ):            
            dict_players_ready[team_name] = {'team_id':player_dict['team_id']}
        player_list = check_player_duplicates(player_dict['player_country'], player_dict['player_name'], player_dict['player_dob'])
                
        if len(player_list) == 0:
            save_player_info(player_dict) # player
        save_team_info(player_dict) # team
        save_team_players_entity(player_dict) # team_players_entity             
        save_league_team_entity(player_dict) # league_team
        if len(player_list) != 0:
            print("PLAYER PREVIOUSLY CREATED ")
                

    if len(player_links)!=1:
        team_name = []
        for player_link in player_links:

            wait_update_page(driver, player_link, 'container__heading')
            player_dict = get_player_data_tennis(driver)
            player_dict['season_id'] = season_id            
            player_dict['team_country'] = player_dict['player_country']
            player_dict['team_desc'] = ''
            player_dict['team_logo'] = player_dict['player_photo']          
            player_dict['sport_id'] = sport_id
            player_dict['instance_id'] = random_id()
            player_dict['player_meta'] = ''
            player_dict['team_meta'] = ''
            player_dict['team_position'] = 0
            player_dict['league_id'] = league_id
            print("Save player info in database")
            
            team_name.append(player_dict['player_name'])
            name_ = player_dict['player_name']
            if not name_ in list((dict_players_ready.keys() ) ):
                dict_players_ready[name_] = {'team_id':player_dict['team_id']}
                save_player_info(player_dict) # player                  

        team_name = '-' .join(team_name)
        player_dict['team_id'] = random_id()
        dict_players_ready[team_name] = {'team_id':player_dict['team_id']}
        if not team_name in list((dict_players_ready.keys() ) ):
            save_team_info(player_dict)                 # team
            save_league_team_entity(player_dict)        # league_team
            save_team_players_entity(player_dict)       # team_players_entity
            
    return dict_players_ready, team_name
#             save_check_point('check_points/players_ready.json', dict_players_ready)

def get_complete_match_info(driver, country_league, sport_name, league_id, season_id,
                             dict_country_league_season, \
                             section = 'results'):
    match_issues = load_check_point('check_points/issues/issues_match.json')
    league_folder = 'check_points/{}/{}/'.format(section, country_league)
    if os.path.exists(league_folder):
        round_files = os.listdir(league_folder)
    else:
        round_files = []

    print(round_files, '\n')
    
    for round_file in round_files:
        # if not round_file.split('/')[-1] in list_rounds_ready:
            file_path = os.path.join(league_folder, round_file)         
            print("Current file: ")
            print(file_path)
            round_info = load_json(file_path)           
            for event_index, event_info in round_info.items():              
                print("#"*30, r"NEW EVENT {file_path}", "#"*30)
                print("Envent info: ***", event_info, "***")
                url_details = event_info['link_details']                
                print_section(url_details, space_ = 50)
                wait_load_details(driver, url_details)
                event_info = get_match_info(driver, event_info)
                # print("event_info part 1: ", event_info)
                event_info['tournament_id'] = ''
                event_info['statistic'] = get_statistics_game(driver)
                event_info['league_id'] = league_id
                event_info['season_id'] = season_id
                print("Match event: ", event_info['name'])
                date_copy = event_info['match_date']
                event_info['match_date'], event_info['start_time'] = get_time_date_format(event_info['match_date'], section ='results') 
                event_info['end_time'] = event_info['start_time']
                event_info['rounds'] = round_file.replace('.json', '')
                # print("event_info: ", event_info)
                try:
                    team_id_home = dict_country_league_season[event_info['home']]['team_id']
                    team_id_visitor = dict_country_league_season[event_info['visitor']]['team_id']
                except:
                    print("###"*80,"TEAM DON'T FOUND IN LIST OF FILES #########")
                    key_issue = sport_name + '_'+ country_league + '_' + date_copy + ' ' + event_info['name']
                    match_issues[key_issue] = url_details
                    save_check_point('check_points/issues/issues_match.json', match_issues)
                    break

                ############# STADIUM OR PLACE SECTION #########################
                try:
                    print("dict_country_league_season[event_info['home']]['stadium_id']")
                    print(dict_country_league_season[event_info['home']]['stadium_id'])
                    event_info['stadium_id'] = dict_country_league_season[event_info['home']]['stadium_id']
                    print(event_info['stadium_id'])
                    print(" STADIUM READY ")
                except:
                    print("  STADIUM CREATED  ")
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

                    dict_country_league_season[event_info['home']]['stadium_id'] = event_info['stadium_id']
                    json_name = 'check_points/leagues_season/{}/{}.json'.format(sport_name, country_league)
                    save_check_point(json_name, dict_country_league_season)                 
                    # print(dict_stadium)                   
                    save_stadium(dict_stadium)
                #################################################################
                match_detail_id = random_id()
                score_id = random_id()
                dict_home = {'match_detail_id':match_detail_id, 'home':True, 'visitor':False, 'match_id':event_info['match_id'],\
                            'team_id':team_id_home, 'points':event_info['home_result'], 'score_id':score_id}
                match_detail_id = random_id()
                score_id = random_id()
                dict_visitor = {'match_detail_id':match_detail_id, 'home':False, 'visitor':True, 'match_id':event_info['match_id'],\
                            'team_id':team_id_visitor, 'points':event_info['visitor_result'], 'score_id':score_id}

                # USED FOR FILES NOT COMPLETELY PROCESSED
                match_created = get_match_ready(event_info['match_id'])             
                # CHECK IF MATCH WAS CREATED PREVIOUSLY
                match_duplicate = check_match_duplicate(event_info['league_id'], event_info['match_date'], event_info['name'])
                if len(match_duplicate)!= 0:
                    print("MATCH SAVED PREVIOUSLY: ", match_duplicate)
                if len(match_created) == 0 and len(match_duplicate) == 0: #  and not match_created
                    print("NEW MATCH ADDED: ")
                    if section =="results":
                        # SET EVENT STATE
                        event_info['status'] = 'completed'
                    elif section =="fixtures":
                        # SET EVENT STATE
                        event_info['status'] = 'schedule'
                    save_math_info(event_info)
                    save_details_math_info(dict_home)
                    save_details_math_info(dict_visitor)

                    if section !="results":
                        dict_home['points'] = -1
                        dict_visitor['points'] = -1
                    save_score_info(dict_home)
                    save_score_info(dict_visitor)                   
            os.remove(file_path)            
            # print("#"*80, '\n'*2)
            # list_rounds_ready.append(round_file.split('/')[-1])
            # dict_leagues_ready[country_league] = list_rounds_ready
            # dict_country_league_check_point[sport_name] = dict_leagues_ready
            # save_check_point('check_points/country_leagues_results_ready.json', dict_country_league_check_point)
    if os.path.exists(league_folder):
        print("folder_path to delete: ", league_folder)
        shutil.rmtree(league_folder)

def save_team_player_single(driver, player_link , league_info):
    # LOAD PLAYER URL    
    if league_info['sport_name'] == 'GOLF':
        wait_update_page(driver, player_link, 'tournamentHeader__participantHeaderWrap')
        player_dict = get_player_data_golf(driver)
    if league_info['sport_name'] == 'TENNIS':
        wait_update_page(driver, player_link, 'container__heading')
        player_dict = get_player_data_tennis(driver)
    if league_info['sport_name'] =='BOXING':
        wait_update_page(driver, player_link, 'container__heading')
        player_dict = get_player_data_boxing(driver)

    player_dict['team_id'] = player_dict['player_id']
    player_dict['season_id'] = league_info['season_id']
    player_dict['team_country'] = player_dict['player_country']
    player_dict['team_name'] = player_dict['player_name']
    player_dict['team_desc'] = ''
    player_dict['team_logo'] = player_dict['player_photo']          
    player_dict['sport_id'] = league_info['sport_id']
    player_dict['instance_id'] = random_id()
    player_dict['player_meta'] = ''
    player_dict['team_meta'] = ''
    player_dict['team_position'] = 0
    player_dict['league_id'] = league_info['league_id']
    
    # CHECK IF PLAYER WAS CREATED PREVIOUSLY
    # player_id_list = check_player_duplicates(player_dict['player_country'], player_dict['player_name'], player_dict['player_dob'])
    player_id_duplicate = check_player_duplicates_id(player_dict['player_id'])
    print("Result player duplicate: ", player_id_duplicate)
    if not player_id_duplicate:
        save_player_info(player_dict) # player
    else:
        print('Player created previously')

    # CHECK IF TEAM WAS CREATED 
    # team_id_list = check_team_duplicates(player_dict['team_name'], player_dict['sport_id'])
    team_id_list = check_team_duplicates_id(player_dict['team_id'])
    print("team_id_list: ", team_id_list)
    if not team_id_list:
        save_team_info(player_dict) # team
        save_team_players_entity(player_dict) # team_players_entity     
    else:
        print('Team created previously')
        player_dict['team_id'] =  team_id_list[0]


    # CHECK IF TEAM WAS SAVED ON THIS SEASON
    team_season = check_team_season_duplicates(player_dict['league_id'], player_dict['season_id'], player_dict['team_id'])
    if not team_season:
        save_league_team_entity(player_dict) # league_team
    return player_dict['team_id']

def save_team_player_doubles(driver, player_links , league_info):
    # LOAD PLAYER URL
    team_members = []
    for player_link in player_links:
        wait_update_page(driver, player_link, 'container__heading')
        player_dict = get_player_data_tennis(driver)        
        player_dict['season_id'] = league_info['season_id']
        player_dict['team_country'] = player_dict['player_country']     
        player_dict['team_desc'] = ''
        player_dict['team_logo'] = player_dict['player_photo']          
        player_dict['sport_id'] = league_info['sport_id']
        player_dict['instance_id'] = random_id()
        player_dict['player_meta'] = ''
        player_dict['team_meta'] = ''
        player_dict['team_position'] = 0
        player_dict['league_id'] = league_info['league_id']
        team_members.append(player_dict['player_name'])
        # CHECK IF PLAYER WAS CREATED PREVIOUSLY
        player_id_list = check_player_duplicates(player_dict['player_country'], player_dict['player_name'], player_dict['player_dob'])
        if not player_id_list:
            save_player_info(player_dict) # player
        else:
            print('Player created previously')          
    
    # TEAM CREATION
    player_dict['team_id'] = random_id()
    player_dict['team_name'] = '-'.join(team_members)
    
    team_id_list = check_team_duplicates(player_dict['team_name'], player_dict['sport_id'])
    if not team_id_list:
        save_team_info(player_dict) # team
        save_team_players_entity(player_dict) # team_players_entity     
    else:
        print('Team created previously')
        player_dict['team_id'] =  team_id_list[0]


    # CHECK IF TEAM WAS SAVED ON THIS SEASON
    team_season = check_team_season_duplicates(player_dict['league_id'], player_dict['season_id'], player_dict['team_id'])
    if not team_season:
        save_league_team_entity(player_dict) # league_team
    return player_dict['team_id']

def get_complete_match_info_tennis(driver, league_info, section='results'):
    
    # LOAD ROUNDS FILES PREVIOUSLY CREATED
    league_folder = 'check_points/{}/{}/'.format(section, league_info['league_name'])# league_info['league_name']= country_league
    if os.path.exists(league_folder):
        round_files = os.listdir(league_folder)
    else:
        round_files = []

    print(round_files, '\n')
    
    for round_file in round_files:
        # if not round_file.split('/')[-1] in list_rounds_ready:
        file_path = os.path.join(league_folder, round_file)
        print(file_path)
        round_info = load_json(file_path)        
        for event_index, event_info in round_info.items():
            # GET MATCH DATA
            url_details = event_info['link_details']
            print("Current URL: ", url_details)
            wait_load_details(driver, url_details)
            event_info = get_match_info(driver, event_info)
            print("event_info tennis: ", event_info)
            
            event_info['statistic'] = get_statistics_game(driver)
            event_info['league_id'] = league_info['league_id']

            print("event_info['match_date']", event_info['match_date'])
            
            event_info['match_date'] = driver.find_element(By.CLASS_NAME, 'duelParticipant__startTime').text
            event_info['match_date'], event_info['start_time'] = get_time_date_format(event_info['match_date'], section ='results') 
            event_info['end_time'] = event_info['start_time']

            if section =="results" and not '-' in event_info['home_result']:
                # SET EVENT STATE
                event_info['status'] = 'R'
            elif section =="fixtures" or '-' in event_info['home_result']:
                # SET EVENT STATE
                event_info['status'] = 'P'
                # CHECK STATUS IS PENDING REPLACE RESULTS BY -1
                event_info['home_result'] = -1
                event_info['visitor_result'] = -1
                

            # print("event_info: ", event_info)
            home_links, away_links = get_links_participants(driver)
            print('home_links, away_links')
            print(home_links, away_links)

            # dict_season ; sport_id, league_id, season_id


            # CASE SINGLES          
            if len(home_links) == 1:  
                team_id_home = save_team_player_single(driver, home_links[0], league_info)# Pending pass sport_id
                team_id_away =  save_team_player_single(driver, away_links[0], league_info)# Pending pass sport_id
            else:
            # CASE DOUBLES 
                team_id_home = save_team_player_doubles(driver, home_links, league_info) # dict_season
                team_id_away = save_team_player_doubles(driver, away_links, league_info) # dict_season


            # dict_country_league_season, home_participant = save_participants_info(driver, home_links, sport_id, league_id, season_id, dict_country_league_season)
            # dict_country_league_season, away_participant = save_participants_info(driver, away_links, sport_id, league_id, season_id, dict_country_league_season)

            print("Salida del dict: ")
            # print(dict_country_league_season)         
            # team_id_home = dict_country_league_season[home_participant]
            # team_id_away = dict_country_league_season[away_participant]

            # LOAD PLACE OR STADIUM INFO AND SAVE IN DB.            
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

            ############# CHECK IF PLACE WAS SAVED PREVIOUSLY ######################### 
            stadium_results = get_stadium_id(name_stadium)
            if len(stadium_results) == 0:
                # dict_country_league_season[home_participant]['stadium_id'] = event_info['stadium_id']             
                print("############ Save stadium info ###################")
                save_stadium(dict_stadium)

            # CASE PLACE OR STADIUM SAVED PREVIOUSLY
            if len(stadium_results) != 0:
                event_info['stadium_id'] = stadium_results[0]
            #################################################################
            print("#"*80, '\n'*2)
            match_detail_id = random_id()
            score_id = random_id()
            dict_home = {'match_detail_id':match_detail_id, 'home':True, 'visitor':False, 'match_id':event_info['match_id'],\
                        'team_id':team_id_home, 'points':event_info['home_result'], 'score_id':score_id}
            match_detail_id = random_id()
            score_id = random_id()
            dict_visitor = {'match_detail_id':match_detail_id, 'home':False, 'visitor':True, 'match_id':event_info['match_id'],\
                        'team_id':team_id_away, 'points':event_info['visitor_result'], 'score_id':score_id}
            
            ################# COMPLETE DATE ######################
            event_info['season_id'] = league_info['season_id']
            event_info['tournament_id'] = ''
            event_info['rounds'] = round_file.replace('.json', '')
            print("Event info:")
            print(event_info)
            print("dict_home: ", dict_home)         
            save_math_info(event_info)
            save_details_math_info(dict_home)
            save_details_math_info(dict_visitor)
            save_score_info(dict_home)
            save_score_info(dict_visitor)
            print("SAVED IN DB ...", end='')
        # list_rounds_ready.append(round_file.split('/')[-1])
        # dict_leagues_ready[country_league] = list_rounds_ready
        # dict_country_league_check_point[sport_id] = dict_leagues_ready
        # save_check_point('check_points/country_leagues_results_ready.json', dict_country_league_check_point)
    if os.path.exists(league_folder):
        print("folder_path to delete: ", league_folder)
        shutil.rmtree(league_folder)

def pending_to_process(dict_country_league_check_point, sport_id, country_league):
    list_sports = list(dict_country_league_check_point.keys())
    if sport_id in list_sports:
        if country_league in list(dict_country_league_check_point[sport_id].keys()):
            return dict_country_league_check_point[sport_id]
        else:
            return dict_country_league_check_point[sport_id]
    else:
        return {}

# def build_check_point(sport_id, country_league):
#   check_point = {'sport_id':sport_id, 'country_league':country_league}
#   save_check_point('check_points/check_point_m4.json', check_point)

# def get_check_point(check_point, sport_id, country_league):
#   print(check_point)
#   if len(check_point)!= 0:
#       if check_point['sport_id'] == sport_id and check_point['country_league'] == country_league:
#           return True
#       else:
#           return False
#   else:
#       return True

def results_fixtures_extraction(driver, list_sports, name_section = 'results'): 
    # dict_country_league_check_point = load_check_point('check_points/country_leagues_results_ready.json')
    dict_sport_id = get_dict_sport_id() # GET DICT SPORT FROM DATABASE
    leagues_info_json = load_check_point('check_points/leagues_info.json')
    check_point = load_check_point('check_points/check_point_m4.json')  
    
    global_check_point = load_check_point('check_points/global_check_point.json')
    # if 'M4' in global_check_point.keys():         
    #   sport_point = global_check_point['M4']['sport']
    #   league_point = global_check_point['M4']['league']
    # else:
    #   sport_point = global_check_point['M4'] = {}
    #   sport_point = ''
    #   league_point = ''

    enable_sport = False
    enable_league = False   

    #############################################################
    #               MAIN LOOP OVER LIST SPORTS                  #
    #############################################################
    for sport_name in list_sports:
        if sport_name == 'FORMULA 1':
            sport_name = 'MOTOR SPORT'
            league_name = 'FORMULA 1'

        if sport_name in global_check_point.keys():
            if 'M4' in global_check_point[sport_name].keys():               
                league_point = global_check_point[sport_name]['M4']['league']
            else:
                global_check_point[sport_name]['M4'] = {}
                league_point = ''
        else:
            global_check_point[sport_name] = {}
            global_check_point[sport_name]['M4'] = {}
            league_point = ''
        ##########  ENABLE CHECK POINT SPORT #############
        # if sport_point != '':
        #   if sport_point == sport_name:
        #       enable_sport = True
        # else:
        #   enable_sport = True
        ###################################################################
        #                       TITLE SECTION                             #
        ###################################################################
        print_section(name_section.upper(), space_ = 50)
        print_section(sport_name, space_ = 50)
        #############################################################
        #               MAIN LOOP OVER LEAGUES                      #
        #############################################################
        
        for league_name, league_info in leagues_info_json[sport_name].items():
                print_section(league_name, space_ = 50)
                
                # for league_name, league_info in league_info.items():              
                # CHECK LIST OF ROUNDS READY BY LEAGUE NAME
                # dict_leagues_ready = pending_to_process(dict_country_league_check_point, sport_id, league_name)

                #####################################################################
                #       LOAD DICT FOR EACH LEAGUE                                   #
                #       'FOLDER /leagues_season/sport_name/LEAGUE_NAME.json         #
                #                   {team_name:                                     #
                #                       url :                                       #
                #                        team_id }                                  #               
                #                                                                   #
                #               get_dict_league_ready                               #
                #####################################################################
                # Exception for formula 1
                if sport_name != 'MOTOR SPORT':
                    # sport_name == 'MOTOR SPORT'
                    # league_name = 'FORMULA 1'

                    path_league_info = 'check_points/leagues_season/{}/{}.json'.format(sport_name, league_name)
                    print("League_id, season_id: ", league_info['league_id'], league_info['season_id'])
                    # save in the same dict league_name, sport_name
                    league_info['league_name'] = league_name
                    league_info['sport_name'] = sport_name
                    league_info['sport_id'] = dict_sport_id[sport_name]             
                    print_section("Section league info, country_id")
                    country_id = league_info['country_id']
                    print(country_id)
                    print(league_info)
                    # list_rounds = get_rounds_ready(league_info['league_id'], league_info['season_id'])
                    list_rounds = []
                    print("List old round from db ", list_rounds)
                    print("File to be search: ", path_league_info)

                
                # check_point_flag = get_check_point(check_point, sport_id, country_league)

                ##########  ENABLE CHECK POINT LEAGUE #############
                if league_point != '':
                    if league_point == league_name:
                        enable_league = True
                else:
                    enable_league = True
                #################################################

                #############################################################
                #   SECTION TO CHECK SPORT MODALITY TEAMS OR INDIVIDUAL     #
                #############################################################
                print(f"{sport_name} {league_name}")
                if sport_name in ['TENNIS', 'GOLF','BOXING', 'MOTOR SPORT']:
                    print("Case individual sports")
                    individual_sport = True
                    flag_to_continue = True
                else:
                    print('Other sports')
                    individual_sport = False
                    flag_to_continue = os.path.isfile(path_league_info) # CONFIRM IF TEAM WAS CREATED
                    dict_league = load_check_point(path_league_info)
                    print("List of teams: ", list(dict_league.keys()))
                if not flag_to_continue:
                    print_section("FILE NOT FOUND", space_ = 40)
                
                if flag_to_continue and enable_league:

                    global_check_point[sport_name]['M4']['league'] = league_name
                    save_check_point('check_points/global_check_point.json', global_check_point)
                    print("Start extraction...")

                    ##################### BLOCK FOR TEAM SPORTS AND TENNIS ###########################
                    # CHECK IF SECTION IS AVAILABLE FOR EACH LEAGUE
                    if not individual_sport or sport_name == 'TENNIS':
                        if name_section in list(league_info.keys()):

                            # LOAD SECTION RESULS OR FIXTURES                        
                            wait_update_page(driver, league_info[name_section], "container__heading")
                            
                            # START NAVIGATION THROUGH ROUNDS
                            print("Navigate navigate_through_rounds")
                            navigate_through_rounds(driver, league_name, country_id, list_rounds, section_name = name_section)

                            if not individual_sport:
                                get_complete_match_info(driver, league_name, sport_name, league_info['league_id'],
                                            league_info['season_id'], dict_league, section=name_section)
                            
                            elif sport_name=='TENNIS':                        
                                print_section('Individual sport boxing tennis')
                                get_complete_match_info_tennis(driver, league_info, section=name_section)
                    #################################################################################

                    # GOLF TOURNAMENT INFORMATION, ALL INFORMATION APPEAR IN THE SECTION SUMMARY
                    elif sport_name == 'GOLF':
                        print_section(f"Sport name {sport_name}")
                        dict_stadium = {'stadium_id':'golf97943','country':'',\
                                 'capacity':0,'desc_i18n':'', 'name':'', 'photo':''}
                        if check_stadium('golf97943'):
                            print("Golf stadium created")
                        else:
                            save_stadium(dict_stadium)

                        wait_update_page(driver, league_info['url'], "container__heading")
                        print("Start info extraction related to golf tournament")

                        # EXTRACT ALL THE BLOCKS FOR EACH TOURNAMENT
                        event_blocks = driver.find_elements(By.CLASS_NAME, 'sportName--noDuel.golf')
                        
                        print_section(f"event_blocks len: {len(event_blocks)}")

                        # for event_block in event_blocks:
                        for n in range(0, len(event_blocks)):
                            wait_update_page(driver, league_info['url'], "container__heading")
                            event_blocks = driver.find_elements(By.CLASS_NAME, 'sportName--noDuel.golf')
                            event_block = event_blocks[n]
                            event_info = get_tournament(driver, league_info, event_block)
                            print("event_info: ", event_info)
                            event_info['stadium_id'] = 'golf97943'
                            # CHECK IF TOURNAMENT WAS CREATED PREVIOUSLY
                            # NAVIGATE IN EACH PARTICIPANT AND BUILD A DICT FOR EACH ONE.
                            dict_players = get_dict_players(event_block)
                            
                            # SAVE MATCH IN DATA BASE
                            save_math_info(event_info)
                            for participant_index, participant_info in dict_players.items():
                                print(participant_index, participant_info)


                                # SAVE PLAYER AND TEAM INFO IN DATA BASE
                                team_id = save_team_player_single(driver, participant_info['player_url'] , league_info)
                                match_detail_id = random_id()
                                score_id = random_id()
                                dict_home = {'match_detail_id':match_detail_id, 'home':False, 'visitor':False, 'match_id':event_info['match_id'],\
                                            'team_id':team_id, 'points':participant_info['statistic']['Par'], 'score_id':score_id}

                                # LOAD PLACE OR STADIUM INFO AND SAVE IN DB.            
                                event_info['stadium_id'] = random_id()
                                if 'CAPACITY' in list(event_info.keys()):
                                    capacity = int(''.join(event_info['CAPACITY'].split()))
                                else:
                                    capacity = 0

                                if 'VENUE' in list(event_info.keys()):
                                    name_stadium = event_info['VENUE']
                                else:
                                    name_stadium = ''                   
                                dict_stadium = {'stadium_id':'golf97943','country':event_info['match_country'],\
                                             'capacity':capacity,'desc_i18n':'', 'name':name_stadium, 'photo':''}
                                             # ATTENDANCE

                                # SAVE MATCH DETAILS AND SCORE ENTITY
                                save_details_math_info(dict_home)
                                save_score_info(dict_home)
                        ##################################
                    elif sport_name == 'BOXING':
                        print("Start extraction to BOXING SPORT")
                        extract_info_boxing(driver, league_info)
                    elif sport_name == 'MOTOR SPORT' and league_name =='FORMULA 1':
                        print("FORMULA 1 INICIO EXTRACCION")
                        category_info = leagues_info_json["MOTOR SPORT"]['FORMULA 1']
                        wait_update_page(driver, category_info['calendar_link'], "container__heading")
                        grand_prix_links = get_grand_prix_links(driver)
                        for grand_prix_link in grand_prix_links:
                            print(grand_prix_link)
                            wait_update_page(driver, grand_prix_link, "container__heading")
                            
                            season_year = driver.find_element(By.CLASS_NAME, 'heading__info').text
                            
                            if season_year== '2024':
                                print("Current season")
                                create_events_f1(driver, category = 'FORMULA 1', season_year = '2024')
                            else:
                                break

    del global_check_point[sport_name]['M4']
    save_check_point('check_points/global_check_point.json', global_check_point)


def build_detail_score_dict(racer, dict_match):
    position, name, team, points = racer.find_elements(By.XPATH, './div')
    name = name.find_element(By.XPATH, './div/div/a').text
    position = position.text.replace('.','').replace(' ','')
    points.text
    team_id = random_id_text("MOTOR SPORT" + team.text+ name)
    dict_detail_score = {'match_detail_id': random_id() , 'home': False, 'visitor': False,
                             'match_id':dict_match['match_id'],'team_id':'',
                         'points':points, 'score_id':random_id()
                            }
    return dict_detail_score

def build_match_dict(driver, block_match, season_year, category):
    # DATE TIME AND STATUS 
    date_time = block_match.find_element(By.XPATH, './/span[@data-testid="wcl-simpleText1"]').text
    race_info = block_match.find_element(By.CLASS_NAME, "event__header.event__header--info").text.split(',')

    if len(race_info)== 4:
        date_time, place, descr, descr2  = race_info
        descr = descr + ',' + descr2

    if len(race_info)== 3:
        date_time, place, descr  = race_info        

    if 'Finished' in date_time:
        match_date, start_time = get_first_date_with_year(date_time)
        status = 'R'        
        place = clean_text(place)
        descr = clean_text(descr)
    else:
        match_date, start_time = get_time_date_format(date_time, section ='results')
        status = 'P'         
    
    place = clean_text(place)
    descr = clean_text(descr)

    grand_prix_title = block_match.find_element(By.XPATH, './/div[@class="event__titleBox"]').text
    grand_prix_title = ' '.join(grand_prix_title.split())
    match_country =  re.findall( r'\((.*?)\)', grand_prix_title)[0]
    
    
    
    # BUILD STADIUM DICT = AUTODROME_DICT
    autodrome_dict = {"stadium_id": random_id_text(place),
                        "capacity": 0,
                        "country": match_country,
                        "desc_i18n": descr,
                        "name": place,
                        "photo": ""
                        }
    
    # BUILD MATCH DICT
    dict_match = {'match_id':random_id_text(grand_prix_title + season_year), 'match_country':match_country, 'end_time':start_time,
                  'match_date':match_date, 'name':grand_prix_title,'start_time':start_time, 
                  'place':place, 'rounds':'',
                  'season_id':random_id_text(category + season_year),
                  'status':status, 'statistic':'',
                  'league_id':random_id_text("MOTOR SPORT" + category), 'stadium_id': autodrome_dict['stadium_id']
                 }
    return autodrome_dict, dict_match

def create_events_f1(driver, category = 'FORMULA 1', season_year = '2024'):

    block_matchs = driver.find_elements(By.CLASS_NAME, "sportName--noDuel.motorsport-auto-racing")

    print(len(block_matchs))
    
    for block_match in block_matchs:  
        title_event = block_match.find_element(By.CLASS_NAME, 'event__titleBox').text
        if 'Race' in title_event:
            print("title_event: ", title_event)
            # GET AUTODROME=STADIUM_ID, MATCH DICT
            list_fields = block_match.find_elements(By.XPATH, './div[@class="event__match event__main event__match--noDuel"]/div')
            list_fields = [field.text for field in list_fields]    

            autodrome_dict, dict_match = build_match_dict(driver, block_match, season_year, category)        
            print_section(f"{dict_match['name']} {dict_match['match_id']} ")
            if not check_stadium(autodrome_dict['stadium_id']):
                print("Create new stadium autodrome")        
                save_stadium(autodrome_dict)

            # CHECK DUPLICATES AND SAVE AUTODROME AND MATCH.
            if not get_match_ready(dict_match['match_id']):
                print("Create new match")
                save_math_info(dict_match)

            # GET PARTICIPANS MATCH DETAILS MATCH SCORE.
            racer_rows = block_match.find_elements(By.XPATH, './div[@title="Click for details!"]')
            for racer in racer_rows:
                list_contain = racer.find_elements(By.XPATH, './div')        
                list_contain = [field.text for field in list_contain]        
                if len(list_contain)==8: 
                    list_contain = list_contain[1:]        

                dict_result = dict(zip(list_fields, list_contain))

                print_section("crear team id")
                print(f"#{dict_result['TEAM']}#")
                if dict_result['TEAM'] == 'RB':
                    dict_result['TEAM'] = 'RB (F1 Team)'
                team_id = get_team_id_pilot(dict_result['DRIVER'], dict_result['TEAM'])
                print(dict_result)

    #             print(f"TEAM: {dict_result['#']} {dict_result['TEAM']} driver: {dict_result['DRIVER']}")
                print("team_id: ", team_id)
                dict_match_detail = {'match_detail_id':random_id(),'home':False, 'visitor':False,
                                    'match_id':dict_match['match_id'], 'team_id':team_id,
                                    'score_id':random_id(), 'points':f1_puntuation(dict_result['#'])}

                # INPUT VAR: team_id, match_id, dict_match['match_id']
                save_details_math_info(dict_match_detail)
                save_score_info(dict_match_detail)

def get_grand_prix_links(driver):
    list_links = driver.find_elements(By.XPATH, '//td[@class="seasonCalendar__name"]/a')
    grand_prix_links = []
    for link in list_links:    
        grand_prix_links.append(link.get_attribute('href'))
    return grand_prix_links

def get_match_link(driver, match):
    dict_match = {}
    html_block = match.get_attribute('outerHTML')
#     link_id = re.findall(r'id="[a-z]_\d_(.+?)\"', html_block)[0] # old regular expression
    link_id = re.findall(r'id="[a-z]_\d+\_(.+?)\"', html_block)[0]
    url_details = "https://www.flashscore.com/match/{}/#/match-summary/match-summary".format(link_id)
    dict_match['url'] = url_details    
    return dict_match

def get_result_boxig(driver):
    home_result = -1
    away_result = -1
    status = 'P'
    try:
        home_participant = driver.find_element(By.CLASS_NAME, 'duelParticipant__home.duelParticipant--winner').text
        home_result = 1
        away_result = 0
        status = 'R'
    except:
        home_participant = driver.find_element(By.CLASS_NAME, 'duelParticipant__home').text
    try:    
        away_participant = driver.find_element(By.CLASS_NAME, 'duelParticipant__away.duelParticipant--winner').text
        home_result = 0
        away_result = 1
        status = 'R'
    except:
        away_participant = driver.find_element(By.CLASS_NAME, 'duelParticipant__away').text
    match_id = random_id()
    result_dict = {'match_id':match_id,'name':home_participant + '-' + away_participant,\
                   'home':home_participant,'visitor':away_participant,\
                   'home_result':home_result,  'visitor_result':away_result,\
                   'status':status, 'place':''
                  }
    return result_dict

def extract_info_boxing(driver, league_info):
    dict_stadium = {'stadium_id':'BOXING97943','country':'',\
             'capacity':0,'desc_i18n':'', 'name':'', 'photo':''}
    if check_stadium('BOXING97943'):
        print("BOXING stadium created")
    else:
        save_stadium(dict_stadium)

    wait_update_page(driver, league_info['url'], "container__heading")    

    # EXTRACT ALL MATCH BLOCKS
    list_match  = driver.find_elements(By.XPATH, '//div[@title="Click for match detail!"]')
    dict_matchs_link = {}
    # for event_block in event_blocks:
    for key, match in enumerate(list_match):
        
        dict_matchs_link[key]= get_match_link(driver, match)# INSIDE MATCH GET COMPLETE INFO

    for key, match in dict_matchs_link.items():

        wait_load_details(driver, match['url'])
        # event_info = get_match_info(driver, event_info)
        event_info = get_result_boxig(driver) # match_id, home_participant, away_participant, name, home_result, away_result, status
        event_info['stadium_id'] = dict_stadium['stadium_id']
        event_info['match_country'] = ''  # MATCH COUNTRY CHECK IF IS AVAILABLE.
        print_section("TEST GET MATCH INFO")
        print("Event info Boxing: ", event_info)
        
        event_info['statistic'] = get_statistics_game(driver)
        event_info['league_id'] = league_info['league_id']            
        
        event_info['match_date'] = driver.find_element(By.CLASS_NAME, 'duelParticipant__startTime').text
        event_info['match_date'], event_info['start_time'] = get_time_date_format(event_info['match_date'], section ='results') 
        event_info['end_time'] = event_info['start_time']            

        # print("event_info: ", event_info)
        home_links, away_links = get_links_participants(driver)
        print('home_links, away_links')
        print(home_links, away_links)
        # save_players_info
        team_id_home = save_team_player_single(driver, home_links[0], league_info)# Pending pass sport_id
        team_id_away =  save_team_player_single(driver, away_links[0], league_info)# Pending pass sport_id

        # save match score entity
        match_detail_id = random_id()
        score_id = random_id()
        dict_home = {'match_detail_id':match_detail_id, 'home':False, 'visitor':False, 'match_id':event_info['match_id'],\
                    'team_id':team_id_home, 'points':event_info['home_result'], 'score_id':score_id}        
        match_detail_id = random_id()
        score_id = random_id()
        dict_visitor = {'match_detail_id':match_detail_id, 'home':False, 'visitor':False, 'match_id':event_info['match_id'],\
                    'team_id':team_id_away, 'points':event_info['visitor_result'], 'score_id':score_id}
        
        ################# COMPLETE DATE ######################
        event_info['season_id'] = league_info['season_id']
        event_info['tournament_id'] = ''
        event_info['rounds'] = ''
        print("Event info:")
        print(event_info)
        print("dict_home: ", dict_home)         
        save_math_info(event_info)
        save_details_math_info(dict_home)
        save_details_math_info(dict_visitor)
        save_score_info(dict_home)
        save_score_info(dict_visitor)

def get_first_date_with_year(text):
    # Regular expression pattern to find the date in the specified format
    date_pattern = r'(\d{2}\.\d{2})\.-(\d{2}\.\d{2})\.(\d{4})'
    
    # Search for matches of the regular expression pattern in the text
    match = re.search(date_pattern, text)   

    if match:
        # Extract the found dates
        first_date_str, second_date_str, year = match.groups()
        
        # Split the date range
        first_date_parts = first_date_str.split('.')
        second_date_parts = second_date_str.split('.')
        
        # Take only the first date from the range and add the year
        first_date = f"{first_date_parts[0]}.{first_date_parts[1]}.{year}"
        
        # Convert the date string into a datetime object
        dt_object = datetime.strptime(first_date, '%d.%m.%Y')
        
        # Extract date and time
        date = dt_object.date()
        time = dt_object.time()
        
        return date, time
    else:
        return None, None

def get_tournament(driver, league_info, event_block):

    dict_match = {}
    # STATISTIC 
    statistic_dict = {}
    valores = event_block.find_element(By.CLASS_NAME, 'event__header--info').text.split('\n')
    
    for valor in valores:
        clave, valor = valor.split(': ')
        statistic_dict[clave] = valor

    print("statistic_dict")
    print(statistic_dict)
    # EXTRACT DATE_TIME
    date_time = event_block.find_element(By.XPATH, './/span[@data-testid="wcl-simpleText1"]').text
    print('#'*100)
    print(date_time)
    if 'Finished' in date_time:
        dict_match['match_date'], dict_match['start_time'] = get_first_date_with_year(statistic_dict['Dates'])
        dict_match['status'] = 'R'
    else:
        dict_match['match_date'], dict_match['start_time'] = get_time_date_format(date_time, section ='results')
        dict_match['status'] = 'P'    
    
    dict_match['match_id'] = random_id()
    dict_match['match_country'] = ''
    
    dict_match['end_time'] = dict_match['start_time']
    dict_match['name'] = event_block.find_element(By.CLASS_NAME, 'event__title').text
    dict_match['place'] = '*'
    
    dict_match['rounds'] = dict_match['name']
    dict_match['season_id'] = league_info['season_id']      
    dict_match['statistic'] = str(statistic_dict)
    dict_match['league_id'] = league_info['league_id']  
    dict_match['stadium_id'] = ''
    return dict_match

def buil_dict_map_values_golf(driver):
    block = driver.find_element(By.CLASS_NAME, 'event__match.event__main.event__match--noDuel')    
    cell_names = block.find_elements(By.XPATH,'.//div')
    dict_map_cell = {}
    for index, cell_name in enumerate(cell_names):
        cell_name = cell_name.get_attribute('title').replace(' ', '_')    
        dict_map_cell[index] = cell_name
    return dict_map_cell 

def get_player_result(player_block, dict_map_cell):
    dict_player = {}
    cell_values = player_block.find_elements(By.XPATH, './/div')    
    for index, cell_value in enumerate(cell_values):
        dict_player[dict_map_cell[index]] = cell_value.text
    return dict_player

def get_player_url(player_block):
    html_block = player_block.get_attribute('outerHTML')    
    link_id = re.findall(r'id="[a-z]\_\d+\_(.+?)"', html_block)[0]
    url_details = "https://www.flashscore.com/match/{}/p/#/match-summary".format(link_id)
    return url_details

def get_dict_players(event_block):

    dict_map_cell = buil_dict_map_values_golf(event_block)
    players = event_block.find_elements(By.XPATH, '//div[@title="Click for player card!"]')
    print(len(players))
    dict_players = {}
    
    for index, player_block in enumerate(players):
        print(index, end = '-')
        dict_players[index] = {'statistic': get_player_result(player_block, dict_map_cell), 'player_url' : get_player_url(player_block)} 
    return dict_players
