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

def get_sports_links(driver):
    wait = WebDriverWait(driver, 10)
    buttonmore = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'menuMinority__arrow')))

    mainsports = driver.find_elements(By.XPATH, '//div[@class="menuTop__items"]/a')

    dict_links = {}

    for link in mainsports:
        sport_name = '_'.join(link.text.split())
        sport_url = link.get_attribute('href')
        dict_links[sport_name] = sport_url

    buttonmore.click()

    list_links = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'menuMinority__item')))

    list_links = driver.find_elements(By.CLASS_NAME, 'menuMinority__item')

    for link in list_links:
        sport_name = '_'.join(link.text.split())
        sport_url = link.get_attribute('href')
        if sport_name == '':
            sport_name = sport_url.split('/')[-2].upper()
        dict_links[sport_name] = sport_url
        
    buttonminus = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'menuMinority__arrow')))
    buttonminus.click()
    
    return dict_links

def create_sport_dict(sport_mode, sport_name):
    sport_id = random_id_text(sport_name)
    sport_dict = {'sport_id' : sport_id, 'is_active' : True, 'desc_i18n' : '', 'logo' : '',\
    'sport_mode' : sport_mode, 'name_i18n' : '', 'point_name': '', 'name':sport_name}
    return sport_dict, sport_id

def click_news(driver):
    wait = WebDriverWait(driver, 10)
    newsbutton = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'tabs__tab.news')))  # "tabs__tab news selected"
    newsbutton.click()

def check_pin(driver):
    pin = driver.find_element(By.ID, "toMyLeagues")
    if 'pinMyLeague active 'in pin.get_attribute('outerHTML'):
        return True
    else:
        return False

def get_league_data(driver, league_team, sport_name):
    dict_sport_id = get_dict_sport_id()
    sport_id = dict_sport_id[sport_name]
    block_ligue_team = driver.find_element(By.CLASS_NAME, 'container__heading')
    sport = block_ligue_team.find_element(By.XPATH, './/h2[@class= "breadcrumb"]/a[1]').text
    league_country = block_ligue_team.find_element(By.XPATH, './/h2[@class= "breadcrumb"]/a[2]').text
    league_name = block_ligue_team.find_element(By.CLASS_NAME,'heading__title').text
    season_name = block_ligue_team.find_element(By.CLASS_NAME, 'heading__info').text
    image_url = block_ligue_team.find_element(By.XPATH, './/div[@class= "heading"]/img').get_attribute('src')
    image_path = random_name_logos(league_team, folder = 'images/logos/')
    # save_image(driver, image_url, image_path)

    # image_path = image_path.replace('images/logos/','')
    league_id = random_id_text(sport_name + league_team)
    season_id = generate_uuid() 
    ligue_tornamen = {"sport_id":sport_id,"league_id":league_id,"season_id":season_id, 'sport':sport, 'league_country': league_country,
                     'league_name': league_name,'season_name':season_name, 'league_logo':image_path,
                      'league_name_i18n':'', 'season_end':datetime.now(), 'season_start':datetime.now(),
                      'image_url':image_url, 'image_path':image_path}
    return ligue_tornamen

def get_league_data_boxing(driver, league_team, sport_name):
    print(f"league_team:{league_team}, sport_name: {sport_name}")
    dict_sport_id = get_dict_sport_id()
    sport_id = dict_sport_id[sport_name]
    block_ligue_team = driver.find_element(By.CLASS_NAME, 'container__heading')
    sport = block_ligue_team.find_element(By.XPATH, './/h2[@class= "breadcrumb"]/a[1]').text
    # league_country = block_ligue_team.find_element(By.XPATH, './/h2[@class= "breadcrumb"]/a[2]').text
    league_name = block_ligue_team.find_element(By.CLASS_NAME,'heading__title').text
    season_name = block_ligue_team.find_element(By.CLASS_NAME, 'heading__info').text
    image_url = block_ligue_team.find_element(By.XPATH, './/div[@class= "heading"]/img').get_attribute('src')
    image_path = random_name_logos(league_team, folder = 'images/logos/')
    # save_image(driver, image_url, image_path)
    # image_path = image_path.replace('images/logos/','')
    league_id = random_id_text(sport_name + league_team)
    season_id = generate_uuid() 
    ligue_tornamen = {"sport_id":sport_id,"league_id":league_id,"season_id":season_id, 'sport':sport, 'league_country': '',
                     'league_name': league_name,'season_name':season_name, 'league_logo':image_path.replace('images/logos/',''),
                      'league_name_i18n':'', 'season_end':datetime.now(), 'season_start':datetime.now(),"image_url":image_url,
                      'image_path':image_path}
    return ligue_tornamen

