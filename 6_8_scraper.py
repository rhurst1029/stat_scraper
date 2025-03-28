from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
import numpy as np
import pandas as pd
import time
import os
import glob
# RUN IN TERMINAL IF OUT CHROMEDRIVER WONT RUN DUE TO UNVERIFIED DEVELOPER #
# xattr -d com.apple.quarantine chromedriver 
def get_play_by_play(url, driver_path):
	cols = ['Time','Team', 'Cap Number', 'Player Name', 'Action Detail', 'Score', 'Quarter']
	# Generating fake user agent
	options = Options()
	ua = UserAgent()
	user_agent = ua.random
	print(user_agent)

	options.add_argument(f'user-agent={user_agent}')
	driver = webdriver.Chrome(executable_path= driver_path,options=options)


	## Goal is to have URL set as an object of the MasterScraper class (Where this class is GameScraper)
	driver.get(url)
	# driver.maximize_window()
	time.sleep(1)
	try: 
		buttons = driver.find_elements(By.XPATH, "//*[contains(@class, 'arrow-down ng-star-inserted')]")
	except: 
		print(f"data NOT found")
		return
	for button in buttons:
		driver.execute_script("arguments[0].scrollIntoView();", button)
		# Call get_data inner func
		time.sleep(0.5)
		button.click()

	## STARTING DATA PULL ## 
	tables = driver.find_elements(By.XPATH, "//div[contains(@class, 'container ng-star-inserted')]")
	# tables = driver.find_elements_by_tag_name('azv-accordion')
	quarter = 1
	master = {}
	meta =  pd.DataFrame( columns = cols)
	for table in tables:
		# Scrolling table into view
		driver.execute_script("arguments[0].scrollIntoView();", table)
		print([i.get_attribute('innerHTML') for i in table.find_elements_by_tag_name('h2')])
		master['Q' + str(quarter)] = []
		# Getting rowwise data for each row in a quarters table
		for i in table.find_elements_by_tag_name('tr'):
			master['Q' + str(quarter)].append([j.get_attribute('innerHTML') for j in i.find_elements_by_tag_name('td') ])
		# Closing dropdown after opening
		# Creating DF for current quarter data
		current = pd.DataFrame(master['Q' + str(quarter)], columns = cols[:-1])
		current.dropna(axis = 0, how = 'all', inplace = True)
		# Creating Quarter Column for given quarter
		# current.loc[:, 'Quarter'] = table.find_element_by_tag_name('h2').get_attribute('innerHTML')
		current.loc[:, 'Quarter'] = 'Q' + str(quarter)

		# Setting blank scores to null for backfill
		current.loc[:, 'Score'] = current.loc[:, 'Score'].replace('', np.nan)
		## Concatinating Current Quarters data with last quarters data
		meta = pd.concat([meta, current], ignore_index = True)
		current = None
		quarter += 1
		print(master.keys())
	# Fowardfilling scores 
	meta.fillna(method='ffill', inplace = True)
	# Filling in initial score
	meta.loc[:, 'Score'].fillna('0 - 0', inplace = True)
	# Getting game name for export
	game_name = '_vs_'.join(['_'.join(i.replace('- MNL', '').strip().lower().split(' ')) for i in meta.Team.unique()])
	print(f'Exporting data for {game_name}')
	meta.to_excel(f'./{game_name}.xlsx')
	# CLOSING DRIVER
	driver.close()
	driver.quit()



def accept_cookies(driver):
	button = driver.find_element(by = By.XPATH, value = '//*[@id="cookie_action_close_header"]')
	driver.execute_script("arguments[0].click();", button)

if __name__ == "__main__":
	# List of links to pull data from
	lst = ['https://scores.6-8sports.com/unity/leagues/a1caaf09-835f-4896-8370-42cafe0ce58b/tournaments/bf8b4ae7-b151-429e-ad68-928e258aed0a/schedule/games/36529961-6233-4a64-8d68-4f7305aad55d/play-by-play']
	# Path for Chrome Driver
	driver_path = '/Users/ryanhurst/Desktop/chromedriver_mac64/chromedriver'
	for url in lst:
		get_play_by_play(url,driver_path)
