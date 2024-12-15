from selenium import webdriver
from selenium.webdriver.common.by import By
import time

website = "https://csstats.gg"
path = "C:\Program Files (x86)\Devtools\chromedriver-win64\chromedriver.exe"

options = webdriver.ChromeOptions()
options.add_experimental_option(name="detach", value=True)

cService = webdriver.ChromeService(executable_path=path)
driver = webdriver.Chrome(options=options, service=cService)
driver.maximize_window()
driver.implicitly_wait(3)

# run
driver.get(website)

# all-matches button
all_matches_dropdown = driver.find_element(by=By.XPATH, value='//a[@class="dropdown-toggle ripple"]')
all_matches_dropdown.click()

all_matches_link = driver.find_element(by=By.XPATH, value='//a[@href="https://csstats.gg/match"]')
all_matches_link.click()

# cookies popup
shadow_parent = driver.find_element(By.CSS_SELECTOR, '#usercentrics-root')
outer = driver.execute_script('return arguments[0].shadowRoot', shadow_parent)
outer.find_element(By.CSS_SELECTOR, "button[data-testid='uc-accept-all-button']").click()

# refresh page
driver.refresh()

# quit
driver.quit()