def get_teams_data(driver, sport_id, league_id, season_id, team_info):
    block_ligue_team = driver.find_element(By.CLASS_NAME, 'container__heading')


    sport = block_ligue_team.find_element(By.XPATH, './/h2[@class= "breadcrumb"]/a[1]').text
    team_country = block_ligue_team.find_element(By.XPATH, './/h2[@class= "breadcrumb"]/a[2]').text
    team_name = block_ligue_team.find_element(By.CLASS_NAME,'heading__title').text


    stadium = block_ligue_team.find_element(By.CLASS_NAME, 'heading__info').text
    image_url = block_ligue_team.find_element(By.XPATH, './/div[@class= "heading"]/img').get_attribute('src')
    image_path = random_name(folder = 'images/logos/')
    save_image(driver, image_url, image_path)
    logo_path = image_path.replace('images/logos/','')
    team_id = random_id_text(sport_name + team_name)
    instance_id = generate_uuid()   
    meta_dict = str({'statistics':team_info['statistics'], 'last_results':team_info['last_results']})
    team_info = {"team_id":team_id,"team_position":team_info['position'], "team_country":team_country,"team_desc":'', 'team_logo':logo_path,\
             'team_name': team_name,'sport_id': sport_id, 'league_id':league_id, 'season_id':season_id,\
             'instance_id':instance_id, 'team_meta':meta_dict, 'stadium':stadium}
    return team_info

def find_ligues_torneos(driver):
    wait = WebDriverWait(driver, 5)
    xpath_expression = '//div[@id="my-leagues-list"]'
    leagues_info = wait.until(EC.visibility_of_element_located((By.XPATH, xpath_expression)))
    dict_liguies = {}
    if not "To select your leagues " in leagues_info.text:
        # ligues = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@id="my-leagues-list"]/div/div/a')))        
        leagues = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@id="my-leagues-list"]/div/div/a')))     
        # ligues = driver.find_elements(By.XPATH, '//div[@id="my-leagues-list"]/div/div/a')
        # print(len(ligues))
        gender = ''
        for league in leagues:
            if '#man' in league.get_attribute('outerHTML'):
                gender = "_man"
            if '#woman' in league.get_attribute('outerHTML'):
                gender = "_woman"
            # dict_liguies['_'.join(ligue.text.split())+gender] = ligue.get_attribute('href')
            league_url = league.get_attribute('href')
            dict_liguies[('_'.join(league_url.split('/')[-3:-1])+gender).upper()] = league_url
    return dict_liguies

def find_categories(driver):
    wait = WebDriverWait(driver, 5)
    xpath_expression = '//div[@id="my-leagues-list"]'
    leagues_info = wait.until(EC.visibility_of_element_located((By.XPATH, xpath_expression)))
    dict_liguies = {}
    if not "To select your leagues " in leagues_info.text:
        # ligues = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@id="my-leagues-list"]/div/div/a')))        
        leagues = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@id="my-leagues-list"]/div/div/a')))     
        # ligues = driver.find_elements(By.XPATH, '//div[@id="my-leagues-list"]/div/div/a')
        # print(len(ligues))
        gender = ''
        for league in leagues:
            print("League name: ")
            print(league.text)
            if '#man' in league.get_attribute('outerHTML'):
                gender = "_man"
            if '#woman' in league.get_attribute('outerHTML'):
                gender = "_woman"
            # dict_liguies['_'.join(ligue.text.split())+gender] = ligue.get_attribute('href')
            league_url = league.get_attribute('href')
            dict_liguies[('_'.join(league_url.split('/')[-3:-1])+gender).upper()] = league_url
    return dict_liguies

