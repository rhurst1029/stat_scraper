from selenium import webdriver
from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeoutError
# from playwright.async_api import expect
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
import requests
from requests_html import HTMLSession 
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import time
import os
import glob
import json
import sys
import time
import regex as re
from twp_constructor import TWPConstructor
import urllib.request
# RUN IN TERMINAL IF OUT CHROMEDRIVER WONT RUN DUE TO UNVERIFIED DEVELOPER #
# xattr -d com.apple.quarantine chromedriver 

def get_player_data(url, driver_path):
	"""
		Given a url to match data:
			i. Navigate to page
			ii. Navigate to tab containing stats
			iii. Identify 'download game stats' button 
			iv. Download game stats to local machine
	"""
	# Initializing driver with provided options
	driver = create_random_driver()
	# Loading the URL
	driver.get(url)
	# accepting cookies for URL
	accept_cookies(driver)
	# Getting to Playbyplay
	WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, f"nav-startlist-tab"))).click()
	time.sleep(5)
	# Finding, scrolling to, and clicking to download player stats
	content = driver.find_element(by = By.ID, value = "btn_download_stats")
	driver.execute_script("arguments[0].scrollIntoView();", content)
	driver.execute_script("arguments[0].click();", content)
	time.sleep(5)

	driver.close()
	driver.quit()

def get_play_by_play(driver, url, league):
	"""
		Given a URL to TWP match play-by-play data:
			i. Checks whether or not game has "Finished"
			ii. If game has "Not Started", then ignore URL
			iii. Call function to check and receive logo data
			iv. Get League/Tournament, Game Date, Team Names for Final Table

	"""

	## Goal is to have URL set as an object of the MasterScraper class (Where this class is GameScraper)
	match = url.split('/')[-1]
	driver.get(url)
	# Accepting and closing cookies popup
	accept_cookies(driver)
	# Checking whether or not game has 'Finished'
	while True:
		## Waiting for element to load since it must be fille with something if we obtained the link
		if len(driver.find_element(By.XPATH, "//span[contains(@class, 'status-label')]").text.lower()) == 0:
			time.sleep(3)
		else: 
			break
	game_status = driver.find_element(By.XPATH, "//span[contains(@class, 'status-label')]").text.lower()
	if game_status != 'finished':
		print(f'Match # {match} is not finished (with status {game_status})... Continuing to next match!')
		return None

	### Getting Team Logos (If we don't already have)
	try:
		get_team_logo(driver)
	except Exception as e:
		print('Couldnt get team Logos for ', match)
	
	###################################
	###### GETTING TO PLAYBYPLAY ######
	###################################
	driver.find_element_by_id("nav-playbyplay-tab").click()
	
	# Initializing columns variable for DataFrame output
	cols = ['event_time', 'team_abrv', 'player_number', 'player_name', 'event_name', 'score', 'quarter']
	## Initializing Event Dict for each quarter
	meta = pd.DataFrame(columns = cols)
	### Getting href to each PBP quarter (including Shoot Outs)
	quarters = [i.get_attribute('href').split('/#')[-1] for i in driver.find_elements(By.XPATH, "//a[contains(@id, 'pills-pbp-')]")]
	# Iterating through each quarter
	for href in quarters:
		# initializing quarter dict
		quarter = href.split('-')[-1]

		# Opening quarter play by play
		try:
			WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, f"pills-pbp-{quarter}-tab"))).click()
		except:
			continue

		# Print number of plays we are dealing with
		WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, f"play-by-play-{quarter}")))
		parent = driver.find_element(By.ID,f"play-by-play-{quarter}")
		div_elements = parent.find_elements_by_xpath("./div")
		# Initializing Col Names
		elem_lst = [div_element.text.split('\n') for div_element in div_elements if len (div_element.text.split('\n') ) > 4]
		# Creating DF for current quarter data w/ ordered columns
		current = pd.DataFrame(elem_lst, columns = cols[:-1]).loc[::-1]
		#### GETTING EVENT DETAILS
		## Opening up dropdowns
		# for div_element in  driver.find_elements(By.XPATH, "//div[contains(@class, 'tw_play_by_play p-1')]"):
		# 	driver.execute_script("arguments[0].scrollIntoView();", div_element)
		# 	print(div_element.get_attribute('tw-event-id'))
		# 	id = div_element.get_attribute('tw-event-id')
		# 	### Open dropdown
		# 	driver.execute_script(f"twa.utils.TooglePlayByPlayDetails('{id}')")

		# Creating Quarter Column for given quarter
		current.loc[:, 'quarter'] = quarter.upper()
		## Concatinating Current Quarters data with last quarters data
		meta = pd.concat([meta, current], ignore_index = True).fillna(method='ffill')
		meta.loc[:, 'score'].fillna('0 - 0', inplace = True)
		current = None
	###################################
	###################################

	team_names = '_'.join(meta.team_abrv.unique())

	competition_name = driver.find_element(By.XPATH,"//body/div[1]/div[2]/div[1]/span[@tw-data='competitionName']").text

	match_details = driver.find_element(By.XPATH,"//*[@id='Wrapper']/div[2]/div[2]/div/div[1]").text

	#### Set League/Tournament, Game Date columns for given DF
	meta.loc[:, 'competition_name'] = competition_name
	meta.loc[:, 'match_details'] = match_details
	meta.loc[:, 'game_url'] = url

	### Getting final score
	home_team_goals = driver.find_element(By.XPATH, "//span[contains(@tw-data, 'hometeamgoals')]").text
	away_team_goals = driver.find_element(By.XPATH, "//span[contains(@tw-data, 'awayteamgoals')]").text
	meta.loc[:, 'final_score'] = home_team_goals + ' - '  + away_team_goals


	### Getting quarter scores
	quarter_scores = [[i.get_attribute('tw-data'), i.text] for i in driver.find_elements(By.XPATH, "//div[contains(@class, 'part_score')]") if i.get_attribute('tw-data') is not None]
	
	for i in quarter_scores:
		meta.loc[:, f'{i[0]}'] = i[1]


	#### ADD Game Date to path
	meta.to_excel(f'./{league}/{team_names}_{match}.xlsx', index = False)

