import psycopg2
from common_functions import load_json
from unidecode import unidecode
import re
import hashlib
import pycountry

def getdb():
    return psycopg2.connect(
                host="localhost",
                user="wohhu",
                password="caracas123",
        dbname='sports_db',
        )

def save_news_database(dict_news):  
    try:
        query = "INSERT INTO news VALUES(%(news_id)s, %(news_content)s, %(image)s,\
                %(published)s, %(news_summary)s, %(news_tags)s, %(title)s)"
        cur = con.cursor()
        cur.execute(query, dict_news)
        con.commit()
    except:
        print("###### ERROR SAVING NEWS ######")
        con.rollback()

def save_sport_database(sport_dict):
    try:
        query = "INSERT INTO sport VALUES(%(sport_id)s, %(is_active)s, %(desc_i18n)s,\
                                         %(logo)s, %(sport_mode)s, %(name_i18n)s, %(point_name)s, %(name)s)"
        cur = con.cursor()
        cur.execute(query, sport_dict)
        con.commit()
    except:
        con.rollback()

def get_country_list():
    """
    Returns a list of country names in English using pycountry.
    """
    return [country.name for country in pycountry.countries]

def generate_unique_id(input_string):
    """
    Generates a unique 17-character ID from a given string.
    The same input will always generate the same output.
    
    :param input_string: The input string (e.g., a country name).
    :return: A unique 17-character string ID.
    """
    # Step 1: Normalize the input string (strip spaces, convert to lowercase)
    normalized_string = input_string.strip().lower()
    
    # Step 2: Create a SHA-256 hash of the normalized string
    hash_object = hashlib.sha256(normalized_string.encode())  
    hex_hash = hash_object.hexdigest()  # Convert hash to hexadecimal string
    
    # Step 3: Convert the hexadecimal hash to base 36 (more compact and readable)
    base36_hash = int(hex_hash, 16)  # Convert hex to integer
    base36_string = base36_encode(base36_hash)  # Convert to base 36
    
    # Step 4: Return the first 17 characters to ensure a fixed-length ID
    return base36_string[:17]

def base36_encode(number):
    """Encodes an integer into a base-36 string."""
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    base36 = ''
    
    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36
    
    return base36 or '0'

def insert_country(country_name):
    cur = con.cursor()
    country_name = country_name.upper().split(',')[0]
    if ',' in country_name:
        country_name = country_name.split(',')[0]
    country_id = generate_unique_id(country_name)
    country_name_i18n = ''
    country_logo = ''
    dict_country = {'country_id': country_id, 'country_name': country_name,
                    'country_name_i18n': country_name_i18n, 'country_logo': country_logo}
    try:
        query = """INSERT INTO COUNTRY (country_id, country_name, country_name_i18n, country_logo) 
                    VALUES (%(country_id)s, %(country_name)s, %(country_name_i18n)s, %(country_logo)s)"""
        cur.execute(query, dict_country)
        con.commit()
        return country_id
    except:
        con.rollback()
      
def insert_countries_to_db(countries):
    try:
        cur = con.cursor()  # Crear cursor fuera del bucle para eficiencia
        
        for country in countries:
            country = country.upper().split(',')[0]
            if ',' in country:
                country = country.split(',')[0]
            country_id = generate_unique_id(country)
            country_name_i18n = ''
            country_logo = ''
            dict_country = {'country_id': country_id, 'country_name': country,
                            'country_name_i18n': country_name_i18n, 'country_logo': country_logo}

            # Verificar si el país ya existe en la base de datos
            check_query = "SELECT 1 FROM COUNTRY WHERE country_id = %(country_id)s"
            cur.execute(check_query, {'country_id': country_id})
            exists = cur.fetchone()

            if exists:
                print(f"⚠️ País '{country}' ya existe en la base de datos. Se omite la inserción.")
            else:
                query = """INSERT INTO COUNTRY (country_id, country_name, country_name_i18n, country_logo) 
                           VALUES (%(country_id)s, %(country_name)s, %(country_name_i18n)s, %(country_logo)s)"""
                cur.execute(query, dict_country)
                con.commit()
                # print(f"✅ País '{country}' insertado correctamente.")

    except Exception as e:
        # print(f"❌ Error: {e}")
        con.rollback()    