def get_result_basketball(row):
    date = row.find_element(By.CLASS_NAME, 'event__time').text
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
    print('#'*50)
    print(html_block, '\n')
    print("New regular expression: ")
    link_id = re.findall(r'id="[a-z]_\d_(.+?)\"', html_block)[0]
    url_details = "https://www.flashscore.com/match/{}/#/match-summary/match-summary".format(link_id)
    result_dict = {'date':date, 'home_participant':home_participant,'away_participant':away_participant,\
                   'home_result':home_result,  'away_result':away_result, 'link_details':url_details}
    print(result_dict, '\n')
    return result_dict

def extract_info_results__(driver):
#     xpath_expression = '//div[@class="sportName {}"]/div'.format(sport)
    xpath_expression = '//div[@class="leagues--static event--leagues results"]/div/div'
    results_block = driver.find_elements(By.XPATH, xpath_expression)

    dict_rounds = {}
    count_sub_section = 0
    count_section = 0
    for i, row in enumerate(results_block): 
        print(row.get_attribute('outerHTML'))

        try:
            # Get seruls block
            result = get_result(row)
            dict_rounds[current_id_section][event_number] = result
            event_number += 1
        except:
            try:
                # Get Rounds block              
                try:
                    # Only get section name or ROUND name
                    id_section_new = row.find_element(By.CLASS_NAME, 'event__title--name').text.replace(' ','_')
                    #id_section = row.find_element(By.CLASS_NAME, 'event__round event__round--static').text.replace(' ','_')
                except:
                    # Else get all available text
                    id_section_new = row.text
                    id_section_new = get_unique_key(id_section_new, dict_rounds.keys())
                if count_sub_section != 0:
                    # save current dict
                    # stop_validate()
                    file_name = 'check_points/events/{}/round_{}.json'.format(section_name, current_id_section)
                    save_check_point(file_name, dict_rounds[current_id_section])
                count_sub_section += 1
                dict_rounds[id_section_new] = {}
                event_number = 0
                current_id_section = id_section_new
            except:             
                # Get name complete section.
                print("Get name complete section: ")                
                section_name = row.find_element(By.CLASS_NAME, 'icon--flag.event__title.fl_22')
                print("section_name: ", section_name)
                section_name = section_name.replace(' ', '_')
                print("section_name: ", section_name)
                os.mkdir("check_points/events/{}".format(section_name))
        print("#"*40, '\n')
        
    return dict_rounds

#####################################################################
#                   SQUAD INFO EXTRACTION                           #
#####################################################################
def get_all_player_info(driver):
    player_block = driver.find_element(By.CLASS_NAME, 'playerHeader__wrapper')
    lines = player_block.find_elements(By.XPATH, './/span')
    dict_info = {}
    value = ''
    count = 0
    for line in lines:
        HTML = line.get_attribute('outerHTML')
        if 'info-bold' in HTML:
            if count != 0:
                dict_info[tag] = value
                value = ''
            tag = line.text.replace(' ','_').replace(':','').lower()
            count += 1
        else:        
            value = value + ' ' + line.text
    dict_info[tag] = value        
    return dict_info

