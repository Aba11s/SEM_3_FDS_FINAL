from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException, WebDriverException

import pandas as pd
import seaborn as sb
import os.path
import time
import datetime as dt
from collections import deque\

LINK = "https://csstats.gg/match"
PATH = "C:\Program Files (x86)\Devtools\chromedriver-win64\chromedriver.exe" # depends on your system


# -- DRIVER SETUP -- #
options = webdriver.ChromeOptions()

# prevents driver from automaticallty closing the window
options.add_experimental_option(name="detach", value=True)
# prevents weird ass info
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

cService = webdriver.ChromeService(executable_path=PATH)
driver = webdriver.Chrome(options=options, service=cService)

# ensures viewport is same on all devices (namely PCs and laptops)
driver.maximize_window()

# adds an implicit delay to wait for loading, pop-ups, etc
driver.implicitly_wait(10)


# -- DATAFRAME SETUP -- #
df_matches_pmr = pd.read_csv('data/matches_pmr.csv')

pmr_match_ids = df_matches_pmr["match_id"].to_list()

# player feature reference
features = [
    "map_bias",
    "avg_rank",
    "rank_var",
    "ACR",
    "BAtR",
    "KD",
    "HLTVr",
    "CSp",
    "ESp",
    "WR",
    "MWR",
    "MPR",
    ]

# dataframe for features
if os.path.exists('data/stats_pmr.csv'):
    df_stats_pmr = pd.read_csv('data/stats_pmr.csv', index_col=0)
else:
    df_stats_pmr = pd.DataFrame(
        columns=[
            "match_id",
            "map_bias",
            "t1_p1",
            "t1_p2",
            "t1_p3",
            "t1_p4",
            "t1_p5",
            "t2_p1",
            "t2_p2",
            "t2_p3",
            "t2_p4",
            "t2_p5",
            "winner"

        ]
    )

map_bias = {
    "de_dust2"   :  0.492,
    "de_mirage"  :  0.491,
    "de_inferno" :  0.503,
    "de_nuke"    :  0.470,
    "de_vertigo" :  0.478,
    "de_overpass":  0.482,
    "de_office"  :  0.542,
    "de_anubis"  :  0.514,
    "de_ancient" :  0.497,
    "de_italy"   :  0.578
}