def get_country_id(country_name):
    """
    Retrieves the country_id from the database based on the given country_name.
    
    Parameters:
    - country_name (str): Name of the country to search for.
    - con (psycopg2.connection): Active database connection.

    Returns:
    - str: The country_id if found, otherwise None.
    """
    try:
        cur = con.cursor()
        
        # Query to search for the country in the database
        query = "SELECT country_id FROM COUNTRY WHERE country_name = %s LIMIT 1;"
        
        cur.execute(query, (country_name,))
        result = cur.fetchone()  # Fetch only one result
        
        cur.close()  # Close the cursor
        
        if result:
            return result[0]  # Return country_id
        else:
            print(f"⚠️ Country '{country_name}' not found in the database.")
            return None

    except Exception as e:
        print(f"❌ Error fetching country_id: {e}")
        return None

def get_dict_sport_id():
    query = "SELECT sport.name, sport.sport_id FROM sport"
    # 
    # -- WHERE team.sport_id = '{}'
    cur = con.cursor()
    cur.execute(query)  
    dict_results = {row[0] : row[1] for row in cur.fetchall()}
    return dict_results

def save_league_info(dict_league_tornament): 
    query = "INSERT INTO league VALUES(%(league_id)s, %(country_id)s, %(league_logo)s, %(league_name)s, %(league_name_i18n)s, %(sport_id)s)"
    cur = con.cursor()                                                                           
    cur.execute(query, dict_league_tornament)                                                         
    con.commit()                                                                                     

def save_season_database(season_dict):
    query = "INSERT INTO season VALUES(%(season_id)s, %(season_name)s, %(season_end)s,\
                                     %(season_start)s, %(league_id)s)"
    cur = con.cursor()
    cur.execute(query, season_dict)
    con.commit()

def save_tournament(dict_tournament):
    query = "INSERT INTO tournament VALUES(%(tournament_id)s, %(team_country)s, %(desc_i18n)s,\
                                     %(end_date)s, %(logo)s, %(name_i18n)s, %(season)s, %(start_date)s, %(tournament_year)s)"
    cur = con.cursor()
    cur.execute(query, dict_tournament)
    con.commit()

def save_team_info(dict_team):
    query = "INSERT INTO team VALUES(%(team_id)s, %(country_id)s, %(team_desc)s,\
     %(team_logo)s, %(team_name)s, %(sport_id)s)"
    cur = con.cursor()                                                                           
    cur.execute(query, dict_team)                                                        
    con.commit()

def save_league_team_entity(dict_team):
    query = "INSERT INTO league_team VALUES(%(instance_id)s, %(team_meta)s, %(team_position)s, %(league_id)s, %(season_id)s, %(team_id)s)"  
    cur = con.cursor()
    cur.execute(query, dict_team)
    con.commit()

def save_player_info(dict_team):    
    print("save_player info")    
    try:
        query = "INSERT INTO player VALUES(%(player_id)s, %(country_id)s, %(player_dob)s,\
        %(player_name)s, %(player_photo)s, %(player_position)s)"
        cur = con.cursor()
        cur.execute(query, dict_team)
        con.commit()
    except Exception as error:
        print(error)        
        con.rollback()

def save_team_players_entity(player_dict):
    query = "INSERT INTO team_players_entity VALUES(%(player_meta)s, %(season_id)s, %(team_id)s,\
     %(player_id)s)"
    cur = con.cursor()
    cur.execute(query, player_dict)
    con.commit()

def get_team_id(league_id, season_id, team_name):
    query = """
    SELECT t2.team_id \
    FROM league_team AS t1\
    JOIN team AS t2 ON t1.team_id = t2.team_id\
    WHERE t1.league_id = '{}' AND t1.season_id = '{}' AND t2.team_name = '{}'""".format(league_id, season_id, team_name)

    cur = con.cursor()
    cur.execute(query)
    results = cur.fetchone()
    return results[0]