def get_player_data(driver):
    dict_player_full_info = get_all_player_info(driver)

    profile_block = driver.find_element(By.ID, 'player-profile-heading')
    player_country = profile_block.find_element(By.XPATH, './/div/h2/span[2]').text
    if 'age' in dict_player_full_info.keys():
        date_str = dict_player_full_info['age'].split()[1].replace('(','').replace(')','')
        player_dob = datetime.strptime(date_str, "%d.%m.%Y")
    else:
        player_dob = datetime.strptime('01.01.1900', "%d.%m.%Y") 

    player_name = profile_block.find_element(By.CLASS_NAME, 'typo-participant-heading').text        
    
    image_url = profile_block.find_element(By.XPATH, './/div/div/div/img').get_attribute('src')
    image_path = random_name(folder = 'images/players/')
    save_image(driver, image_url, image_path)
    player_photo = image_path.replace('images/players/','')

    player_position = profile_block.find_element(By.CLASS_NAME, 'typo-participant-info-bold').text
    player_id = generate_uuid()
    player_dict = {'player_id':player_id, 'player_country':player_country, 'player_dob':player_dob, 'player_name':player_name,\
     'player_photo':player_photo, 'player_position':player_position}
    return player_dict

def get_sections_links(driver):
    list_links = driver.find_elements(By.XPATH, '//div[@class="tabs__group"]/a')

    dict_links = {}
    for link in list_links[1:]:    
        url_termination = link.get_attribute('href')
        dict_links[url_termination.split('/')[-2]] = url_termination
    return dict_links
#####################################################################

################################ MOTOR SPORT SECTION #########################################################
def find_categories_motor_sport(driver, list_enables):    
    driver.execute_script("document.body.style.zoom='50%'")
    wait = WebDriverWait(driver, 10)
    categories_block = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "lmc__menu")))

    calendar = driver.find_element(By.CLASS_NAME, 'leftMenu.menu.leftMenu--seasonCalendar')
    calendar_f1_link = calendar.find_element(By.XPATH, '..//div[@class="leftMenu__item"]/a').get_attribute('href')
    
    list_categories = categories_block.find_elements(By.CLASS_NAME, 'lmc__block ')
    dict_categories_info = {}
    for category_block in list_categories:
        category_name = category_block.find_element(By.XPATH, './/span[@class="lmc__elementName"]').text    
        if category_name.upper() in list_enables:
            link = category_block.find_element(By.XPATH, './/a').get_attribute('href')
    #         wait2 = WebDriverWait(category_block, 10)
    #         # expand = category_block.find_element(By.CLASS_NAME, 'lmc__element.lmc__item ')
    #         expand = wait2.until(EC.element_to_be_clickable((By.CLASS_NAME, 'lmc__element.lmc__item ')))
    #         expand.click()
    #         wait2 = wait = WebDriverWait(category_block, 10)
    #         standing_link = wait2.until(EC.element_to_be_clickable((By.CLASS_NAME, "lmc__template.lmc__templateRank")))
            # dict_categories_info[category_name.upper()] = {'url':link, 
            # 'standing_link':standing_link.get_attribute('href')}            
            dict_categories_info[category_name.upper()] = {'url':link, 
            'standing_link':'https://www.flashscore.com/motorsport/championship-standings/f1/'}            
    # dict_categories_info['FORMULA 1']['calendar_link'] = calendar_f1_link
    dict_categories_info['FORMULA 1']['calendar_link'] = 'https://www.flashscore.com/motorsport/calendar/f1/'
    return dict_categories_info

def get_racer_info(driver):
    profile_block = driver.find_element(By.CLASS_NAME, 'container__heading')
    lines = profile_block.find_elements(By.XPATH, './/div[@class="heading__info"]/div')    

    dict_info = {}
    value = ''
    for line in lines:
      if ':' in line.text:
        key, value= line.text.split(':')
        dict_info[key.lower()] = value
    dict_info['standings'] = dict_info['standings'].replace('.','').replace(' ','')
    player_country = profile_block.find_element(By.XPATH, './/span[@class="breadcrumb__text"]').text

    print("Player keys info: ")
    print(dict_info)
    if 'age' in dict_info.keys():        
        birth_date = re.findall(r'\d+\.\d+\.\d+', dict_info['age'])
        if len(birth_date)!= 0:
            date_str = birth_date[0]
            player_dob = datetime.strptime(date_str, "%d.%m.%Y")        
    else:
        player_dob = datetime.strptime('01.01.1900', "%d.%m.%Y")        

    player_name = profile_block.find_element(By.CLASS_NAME, 'heading__name').text

    image_url = profile_block.find_element(By.XPATH, './/div/img').get_attribute('src')
    # image_path = random_name(folder = 'images/players/')
    image_path = random_name_logos(player_name, folder = 'images/players/')
    save_image(driver, image_url, image_path)
    player_photo = image_path.replace('images/players/','')
    player_id = random_id_text(player_name + player_country)
    player_dict = {'player_id':player_id, 'player_country':player_country, 'player_dob':player_dob, 'player_name':player_name,\
     'player_photo':player_photo, 'player_position':dict_info['standings'], 'player_meta': ''}
        
    return player_dict

