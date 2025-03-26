from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import psycopg2
import shutil
from data_base import *
from common_functions import *
from milestone4 import wait_load_details, get_match_info, get_statistics_game
from milestone8 import give_click_on_live
from milestone4 import get_time_date_format

def check_if_title(row):
    try:
        row.find_element(By.CSS_SELECTOR, '[class="event__title"]')
        return True
    except:
        return False
    
def check_if_pin(row):
    try:
        row.find_element(By.CSS_SELECTOR, '[data-testid="wcl-pin-active"]')
        return True
    except:
        return False
    
def check_if_match(row):
    try:
        row.find_element(By.CSS_SELECTOR, '[title="Click for match detail!"]')
        return True
    except:
        return False

def find_rows(driver):
    # block_leagues = driver.find_element(By.CLASS_NAME, 'leagues--live')
    block_leagues = driver.find_element(By.CLASS_NAME, "sportName.soccer")
    return block_leagues.find_elements(By.XPATH, "./div")

def extract_country_league_name(driver, row):
    league_box = row.find_element(By.CLASS_NAME, "event__titleBox")
    country = league_box.find_element(By.XPATH, 'span').text    
    league_name = league_box.find_element(By.XPATH, 'a').text
    if '-' in league_name:                                            # DELETE LINE
        league_name = league_name.split(' -')[0]#.replace(' ', '')    # DELETE LINE
    return country, league_name

def get_league_info_json(leagues_info, country, league_name, sport):
    country, league_name, sport    
    return leagues_info[sport][f'{country}_{league_name}']


def get_complementary_info(json_dict_league_info, season_info):
    # LOAD COUNTRY ID AND LEAGUE ID    
    season_info['country_id'] = json_dict_league_info['country_id']
    season_info['league_id'] = json_dict_league_info['league_id']
    season_info['season_id'] = json_dict_league_info['season_id']
    return season_info

################# continuacion extrac match
def extract_match_info(driver, row, section = 'results'):
    print("################ INSIDE GET RESULT ################")
    print("Row: ", row.text)
    home_xpath_expression = ".//div[contains(@class, 'homeParticipant')]"
    away_xpath_expression = ".//div[contains(@class, 'awayParticipant')]"
    
    match_date = datetime.utcnow().date()
    try:
        start_time = row.find_element(By.CLASS_NAME, 'event__time').text
        start_time = datetime.strptime(start_time, "%H:%M").time()
    except:        
        fecha_hora = datetime.now()
        start_time = fecha_hora.time()
        end_time = start_time
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
    match_id = generate_uuid()
    result_dict = {'match_id':match_id,'match_date':match_date,'start_time':start_time, 'end_time':end_time,\
                    'name':home_participant + '-' + away_participant,'home':home_participant,'visitor':away_participant,\
                    'home_result':home_result,  'visitor_result':away_result, 'link_details':url_details,'place':'',
                    'country_id':''}    
    return result_dict

def get_match_info_v2(driver, event_info):
    # Extract details about matchs
    match_country = driver.find_element(By.XPATH, '//span[@class="tournamentHeader__country"]').text.split(":")[0]
    event_info['match_country'] = match_country 
    match_info_elements = driver.find_elements(By.XPATH, '//div[@class="matchInfoData"]/div')
    print("match_info_elements len", len(match_info_elements))

    # GET MATCH DATE COMPLETE.
    event_info['match_date'] = driver.find_element(By.CLASS_NAME, 'duelParticipant__startTime').text
    event_info['match_date'], event_info['start_time'] = get_time_date_format(event_info['match_date'], section ='results') 
    print("Match info len: ", len(match_info_elements))
    for element in match_info_elements:
        print(element.text)
        field_name = element.find_element(By.CLASS_NAME, 'matchInfoItem__name').text.replace(':','')
        field_value = element.find_element(By.CLASS_NAME, 'matchInfoItem__value').text
        event_info[field_name] = field_value
    return event_info

def complete_match_info(driver, match_dict):
    # LOAD MATCH URL AND WAIT ALL ELEMENTS
    wait_load_details(driver, match_dict['link_details'])
    # GET ADDITIONAL INFORMAION INSIDE LINK MATCH
    match_dict = get_match_info_v2(driver, match_dict)
    # GET STATISTIC INFO FROM MATCH
    match_dict['statistic'] = get_statistics_game(driver)
    return match_dict

def get_stadium_info(driver, country_id):
    stadium_info = driver.find_elements(By.XPATH, '//*[contains(@class, "summaryMatchInformation")]/div')
    dict_stadium = {stadium_info[n].text.strip(): stadium_info[n + 1].text.replace('\n', ' ').strip()
        for n in range(0, len(stadium_info) - 1, 2)}

    if 'CAPACITY' in dict_stadium.keys():
        capacity = int(''.join(dict_stadium['CAPACITY'].split()))
    else:
        capacity = 0

    if 'VENUE' in list(dict_stadium.keys()):
        name_stadium = dict_stadium['VENUE']
    else:
        name_stadium = ''

    dict_stadium = {'stadium_id':generate_uuid(),'country':country_id,\
                    'capacity':capacity,'desc_i18n':'', 'name':name_stadium, 'photo':''}
    return dict_stadium