def get_seasons(league_id, season_name):
    query = "SELECT season_name, season_id FROM season  WHERE league_id ='{}' and season_name = '{}';".format(league_id, season_name)
    cur = con.cursor()
    cur.execute(query)  
    results = [row[0] for row in cur.fetchall()]
    for row in cur.fetchall():
        print(row)
    return results

def get_list_id_teams(sport_id, country_id, team_name):
    query = """SELECT team_id FROM team WHERE sport_id ='{}' and country_id = '{}' and team_name = '{}';""".format(sport_id, country_id, team_name)
    cur = con.cursor()
    cur.execute(query)  
    results = [row[0] for row in cur.fetchall()]
    return results

def get_dict_results(table= 'league', columns = 'sport_id, league_country, league_name, league_id'):    
    query = f"SELECT {columns} FROM {table};"   
    cur = con.cursor()
    cur.execute(query)
    dict_results = {row[0] + '_'+ row[1] + '_' + row[2]: row[3] for row in cur.fetchall()}
    return dict_results

def get_dict_teams(sport_id = 'FOOTBALL'):
    query = """
    SELECT league.league_country, team.team_name, team.team_id\
    FROM team \
    JOIN league_team ON team.team_id = league_team.team_id\
    JOIN league league_team.league_id = league.league_id    
    WHERE team.id_sport = '{}'""".format(sport_id)

    cur = con.cursor()
    cur.execute(query)

    dict_results = {unidecode('-'.join(row[0].replace('&', '').split() ) ).upper():\
                    {'team_name': unidecode('-'.join(row[1].split() ) ).upper(),\
                     'team_id': row[2]} for row in cur.fetchall()}
    return dict_results

def get_dict_league_ready(sport_id = 'TENNIS'):
    #####################################################################
    #		GET DICT WITH LEAGUES SAVED IN DATA_BASE 				  	#
    #		'{ sport_id: 												#
    #					team_country: 									#
    #						league_country 								#
    #								team_name: team_id}   				#
    #																  	#
    #				get_dict_league_ready 								#
    #####################################################################
    query = """
        SELECT team.sport_id, team.country_id, league.country_id, team.team_name, team.team_id
        FROM team
        JOIN league_team ON team.team_id = league_team.team_id
        JOIN league ON league_team.league_id = league.league_id
        WHERE team.sport_id = '{}'""".format(sport_id)
    # 
    # -- WHERE team.sport_id = '{}'
    cur = con.cursor()
    cur.execute(query)
    results = cur.fetchall()
    dict_results = {}
    for row in results: 
        dict_results.setdefault(row[0], {}).setdefault(row[1], {}).setdefault(row[2], {})[row[3]] = {'team_id': row[4]} 

    return dict_results

######################################## FUNCTIONS RELATED TO MATCHS ########################################
def save_math_info(dict_match):    
    # print("dict_match: ", dict_match['statistic'])
    # table_dict = {
    # "match_id": 255,
    # "match_country": 80,
    # "end_time": 1,  # No es una cadena de caracteres
    # "match_date": 1,  # No es una cadena de caracteres
    # "name": 70,
    # "place": 128,
    # "start_time": 1,  # No es una cadena de caracteres
    # "league_id": 40,
    # "stadium_id": 255,
    # "tournament_id": 255,
    # "rounds": 40,
    # "season_id": 40,
    # "status": 40,
    # "statistic": 1600}

    # for key, value in dict_match.items():
    #     try:
    #         print(f"{key} {len(value)}/{table_dict[key]} {value}")
    #     except:
    #         print("Possible error: ")
    #         print(f"key: {key}, value:{value} #")
    query = "INSERT INTO match VALUES(%(match_id)s, %(country_id)s, %(end_time)s,\
     %(match_date)s, %(name)s, %(place)s, %(start_time)s, %(league_id)s, \
     %(stadium_id)s, %(tournament_id)s,%(rounds)s, %(season_id)s, \
         %(statistic)s, %(status)s, %(sport_id)s )"
    print(query)
    cur = con.cursor()
    cur.execute(query, dict_match)
    con.commit()