def create_league(driver, category_info):
    dict_league = {'league_id':random_id_text("MOTOR SPORT" + category_info['league_name']), 'league_logo':'',
                    'league_country':'',
                   'league_name':category_info['league_name'],'league_name_i18n':'',
                   'sport_id':random_id_text('MOTOR SPORT'), 'league_name':category_info['league_name']}

    if  not check_league_duplicate(dict_league['league_id']):
        save_league_info(dict_league)
    return dict_league

def create_season(driver, dict_league):
    season_text = driver.find_element(By.CLASS_NAME, 'rankingTable__league.rankingTable__mainRow').text
    season_year = re.findall(r'\d+\.\d+\.(\d+)', season_text)[0]
    season_dict = {'season_id' : random_id_text(dict_league['league_name'] + season_year), 'season_name':season_year,
                 'season_end':datetime.now().date(),'season_start':datetime.now().date(),
                  'league_id': dict_league['league_id']}    
    return season_dict

def create_drivers_teams(driver, dict_categories):
    
    for category, category_info in dict_categories.items():
        category_info['league_name'] = category
        wait_update_page(driver, category_info['standing_link'], "container__heading")
        
        dict_league = create_league(driver, category_info) # Create league save in db.       
        season_dict = create_season(driver, dict_league)

        if not check_season_duplicate(season_dict['season_id']):
            save_season_database(season_dict)
        racers_table = driver.find_element(By.CLASS_NAME, 'rankingTable__table')
        # BLOC FOR EXTRACT LINKS AND RACERS INFO.
        list_racers = driver.find_elements(By.XPATH, '//div[@class="rankingTable__table"]/div[@class="rankingTable__row"]')
        dict_racers = {}
        for racer in list_racers:    
            position, name, team, points = racer.find_elements(By.XPATH, './div')
            link = name.find_element(By.XPATH, './div/div/a').get_attribute('href')
            name = name.find_element(By.XPATH, './div/div/a').text
            position = position.text.replace('.','').replace(' ','')
            points.text
            dict_racers[position] = {'name': name, 'team_name': team.text, 'points': points.text,
                                     'link':link,'team_country':'',  'team_desc':'', 'team_logo':'',
                                     'player_meta' : '','team_meta':'', 'team_position': 0
                                    }
            
        for position, racer in dict_racers.items():            
            wait_update_page(driver, racer['link'], "container__heading")
            dict_racer = get_racer_info(driver)
            dict_racer['team_name'] = racer['team_name']
            dict_racer['name'] = racer['name']
            dict_racer['sport_name'] = category
            save_racer_team(dict_racer, season_dict['season_id'])# save each racer in data base.            
#####################################################################
#                   MOTOR SPORT PLAYER INFO EXTRACTION              #
#####################################################################