def build_stadium_dict(driver, season_info, match_dict):
    home_name = match_dict['home']
    visitor_name = match_dict['visitor']

    try:
        stadium_id = season_info[home_name]['stadium_id']
        return False, {'stadium_id':stadium_id}
    except:
        # EXTRACT INFO FROM MATCH LINK AND CREATE DICT USED TO SAVE IN DATA BASE
        stadium_dict = get_stadium_info(driver, season_info['country_id'])
        return True, stadium_dict
    
def generate_dict_details(season_info, match_dict):
    #########################################################################################################
    #   season_info, for each team using the team name like key contains team_id, team_url, stadium_id      #
    #   match_dict contains info related to current match                                                   #
    #                                                                                                       #
    #########################################################################################################
    match_detail_id = generate_uuid()
    team_id_home = season_info[match_dict['home']]['team_id']
    team_id_visitor = season_info[match_dict['visitor']]['team_id']
    match_id = match_dict['match_id']
    score_id = generate_uuid()
    dict_home = {'match_detail_id':match_detail_id, 'home':True, 'visitor':False, 'match_id':match_id,\
                'team_id':team_id_home, 'points':match_dict['home_result'], 'score_id':score_id}
    match_detail_id = generate_uuid()
    score_id = generate_uuid()
    dict_visitor = {'match_detail_id':match_detail_id, 'home':False, 'visitor':True, 'match_id':match_id,\
                'team_id':team_id_visitor, 'points':match_dict['visitor_result'], 'score_id':score_id}
    return dict_home, dict_visitor

def complete_dict_match(match_dict, stadium_dict, season_info):
    match_dict['stadium_id'] = stadium_dict['stadium_id']
    match_dict['place'] = ''
    match_dict['league_id'] = season_info['league_id']
    match_dict['tournament_id'] = ''
    match_dict['rounds'] = ''
    match_dict['status'] = 'schedule'
    match_dict['season_id'] = season_info['season_id']
    return match_dict

def extract_matchs_from_schedule():
    driver = launch_navigator('https://www.flashscore.com', headless = False)
    login(driver, email_= "jignacio@jweglobal.com", password_ = "Caracas5050@\n")
    sport_name = 'FOOTBALL'

    # LOAD SPORTS LIST OF URLS
    dict_sports_url = load_json('check_points/sports_url_m2.json')

    # LOAD LEAGUES INFO RELATED
    leagues_info = load_json('check_points/leagues_info.json')

    # LOAD SPORT LINK
    # wait_update_page(driver, dict_sports_url[sport_name], "container__heading")

    # GIVE CLICK IN SECTION LIVE
    # live_games_found = give_click_on_live(driver, sport_name, section = "Schedule")

    # LOOP IN LIST OF SPORTS
    match_flag = False
    sub_blocks = find_rows(driver)
    for index, row in enumerate(sub_blocks):
        title_flag = check_if_title(row)    
        
        if title_flag:        
            if check_if_pin(row):
                print("Index: ", index, row.text.replace('\n', ' '))            
                country, league_name = extract_country_league_name(driver, row)
                # FROM LEAGUES_INFO.JSON ONLY LOAD DICT WITH LEAGUE INFO
                json_dict_league_info = get_league_info_json(leagues_info, country, league_name, sport_name)
                
                # CHECK IF PATH EXIST
                path_season = f"check_points/leagues_season/{sport_name}/{country}_{league_name}.json"
                print(path_season)
                if os.path.exists(path_season):
                    print('FILE FOUND')
                    # LOAD INFO RELATED TO SEASON INFO (TEAMS, TEAMS_ID, STADIUM_ID)            
                    season_info = load_json(path_season)                
                    # COMPLETE INFO SEASON INFO WITH LEAGUE INFO
                    season_info = get_complementary_info(json_dict_league_info, season_info)
                    # ENABLE FLAG TO ALLOW CHECKING MATCHES
                    match_flag = True
                else:
                    match_flag = False
                
            else:
                match_flag = False
        # CHECK IF MATCH ACTIVATE AND CONFIRM IF CONTAIN (Click for match detail!)
        if match_flag and check_if_match(row):        
            # EXTACT MATCH INFO
            match_dict = extract_match_info(driver, row, section = 'live')
            print_section("MATCH DICT INFO")
            print(match_dict)

            # CHECK IF MATCH WAS PREVIUSLY CREATED
            duplicate = check_match_duplicate2(season_info['league_id'], match_dict['name'])
            if not duplicate:
                print('CREATE MATCH')
                match_dict = complete_match_info(driver, match_dict)
                # CHECK IF STADIUM WAS SAVED PREVIUSLY IN CONTRARY CASE CREATE STADIUM DICT
                create_stadium_flag, stadium_info_or_id = build_stadium_dict(driver, season_info, match_dict)
                # CHECK FLAG STADIUM AND SAVE IN DATA BASE
                if create_stadium_flag:
                    save_stadium(stadium_info_or_id)
                # CREATE DICT OF MATCH DETAILS
                dict_home, dict_visitor = generate_dict_details(season_info, match_dict)
                # COMPLETE FIELDS IN MATCH DICT
                match_dict = complete_dict_match(match_dict, stadium_info_or_id, season_info)
                # SAVE ALL IN DATA BASE
                save_math_info(match_dict)
                save_details_math_info(dict_home)
                save_details_math_info(dict_visitor)
                save_score_info(dict_home)
                save_score_info(dict_visitor)
    #     stop_validate()

if __name__ == "__main__":	
	extract_matchs_from_schedule()