def save_details_math_info(dict_match):
    query = "INSERT INTO match_detail VALUES(%(match_detail_id)s, %(home)s, %(visitor)s,\
     %(match_id)s, %(team_id)s)"
    cur = con.cursor()
    cur.execute(query, dict_match)
    con.commit()

def save_score_info(dict_match):
    query = "INSERT INTO score_entity VALUES(%(score_id)s, %(points)s, %(match_detail_id)s)"
    cur = con.cursor()
    cur.execute(query, dict_match)
    con.commit()

def save_stadium(dict_match):
    query = "INSERT INTO stadium VALUES(%(stadium_id)s, %(capacity)s,\
     %(desc_i18n)s, %(name)s, %(photo)s)"
    cur = con.cursor()
    cur.execute(query, dict_match)
    con.commit()

def get_rounds_ready(league_id, season_id):
    query = "SELECT DISTINCT rounds FROM match WHERE league_id = '{}' AND season_id = '{}';".format(league_id, season_id)   
    print("query inside rounds ready: ")
    print(query)
    cur = con.cursor()
    cur.execute(query)  
    results = [row[0] for row in cur.fetchall()]
    return results

def check_league_duplicate(league_id):
    query = "SELECT league_id FROM league WHERE league_id ='{}';".format(league_id) 
    cur = con.cursor()
    cur.execute(query)  
    results = [row[0] for row in cur.fetchall()]
    return results

def check_season_duplicate(season_id):
    query = "SELECT season_id FROM season WHERE season_id ='{}';".format(season_id) 
    cur = con.cursor()
    cur.execute(query)  
    results = [row[0] for row in cur.fetchall()]
    return results

def check_player_duplicates(player_country, player_name, player_dob):
    query = "SELECT player_id FROM player WHERE player_country ='{}' AND player_name ='{}' AND player_dob ='{}';".format(player_country, player_name, player_dob)
    print("Check player duplicates")
    print(query)
    cur = con.cursor()
    cur.execute(query)  
    results = [row[0] for row in cur.fetchall()]
    return results

def check_player_duplicates_id(player_id):
    query = "SELECT player_id FROM player WHERE player_id ='{}';".format(player_id) 
    cur = con.cursor()
    cur.execute(query)  
    results = [row[0] for row in cur.fetchall()]
    return results

def check_team_duplicates(team_name, sport_id):
    query = "SELECT team_id FROM team WHERE team_name ='{}' AND sport_id ='{}';".format(team_name, sport_id)
    cur = con.cursor()
    cur.execute(query)  
    results = [row[0] for row in cur.fetchall()]
    return results

def check_team_duplicates_id(team_id):
    query = "SELECT team_id FROM team WHERE team_id ='{}';".format(team_id)
    print("check team duplicates")
    print(query)
    cur = con.cursor()
    cur.execute(query)  
    results = [row[0] for row in cur.fetchall()]
    return results

def get_team_id_f1(team_name):
    query = f"SELECT team_id, team_name FROM team WHERE team_desc ='{team_name}'"
    cur = con.cursor()
    cur.execute(query)  
    results = {row[0]: row[1] for row in cur.fetchall()}
    return results

def get_team_id_pilot(racer_name, team_name):    
    dict_team_id = get_team_id_f1(team_name)
    for team_id, complete_name in dict_team_id.items():        
        if racer_name.upper().split()[0] in complete_name.upper().split():
            return team_id

def check_team_season_duplicates(league_id, season_id, team_id):
    query = "SELECT season_id FROM league_team WHERE league_id ='{}' AND season_id ='{}' AND team_id ='{}';".format(league_id, season_id, team_id)
    cur = con.cursor()
    cur.execute(query)  
    results = [row[0] for row in cur.fetchall()]
    return results