def get_racer_info(driver):
    profile_block = driver.find_element(By.CLASS_NAME, 'container__heading')
    lines = profile_block.find_elements(By.XPATH, './/div[@class="heading__info"]/div')

    dict_info = {}
    value = ''
    for line in lines:
      if ':' in line.text:
        key, value= line.text.split(':')
        dict_info[key.lower()] = value
    dict_info['standings'] = dict_info['standings'].replace('.','').replace(' ','')
    player_country = profile_block.find_element(By.XPATH, './/span[@class="breadcrumb__text"]').text

    print("Player keys info: ")
    print(dict_info)
    if 'age' in dict_info.keys():        
        birth_date = re.findall(r'\d+\.\d+\.\d+', dict_info['age'])
        if len(birth_date)!= 0:
            date_str = birth_date[0]
            player_dob = datetime.strptime(date_str, "%d.%m.%Y")        
    else:
        player_dob = datetime.strptime('01.01.1900', "%d.%m.%Y")        

    player_name = profile_block.find_element(By.CLASS_NAME, 'heading__name').text

    image_url = profile_block.find_element(By.XPATH, './/div/img').get_attribute('src')
    # image_path = random_name(folder = 'images/players/')
    image_path = random_name_logos(player_name, folder = 'images/players/')
    save_image(driver, image_url, image_path)
    player_photo = image_path.replace('images/players/','')
    player_id = generate_uuid()
    player_dict = {'player_id':player_id, 'player_country':player_country, 'player_dob':player_dob, 'player_name':player_name,\
     'player_photo':player_photo, 'player_position':dict_info['standings'], 'player_meta': ''}
        
    return player_dict

def save_racer_team(dict_racer, season_id):
    dict_racer['team_id'] = random_id_text("MOTOR SPORT" + dict_racer['team_name']+ dict_racer['name'])
    dict_racer['season_id'] = season_id
    dict_racer['sport_id'] = random_id_text("MOTOR SPORT")
    dict_racer['instance_id'] = generate_uuid()    
    dict_racer['league_id'] = random_id_text("MOTOR SPORT" + dict_racer['sport_name'])
    dict_racer['team_country'] = dict_racer['player_country']
    dict_racer['team_desc'] = dict_racer['team_name']
    dict_racer['team_name'] = dict_racer['name']
    dict_racer['team_logo'] = dict_racer['player_photo']
    dict_racer['team_meta'] = ''
    dict_racer['team_position'] = 0
    
    # CHECK IF PLAYER WAS CREATED PREVIOUSLY
    # player_id_list = check_player_duplicates(dict_racer['player_country'], dict_racer['player_name'], dict_racer['player_dob'])
    player_id_duplicate = check_player_duplicates_id(dict_racer['player_id'])
    
    print_section(dict_racer['name'])

    print("Result player duplicate: ", player_id_duplicate)
    if not player_id_duplicate:
        save_player_info(dict_racer) # player
    else:
        print('Player created previously')

    # CHECK IF TEAM WAS CREATED
    team_id_list = check_team_duplicates_id(dict_racer['team_id'])
    print("team_id_list: ", team_id_list)
    if not team_id_list:
        save_team_info(dict_racer) # team
        save_team_players_entity(dict_racer) # team_players_entity     
    else:
        print('Team created previously')
        dict_racer['team_id'] =  team_id_list[0]

    # CHECK IF TEAM WAS SAVED ON THIS SEASON
    team_season = check_team_season_duplicates(dict_racer['league_id'], dict_racer['season_id'], dict_racer['team_id'])
    if not team_season:
        save_league_team_entity(dict_racer)


dict_sports_url = load_json('check_points/sports_url_m2.json')  # load url sports
sport_mode_dict = check_previous_execution(file_path = 'check_points/CONFIG_M2.json') # load dict of sports modalities
dict_sport_info = load_check_point('check_points/leagues_info.json') # load info loaded previously sport, league_id, season_id
dict_sport_id = get_dict_sport_id() # build dict with sports and sports_id sport_name like key    

def check_duplicate_sports(sport_name):
    # If the sport is new, create and save it in the database; otherwise, retrieve the sport_id.
    if not sport_name in dict_sport_id.keys():              
        sport_dict, sport_id = create_sport_dict(sport_mode_dict[sport_name]['mode'], sport_name)           
        save_sport_database(sport_dict)
    else:
        sport_id = dict_sport_id[sport_name]
    return sport_id