def get_team_logo(driver):
	"""
	This function will be called inside calls to get_play_by_play
		given a driver element object for game header:
			1. Finds the team names in the innerHTML
			2. Checks local repository for team image
			3. If team image doesnt exist: 
				i. save png to ./teams folder as __TEAM_ABRV__.PNG 
			4. If team image does exist
				i. Return none and exit function call
	"""
	# Checking if driver element exists, getting team names if it does

	# Checking if we already have team logo in local ./ teams folder
	if not os.path.exists('./teams'):
		# If it doesn't exist, make the directory
		os.mkdir('./teams')
	### Wait for images to be available
	WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@tw-data, 'hometeamlogo')]")))
	### Getting team names
	home_team_name = driver.find_element(By.XPATH, "//div[contains(@tw-data, 'hometeamname_short')]").text
	away_team_name = driver.find_element(By.XPATH, "//div[contains(@tw-data, 'awayteamname_short')]").text

	home_team_path = f'./teams/{home_team_name}.png'
	## Checking if logos already exist
	if not (os.path.exists(home_team_path)):
		### Getting and downloading logos if they exist
		home_team_logo = driver.find_element(By.XPATH, "//div[contains(@tw-data, 'hometeamlogo')]/img").get_attribute('src')
		# download the logos for home teams
		urllib.request.urlretrieve(home_team_logo, home_team_path)

	## Checking if logos already exist
	away_team_path = f'./teams/{away_team_name}.png'
	if not (os.path.exists(away_team_path)):
		### Performing the same on away team
		away_team_logo = driver.find_element(By.XPATH, "//div[contains(@tw-data, 'awayteamlogo')]/img").get_attribute('src')
		urllib.request.urlretrieve(away_team_logo, away_team_path)

def accept_cookies(driver):
	"""
		Identifies and accepts cookies upon opening url with new driver
	"""
	button = driver.find_element(by = By.XPATH, value = '//*[@id="cookie_action_close_header"]')
	driver.execute_script("arguments[0].click();", button)

def create_random_driver():
	"""
	Creates new fake user agent & returns driver 
	"""
	driver_path = '/Users/ryanhurst/Desktop/chromedriver_mac64/chromedriver'
	# Generating fake user agent
	options = Options()
	ua = UserAgent()
	user_agent = ua.random
	options.add_argument(f'user-agent={user_agent}')
	return webdriver.Chrome(executable_path= driver_path,options=options)

if __name__ == "__main__":



### THings to add:
# Improved logic for getting logos
# Improved shootout logic: if PSO in quarters then SHOOTOUT (DONE)
# Creation of final_score field (DONE)
# Creation of quarter_end_score field (DONE)
### Finally: Getting event details, then images (LOGIC ALMOST THERE)


	# ### Initializing driver
	# # Create initial driver for getting current game's data
	driver = create_random_driver()

	# # ### Getting match links to pull
	# links = TWPConstructor().match_links

	# #### JUST GETTING CHAMPIONS LEAGUE RN, DELETE LATER
	# links = {k:v for (k,v) in links.items() if 'Champions League' in k}
	# ### Getting data fore matches
	# for league, match_urls in links.items():
	# 	league = re.sub('[^a-zA-Z0-9 \n\.]', '', league)
	# 	league = league.replace('/', '_').replace(' ', '_')

	# 	print(f"Running {len(match_urls)} for {league}")
	# 	if ('test' in league.lower()) or (league.strip() == ""):
	# 		print(league.lower(), "SKIPPING", '\n'*2)
	# 		continue
	# 	else:
	# 		### Making directory for games to be saved to
	# 		os.mkdir(f'./{league}')
	# 	### Run on all links
	# 	for url in match_urls:
	# 		try:
	# 			get_play_by_play(driver, url, league)
	# 		except Exception as e:
	# 			print(f"failed for {url} with error {e}")
	# 			continue
	


	### Getting two games
	links = ['https://total-waterpolo.com/tw_match/9055', 'https://total-waterpolo.com/tw_match/9056']
	for url in links:
		get_play_by_play(driver, url, 'Champions_League_2024')

	# CLOSING DRIVER
	driver.close()
	driver.quit()

	### Getting the master df
	### Concatinating Champions League Games
	files =	['./Champions_League_2024'
	, './Champions_League_2223'
	, './Champions_League']
	# files = [i for i in glob.glob('./final_outputs/*') if os.path.isdir(i)]
	
	main = pd.DataFrame() 
	for file in files:
		print('Getting data for: ', file.split('./')[-1])
		if len([i for i in glob.glob(f'{file}/*')]) == 0:
			print(f'No files contained in {file}. Deleting Directory')
			os.rmdir(file)
		### Concatinating all files in dir
		for raw in glob.glob(f'{file}/*'):
			match_id = raw.split('/')[-1].split('.xlsx')[0]
			### Edge Cases
			if 'null' in raw:
				continue
			new = pd.read_excel(raw)
			new.loc[:, 'match_id'] = match_id
			main = pd.concat([main, new], ignore_index = True)
			new = None

	main.to_excel('./Champions_League_Outputs.xlsx', index = False)