def check_team_player_entitiy(season_id, team_id, player_id):
    query = """SELECT player_id FROM team_players_entity WHERE
                 season_id ='{}' AND team_id ='{}' AND player_id ='{}';""".format(season_id, team_id, player_id)
    cur = con.cursor()
    cur.execute(query)  
    results = [row[0] for row in cur.fetchall()]
    return results  

def get_match_id(league_country, league_name, match_date, match_name):
    
    query = """
    SELECT match.match_id
    FROM match
    JOIN league ON league.league_id = match.league_id
    WHERE league.league_country = '{}' and 
    league.league_name = '{}' and 
    match.match_date = '{}' and match.name = '{}'""".format(league_country, league_name, match_date, match_name)    
    cur = con.cursor()
    cur.execute(query)
    return cur.fetchone()

def get_math_details_ids(match_id):
    query = """
    SELECT match_detail_id, home FROM match_detail
     WHERE match_id = '{}';""".format(match_id);
    cur = con.cursor()
    cur.execute(query)

    dict_results = {row[0]:row[1] for row in cur.fetchall()}
    return dict_results

def get_match_ready(match_id):
    query = "SELECT MATCH_ID FROM MATCH WHERE MATCH_ID='{}';".format(match_id)  
    cur = con.cursor()
    cur.execute(query)
    results = [row[0] for row in cur.fetchall()]
    return results

def check_match_duplicate(league_id, match_date, match_name):
    query = """SELECT MATCH_ID FROM MATCH WHERE LEAGUE_ID ='{}'
                 AND MATCH_DATE='{}' AND NAME='{}';""".format(league_id, match_date, match_name)    
    print(query)
    cur = con.cursor()
    cur.execute(query)
    results = [row[0] for row in cur.fetchall()]
    return results

def check_match_duplicate2(league_id, match_name):
    query = """SELECT MATCH_ID FROM MATCH WHERE LEAGUE_ID ='{}'
    AND MATCH_DATE = CURRENT_DATE 
    AND NAME='{}';""".format(league_id, match_name)
    print(query)
    cur = con.cursor()
    cur.execute(query)
    results = [row[0] for row in cur.fetchall()]
    return results

def get_stadium_id(place_name):
    query = """SELECT STADIUM_ID FROM STADIUM WHERE NAME ='{}';""".format(place_name)   
    cur = con.cursor()
    cur.execute(query)
    results = [row[0] for row in cur.fetchall()]
    return results

def check_stadium(stadium_id):
    query = """SELECT STADIUM_ID FROM STADIUM WHERE stadium_id ='{}';""".format(stadium_id) 
    cur = con.cursor()
    cur.execute(query)
    results = [row[0] for row in cur.fetchall()]
    return results

def update_score(params):
    query = "UPDATE score_entity SET points = %(points)s WHERE match_detail_id = %(match_detail_id)s"
    # query = "INSERT INTO score_entity VALUES(%(score_id)s, %(points)s, %(match_detail_id)s)"
    cur = con.cursor()
    cur.execute(query, params)
    con.commit()

def update_match_status(params):
    query = "UPDATE match SET status = %(status)s WHERE match_id = %(match_id)s"
    cur = con.cursor()
    cur.execute(query, params)
    con.commit()

def get_match_by_day():
    # Query to retrieve pending matches for updating.
    query = """
        SELECT sport.name, league.league_name, league.country_id,
            match.match_date, match.start_time, match.name, match.match_id
        FROM MATCH 
        JOIN LEAGUE ON MATCH.LEAGUE_ID = LEAGUE.LEAGUE_ID
        JOIN SPORT ON SPORT.SPORT_ID = LEAGUE.SPORT_ID
        WHERE MATCH.MATCH_DATE BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '1 day'
    """
    # AND MATCH.STATUS = 'P' 
    cur = con.cursor()
    cur.execute(query)    
    return cur.fetchall()