def load_dict_leagues_ready_json(sport_name):
    ###################################################################
    #       LOAD INFO RELATED TO SPORTS AND LEAGUES ()                   #
    # "SPORT": {
    #     "PAIS_LEAGUE_NAME: {"league_name", url, league_id, season_id, country_id, other urls)        
    ###################################################################
    if sport_name in list(dict_sport_info.keys()):
        return dict_sport_info[sport_name]
    else:
        return {}
def create_leagues(driver, list_sports):
    country_list = get_country_list() # Get country list    
    insert_countries_to_db(country_list) # Insert countries in table country

    # ################################################################################
    driver.execute_script("document.body.style.zoom='50%'")# INITIAL ZOOM ADJUST
    
    # for sport_name, sport_info in conf_enable_sport.items():
    #   if sport_info['enable']:
    for sport_name in list_sports:
        try:
            details = {'sport':sport_name}
            ###################################################################
            #                       TITLE SECTION                             #
            ###################################################################
            print_section(sport_name, space_ = 50)
            ###################################################################
            #       CHECK IF SPORT WAS SAVED PREVIOUSLY                       #
            ###################################################################
            sport_id = check_duplicate_sports(sport_name)

            ######################################################################################################################
            # GET DICT WITH LEAGUES SAVED IN DATA_BASE: '{ sport_id _ league_country _ league_name : league_id}                  #
            ######################################################################################################################            
            dict_leagues_ready_db = get_dict_results(table= 'league', columns = 'sport_id, country_id, league_name, league_id')     
            
            ###################################################################
            #               SECTION GET CURRENT LEAGUES                       #
            ###################################################################     
            wait_update_page(driver, dict_sports_url[sport_name], "container__heading")

            #########################################################################################################
            #       LOAD INFO RELATED TO SPORTS AND LEAGUES ()                                                      #
            # "SPORT": {"PAIS_LEAGUE_NAME: {"league_name", url, league_id, season_id, country_id, other urls)       #
            #########################################################################################################
            dict_leagues_ready_json = load_dict_leagues_ready_json(sport_name)

            if sport_name == 'MOTOR SPORT':   
                creale_leagues_f1(driver, sport_name)
            else:
                new_dict_leagues = find_ligues_torneos(driver)
                count_league = 1
                ###################################################################
                #                       LOOP OVER LEAGUES                         #
                ###################################################################
                for league_name, league_url in new_dict_leagues.items():
                    details.update({"league":league_name, 'url':league_url})
                    enable_save = False
                    print("***", league_name,"***", " "*(50-len(league_name)), count_league, "/" ,len(new_dict_leagues))
                    wait_update_page(driver, league_url, "container__heading")
                    count_league += 1
                    pin_activate = check_pin(driver) # CHECK PIN ACTIVE.
                    if pin_activate:
                        # EXTRACT LEAGUES DATA FROM THE CURRENT URL
                        if sport_name == 'BOXING':                  
                            print_section("BOXING CASE")
                            league_info = get_league_data_boxing(driver, league_name, sport_name)
                        else:
                            league_info = get_league_data(driver, league_name, sport_name)

                        print_section("LEAGUE INFO")                    
                        print(league_info)
                        league_info['country_id'] = get_country_id(league_info['league_country'])
                        # Check if the country is saved in the database; if not, create it.
                        if not league_info['country_id']:
                            league_info['country_id'] = insert_country(league_info['league_country'])
                            print(f"Country {league_info['league_country']} created ")
                        print(league_info)
                        sport_leag_countr_name_db = sport_id+"_"+league_info['country_id'] +'_'+ league_info['league_name']
                        sport_leag_countr_name_json = league_info['league_country'] +'_'+ league_info['league_name']
                        print("key db ", sport_leag_countr_name_db)
                        print("key json: ", sport_leag_countr_name_json)
                        ###################################################################
                        #           SECTION CHECK IF LEAGUE WAS SAVED IN DB               #
                        ###################################################################
                        print("dict_leagues_ready_db")
                        print("#"*80)
                        if sport_leag_countr_name_db in list(dict_leagues_ready_db.keys()):                 
                            # print(" "*(60-len(sport_leag_countr_name_json))," READY")
                            print_section(" READY", space_ = 10)
                            print(sport_leag_countr_name_json)
                            league_id = dict_leagues_ready_db[sport_leag_countr_name_db]                    
                            league_info['league_id'] = league_id # REPLACE LEAGUE ID WITH LEAGUE ID FROM DATABASE
                            print("League id from db: ", league_id)
                        else:
                            enable_save = True
                            save_image(driver, league_info['image_url'], league_info['image_path'])
                            # print(" "*(60-len(sport_leag_countr_name_json)), " NEW LEAGUE")
                            print_section(" NEW LEAGUE", space_ = 10)
                            print(sport_leag_countr_name_json)
                            league_id = league_info['league_id']                    
                            save_league_info(league_info)

                        print("LEAGUE ID USED FOR SEASON: ", league_id)
                        ###################################################################
                        #           SECTION CHECK SEASON SAVED PREVIUSLY                  #
                        ###################################################################
                        # CHECK SEASON FROM DATA BASE
                        list_seasons = get_seasons(league_id, league_info['season_name'])
                        # list_seasons = [] # UNCOMENT
                        print("list_seasons: ", list_seasons)
                        
                        if len(list_seasons) == 0:
                            enable_save = True
                            print(" "*30, "SAVE NEW SEASON", league_info['season_id'])
                            save_season_database(league_info) # UNCOMENT

                        ###################################################################
                        #           SECTION CHECK SEASON SAVED PREVIUSLY                  #
                        ###################################################################

                        if enable_save:
                            dict_leagues_ready_json[sport_leag_countr_name_json] = {'league_name':league_info['league_name'] ,
                                                                    'url':league_url, 'league_id':league_id,
                                                                    'season_id':league_info['season_id'],
                                                                    'country_id':league_info['country_id']}

                        # GET SECTIONS LINKS
                        dict_sections_links = get_sections_links(driver)
                        for section, url_section in dict_sections_links.items():
                            dict_leagues_ready_json[sport_leag_countr_name_json][section] = url_section

                    # SAVE JSON FILE WITH THE INFORMATION RELATED TO EACH LEAGUE
                    if enable_save:
                        dict_sport_info[sport_name] = dict_leagues_ready_json
                    save_check_point('check_points/leagues_info.json', dict_sport_info)
                    
                    # stop_validate()
            # driver.quit()
        except WebDriverException as e:
            print("SAVE ERROR REGISTER")
            log_selenium_error(driver, e, details)
        # finally:
        #     driver.quit()
            
def creale_leagues_f1(driver, sport_name):
    list_enables = ['FORMULA 1']
    dict_categories_info = find_categories_motor_sport(driver, list_enables)                
    create_drivers_teams(driver, dict_categories_info) # Create Category = Create league                
    dict_sport_info[sport_name] = dict_categories_info # create_teams()# Escuderias equipos de autos.                
    save_check_point('check_points/leagues_info.json', dict_sport_info)

def initial_settings_m2(driver):

    # GET SPORTS AND SPORTS LINKS
    if not os.path.isfile('check_points/sports_url_m1.json'):
        driver.get('https://www.flashscore.com')
        dict_sports = get_sports_links(driver)
        save_check_point('check_points/sports_url_m2.json', dict_sports)

    # BUILD CONFIG_M2
    if not os.path.isfile('check_points/CONFIG_M2.json'):
        dict_sports = load_json('check_points/sports_url_m2.json')
        dict_sports
        dict_config_m2 = {}
        for sport in dict_sports.keys():
            dict_config_m2[sport] = False
        save_check_point('check_points/CONFIG_M2.json', dict_config_m2)
