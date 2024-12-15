from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException

import pandas as pd
import seaborn as sb
import os.path
import time
import datetime as dt
from collections import deque

LINK = "https://csstats.gg/match"
PATH = "C:\Program Files (x86)\Devtools\chromedriver-win64\chromedriver.exe" #depends on your system

# -- DATAFRAME SETUP -- #

if os.path.exists('data/matches_pmr_2.csv'):
    df_matches_pmr = pd.read_csv('data/matches_pmr_2.csv', index_col=0)
else:
    df_matches_pmr = pd.DataFrame(
        columns=[
            'match_id',
            'premiere_rating',
            'date',
            'map',
            'team_1',
            'team_1_score',
            'team_2',
            'team_2_score',
            'KDA'
            ]
    )

if os.path.exists('data/matches_ofc_2.csv'):
    df_matches_ofc = pd.read_csv('data/matches_ofc_2.csv', index_col=0)
else:
    df_matches_ofc = pd.DataFrame(
        columns=[
            'match_id',
            'official_rank',
            'date',
            'map',
            'team_1',
            'team_1_score',
            'team_2',
            'team_2_score',
            'KDA'
            ]
    )

# stores last 50 match id's to check for duplicates
last_50 = []
last_50.extend(df_matches_pmr.tail(50)['match_id'].to_list())
last_50.extend(df_matches_ofc.tail(50)['match_id'].to_list())
print(last_50)

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
driver.implicitly_wait(15)


# -- RUN -- #
driver.get(LINK)
running = True

# handling pop-up with shadow DOM
shadow_parent = driver.find_element(by=By.CSS_SELECTOR, value='#usercentrics-root')
outer = driver.execute_script('return arguments[0].shadowRoot', shadow_parent)
cookie_button = outer.find_element(By.CSS_SELECTOR, "button[data-testid='uc-accept-all-button']")
cookie_button.click()

while running:
    # break case
    try:
       # selecting table
        driver.implicitly_wait(0)
        table = driver.find_element(by=By.XPATH, value='//table[@class="table table-striped"]')

        # selecting rows
        rows = table.find_elements(by=By.TAG_NAME, value='tr')

        # selecting columns/cells
        for row in rows[1:]: # skips header row
            cells = row.find_elements(By.TAG_NAME, value='td')
            is_premiere = True

            # match_id
            match_id = int(row.get_attribute('onclick').split('/')[2][:-1])
            if match_id in last_50:
                continue # ignore duplicate matches
                print("Duplicate e")
            else:
                last_50.append(match_id)
                print(last_50.pop(0))
            
            # premiere rating / official rank / none
            if len(cells[1].find_elements(By.TAG_NAME, 'div')) > 0:
                rating = int(cells[1].find_element(By.TAG_NAME, 'span').text.replace(',',''))

            elif len(cells[1].find_elements(By.TAG_NAME, 'img')) > 0:
                is_premiere = False
                rank = cells[1].find_element(By.TAG_NAME, 'img').get_attribute('title')

            else: # ignore all non-competitive matches
                continue

            # date
            date = pd.to_datetime('now')
            # map
            try:
                match_map = cells[4].find_element(By.TAG_NAME, 'img').get_attribute('title')
            except NoSuchElementException:
                match_map = cells[4].text

            # teams
            arr_t1 = []
            elm_c5 = cells[5].find_elements(By.TAG_NAME, 'img')
            for elm in elm_c5:
                arr_t1.append(elm.get_attribute('title'))

            arr_t2 = []
            elm_c8 = cells[8].find_elements(By.TAG_NAME, 'img')
            for elm in elm_c8:
                arr_t2.append(elm.get_attribute('title'))

            # scores
            score_t1 = cells[6].text
            score_t2 = cells[7].text

            # KDA
            match_kda = []
            match_kda.append(cells[9].text)
            match_kda.append(cells[10].text)
            match_kda.append(cells[11].text)

            # appending to dataframe
            if(is_premiere):
                new_df_row = {
                    'match_id':match_id,
                    'premiere_rating':rating,
                    'date':date,
                    'map':match_map,
                    'team_1':arr_t1,
                    'team_1_score':score_t1,
                    'team_2':arr_t2,
                    'team_2_score':score_t2,
                    'KDA':match_kda
                }

                df_matches_pmr = df_matches_pmr._append(new_df_row, ignore_index=True)

            else:
                new_df_row = {
                    'match_id':match_id,
                    'official_rank':rank,
                    'date':date,
                    'map':match_map,
                    'team_1':arr_t1,
                    'team_1_score':score_t1,
                    'team_2':arr_t2,
                    'team_2_score':score_t2,
                    'KDA':match_kda
                }

                df_matches_ofc = df_matches_ofc._append(new_df_row, ignore_index=True)

        print("reloading page. . .")
        time.sleep(5)
        driver.refresh() 

    except NoSuchWindowException:
        running = False
        print("Closing Session")
        time.sleep(5)
        break
        
    

print(df_matches_pmr.head())

driver.quit()

# saves result to df
df_matches_pmr.to_csv('data/matches_pmr_2.csv')
df_matches_ofc.to_csv('data/matches_ofc_2.csv')

print("Session Completed")