def get_match_by_day_internal(delta, interval = 1):
    # Query to retrieve pending matches for updating.
    query = f"""
        SELECT 
            sport.name AS sport_name, 
            league.league_name, 
            league.country_id,
            match.match_date, 
            match.start_time, 
            match.name AS match_name, 
            match.match_id
        FROM match
        JOIN league ON match.league_id = league.league_id
        JOIN sport ON sport.sport_id = league.sport_id
        WHERE 
            (match.match_date + match.start_time) 
            BETWEEN (NOW() + INTERVAL '{str(delta-1)} hour') AND (NOW() + INTERVAL '{str(delta + interval)} hour')
    """    
    # AND MATCH.STATUS = 'P' 
    cur = con.cursor()
    cur.execute(query)    
    return cur.fetchall()

def get_match_by_league_name(league_name_, month_number, day_number):
    # Query to retrieve pending matches for updating.
    query = f"""
        SELECT sport.name, league.league_name, league.league_country,
               match.match_date, match.start_time, match.name, match.match_id
        FROM MATCH 
        JOIN LEAGUE ON MATCH.LEAGUE_ID = LEAGUE.LEAGUE_ID
        JOIN SPORT ON SPORT.SPORT_ID = LEAGUE.SPORT_ID
        WHERE LEAGUE.LEAGUE_NAME LIKE '{league_name_}' AND
              MATCH.STATUS = 'P' AND
              EXTRACT(MONTH FROM match.match_date) = {month_number} AND
              EXTRACT(DAY FROM match.match_date) = {day_number}
    """ 
    cur = con.cursor()
    cur.execute(query)    
    return cur.fetchall()

def get_match_update():
    # Query to retrieve pending matches for updating.
    query = """
        SELECT sport.name, league.league_name, league.league_country,\
        match.match_date, match.start_time, match.name, match.match_id \
        FROM MATCH 
        JOIN LEAGUE ON MATCH.LEAGUE_ID = LEAGUE.LEAGUE_ID
        JOIN SPORT ON SPORT.SPORT_ID = LEAGUE.SPORT_ID
        WHERE MATCH.MATCH_DATE <= CURRENT_DATE AND \
        START_TIME < CURRENT_TIME AND \
        MATCH.STATUS = 'P' 
        """
    cur = con.cursor()
    cur.execute(query)    
    return cur.fetchall()

def get_team_duplicates():
    query = """
    SELECT team_id, team_name, country_id, sport_id
    FROM team
    WHERE (team_name, country_id, sport_id) IN (
        SELECT team_name, country_id, sport_id
        FROM team
        GROUP BY team_name, country_id, sport_id
        HAVING COUNT(*) > 1
    )
    ORDER BY team_name, country_id; 
        """
    cur = con.cursor()
    cur.execute(query)    
    return cur.fetchall()

def delete_team(team_id):
    """
    Deletes records from score_entity table based on match_detail_id.

    :param match_detail_id: ID used to filter rows to delete.
    :param con: psycopg2 database conection object.
    """
    try:
        with con.cursor() as cur:
            query = f"DELETE FROM team WHERE team_id = '{team_id}';"            
            cur = con.cursor()
            cur.execute(query)
            con.commit()
            
    except Exception as e:
        con.rollback()
        print(f"Error deleting team record: {e}")

def delete_league_team(team_id):
    """
    Deletes records from score_entity table based on match_detail_id.

    :param match_detail_id: ID used to filter rows to delete.
    :param con: psycopg2 database conection object.
    """
    try:
        with con.cursor() as cur:
            query = f"DELETE FROM league_team WHERE team_id = '{team_id}';"            
            cur = con.cursor()
            cur.execute(query)
            con.commit()
            
    except Exception as e:
        con.rollback()
        print(f"Error deleting league_team record: {e}")

def get_league_name_country(team_id):
    query = f"""
            SELECT s.name, ct.country_name, l.league_name
            FROM league_team lt
            JOIN league l ON lt.league_id = l.league_id
            JOIN country ct ON l.country_id = ct.country_id
            JOIN sport s ON l.sport_id = s.sport_id
            WHERE lt.team_id = '{team_id}';

            """
    cur = con.cursor()
    cur.execute(query)    
    return cur.fetchone()

