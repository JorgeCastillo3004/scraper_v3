import time
import json
import re
import os

from common_functions import *
from data_base import *
from milestone1 import *
from milestone2 import *
from milestone3 import *
from milestone4 import *
from milestone6 import *
from milestone7 import *
from milestone8 import *

CONFIG = load_json('check_points/CONFIG.json')
database_enable = CONFIG['DATA_BASE']
if database_enable:
    con = getdb()

def main():
    main_extract_news_enable = False    # 1
    create_leagues_flag      = False    # 2
    teams_creation_flag      = False    # 3
    results_extraction_flag  = False    # 4
    fixture_extraction_flag  = True     # 5 — ACTIVO
    players_flag             = False    # 6
    live_games_flag          = False

    if main_extract_news_enable:
        main_extract_news(driver, ["FOOTBALL"], MAX_OLDER_DATE_ALLOWED=30)

    if create_leagues_flag:
        create_leagues(driver, ["FOOTBALL"])

    if teams_creation_flag:
        teams_creation(driver, ["FOOTBALL"])

    if results_extraction_flag:
        results_fixtures_extraction(driver, ["FOOTBALL"], name_section='results')

    if fixture_extraction_flag:
        results_fixtures_extraction(driver, ["FOOTBALL"], name_section='fixtures')

    if players_flag:
        players(driver, ["FOOTBALL", "BASKETBALL", "BASEBALL", "AM. FOOTBALL", "HOCKEY"])

    if live_games_flag:
        update_lives_matchs(driver)

if __name__ == "__main__":
    driver = launch_navigator('https://www.flashscore.com', headless=True)
    login(driver, email_="jignacio@jweglobal.com", password_="Caracas5050@\n")
    main()
    if database_enable:
        con.close()