while True:
    try:
        # -- RUN -- #
        driver.get(LINK)
        running = True

        # handling pop-up with shadow DOM
        try:
            shadow_parent = driver.find_element(by=By.CSS_SELECTOR, value='#usercentrics-root')
            outer = driver.execute_script('return arguments[0].shadowRoot', shadow_parent)
            cookie_button = outer.find_element(By.CSS_SELECTOR, "button[data-testid='uc-accept-all-button']")
            cookie_button.click()
        except Exception:
            pass

        # checks if match_id has been scraped
        scraped_ids = df_stats_pmr['match_id'].to_list()

        # scrapes individual matches
        for id in pmr_match_ids:
            
            # skips if already scraped
            if id in scraped_ids:
                continue

            web_path = LINK + "/" + str(id)
            driver.get(web_path)

            # checks if t1 win or lose
            scores = driver.find_elements(By.XPATH, '//span[@class="team-score-number"]')
            winner = "team_1" if int(scores[0].text) >= int(scores[1].text) else "team_2"
            print(f"WINNER = {winner}")

            # get map
            match_map = driver.find_element(By.XPATH, '//div[@class="flex flex-wrap "]/div[3]/img').get_attribute('title')

            # get map bias
            bias = map_bias.get(match_map)

            # getting link to each player stats
            player_links = []

            table = driver.find_element(By.TAG_NAME, "table")
            tbodies = table.find_elements(By.TAG_NAME, "tbody") # tbody[0] = t1, tbody[2] = t2

            #t1
            rows = tbodies[0].find_elements(By.TAG_NAME, "tr")
            for row in rows[1:]:
                try:
                    player_links.append(row.find_element(By.TAG_NAME, "a").get_attribute("href"))
                except NoSuchElementException:
                    print("Player is missing")
                    continue

            #t2
            rows = tbodies[2].find_elements(By.TAG_NAME, 'tr')
            for row in rows[1:]:
                try:
                    player_links.append(row.find_element(By.TAG_NAME, "a").get_attribute("href"))
                except NoSuchElementException:
                    print("Player is missing")
                    continue

            players_stats = [None]*10
            p_index = 0
            
            # goes to each player stats
            for link in player_links:
                driver.get(link)

                player_ranks = driver.find_elements(By.XPATH, '//div[@class="ranks"]')

                # player ratings
                for p in player_ranks:
                    if p.find_element(By.TAG_NAME, "img").get_attribute("title") == "Premier":
                        over = p.find_element(By.TAG_NAME, 'div')
                        overs = over.find_elements(By.TAG_NAME,'div')

                        # current rating
                        try:
                            current_rating = int(overs[1].text.replace(',',''))
                        except Exception:
                            current_rating = 0
                        
                        # best rating
                        try:
                            best_rating = int(overs[-1].text.replace(',',''))
                        except Exception:
                            best_rating = current_rating

                        #print(f"current rating: {current_rating},  best rating: {best_rating}\n")
                        break

                # KD
                try:
                    kd = float(driver.find_element(By.XPATH, '//div[@class="col-sm-8"]/div[1]/div[1]/div/div[2]/div[2]/div/span').text)
                except ValueError:
                    kd = float(0)

                # HLTV rating
                try:
                    hltvr = float(driver.find_element(By.XPATH, '//div[@class="col-sm-8"]/div[1]/div[2]/div/div[2]/div[2]/div/span').text)
                except ValueError:
                    hltvr = float(0)

                # WR (win rate)
                try:
                    wr = float(driver.find_element(By.XPATH, '//div[@class="col-sm-8"]/div[1]/div[3]/div/div[2]/div[2]').text.replace('\n','').replace(' ','').split('%')[0])/100
                except ValueError:
                    wr = float(0)

                # HSp (head shots percentage)
                try:
                    hs = float(driver.find_element(By.XPATH, '//div[@class="col-sm-8"]/div[1]/div[4]/div/div[2]/div[2]').text.replace('\n','').replace(' ','').split('%')[0])/100
                except ValueError:
                    hs = float(0)

                # ADR
                try:
                    adr = float(driver.find_element(By.XPATH, '//div[@class="col-sm-8"]/div[1]/div[5]/div/div[2]/div[2]').text[:-1])/100
                except ValueError:
                    adr = float(0)
                    
                # CSp (clutch success)
                try:
                    cs = float(driver.find_element(By.XPATH, '//div[@class="col-sm-8"]/div[2]/div/div[1]/div[2]/div/span[2]').text[:-1])/100
                except ValueError:
                    cs = float(0)
                    
                # ESp (entry success)
                try:
                    es = float(driver.find_element(By.XPATH, '//div[@class="col-sm-8"]/div[2]/div/div[2]/div[2]/div/span[2]').text[:-1])/100
                except ValueError:
                    es = float(0)
                    
                print(f"\nCS | ES : {cs} | {es}")
                print(f"WR | HS : {wr} | {hs}")
                print(f"kd | hltvr : {kd} | {hltvr}")

                # Maps stats
                driver.get(link+"#/maps")

                maps = driver.find_elements(By.XPATH, '//div[@class="content-tab current-tab"]/div/div')[1:]

                play_count = 0
                highest_play_count = 0
            
                for map in maps:
                    map_title = map.find_element(By.TAG_NAME, 'span').text
                    map_stat = map.find_element(By.TAG_NAME, 'div')
                    
                    # MWR (map win rate)
                    if map_title == match_map:
                        mwr = int(map_stat.find_elements(By.TAG_NAME, 'div')[2].text[:-1])/100
                        highest_play_count = int(map_stat.find_element(By.XPATH, './div[@style="float:left; padding-top:22px; width:20%"]').text)
                        
                    # MPR (map play rate)
                    play_count += int(map_stat.find_element(By.XPATH, './div[@style="float:left; padding-top:22px; width:20%"]').text)
            
                mpr = play_count and highest_play_count / play_count or 0
                print(f"MWR | MPR : {mwr} | {mpr}")

                '''
                current_rank, best_rank, kd, hltvr, wr, hs, adr, cs, es, mwr, mpr
                '''
                player_stats = [current_rating, best_rating, kd, hltvr, wr, hs, adr, cs, es, mwr, mpr] 
                players_stats[p_index] = player_stats
                p_index += 1      
                
            # appends to dataframe
            new_row = {
                "match_id":id,
                "map_bias":bias,
                "t1_p1":players_stats[0],
                "t1_p2":players_stats[1],
                "t1_p3":players_stats[2],
                "t1_p4":players_stats[3],
                "t1_p5":players_stats[4],
                "t2_p1":players_stats[5],
                "t2_p2":players_stats[6],
                "t2_p3":players_stats[7],
                "t2_p4":players_stats[8],
                "t2_p5":players_stats[9],
                "winner": winner
            }

            df_stats_pmr = df_stats_pmr._append(new_row, ignore_index=True)
            df_stats_pmr.reset_index(inplace = True, drop = True)
            df_stats_pmr.to_csv('data/stats_pmr.csv')

    except Exception:
        print("Driver closed unexpectedly, restarting. . .")
        time.sleep(5) 


        
        










                

            