def get_list_match_id(team_id):
    query = f"""
            SELECT match_id
            FROM match_detail            
            WHERE team_id = '{team_id}';
            """    
    cur = con.cursor()
    cur.execute(query)    
    return cur.fetchall()

def get_match_details_ids(match_id):
    query = f"""
            SELECT md.match_detail_id
            FROM match_detail md            
            WHERE md.match_id = '{match_id}';
            """    
    cur = con.cursor()
    cur.execute(query)    
    return cur.fetchall()

def delete_score_entity(match_detail_id):
    """
    Deletes records from score_entity table based on match_detail_id.

    :param match_detail_id: ID used to filter rows to delete.
    :param con: psycopg2 database conection object.
    """
    try:
        with con.cursor() as cur:
            query = f"DELETE FROM score_entity WHERE match_detail_id ='{match_detail_id}';"            
            cur = con.cursor()
            cur.execute(query)
            con.commit()            
    except Exception as e:
        con.rollback()
        print(f"Error deleting records: {e}")

def delete_match_detail(match_detail_id):
    """
    Deletes records from score_entity table based on match_detail_id.

    :param match_detail_id: ID used to filter rows to delete.
    :param con: psycopg2 database conection object.
    """
    try:
        with con.cursor() as cur:
            query = f"DELETE FROM match_detail WHERE match_detail_id = '{match_detail_id}';"            
            cur = con.cursor()
            cur.execute(query)
            con.commit()            
            
    except Exception as e:
        con.rollback()
        print(f"Error deleting records: {e}")

def delete_match(match_id):
    """
    Deletes records from score_entity table based on match_detail_id.

    :param match_detail_id: ID used to filter rows to delete.
    :param con: psycopg2 database conection object.
    """
    try:
        with con.cursor() as cur:
            query = f"DELETE FROM match WHERE match_id = '{match_id}';"            
            cur = con.cursor()
            cur.execute(query)
            con.commit()
            
    except Exception as e:
        con.rollback()
        print(f"Error deleting records: {e}")

def delete_team_players_entity(team_id):
    """
    Deletes records from score_entity table based on match_detail_id.

    :param match_detail_id: ID used to filter rows to delete.
    :param con: psycopg2 database conection object.
    """
    try:
        with con.cursor() as cur:
            query = f"DELETE FROM team_players_entity WHERE team_id = '{team_id}';"
            cur = con.cursor()
            cur.execute(query)
            con.commit()
            
    except Exception as e:
        con.rollback()
        print(f"Error deleting league_team record: {e}")

def delete_player_id(player_id):
    """
    Deletes records from score_entity table based on match_detail_id.

    :param match_detail_id: ID used to filter rows to delete.
    :param con: psycopg2 database conection object.
    """
    try:
        with con.cursor() as cur:
            query = f"DELETE FROM player WHERE player_id = '{player_id}';"
            cur = con.cursor()
            cur.execute(query)
            con.commit()
            
    except Exception as e:
        con.rollback()
        print(f"Error deleting player_id record: {e}")


def get_player_ids(team_id):
    query = f"""
            SELECT player_id
            FROM team_players_entity
            WHERE team_id = '{team_id}';
            """    
    cur = con.cursor()
    cur.execute(query)    
    return cur.fetchall()


def delete_team_duplicate(team_id):

    match_ids = get_list_match_id(team_id)
    
    for match_id in match_ids:
    
        list_details_id = get_match_details_ids(match_id[0])
        for match_detail_id in list_details_id:                
            print(f"delete current match_detail_id: {match_detail_id[0]}")
            delete_score_entity(match_detail_id[0])
            delete_match_detail(match_detail_id[0])
        delete_match(match_id[0])
    delete_league_team(team_id)
    delete_team(team_id)
    # delete player, team_players_entity
    list_players_id = get_player_ids(team_id)
    for player_id in list_players_id:
        delete_player_id(player_id)
    delete_team_players_entity(team_id)

con = getdb()