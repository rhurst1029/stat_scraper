from selenium import webdriver
from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeoutError
# from playwright.async_api import expect
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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
	time.sleep(2)  # Give the page time to load
	
	# Accepting and closing cookies popup
	try:
		accept_cookies(driver)
	except:
		print(f"Could not accept cookies for match {match} - continuing anyway")
	
	# Checking whether or not game has 'Finished'
	try:
		# Wait for the status element to be present and visible
		status_element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'status-label')]"))
		)
		# Get the text and ensure it's not empty
		game_status = status_element.text.strip().lower()
		print(f"Match {match} status: {game_status}")  # Debug print
		
		if not game_status:
			print(f'Match # {match} status is empty, waiting longer...')
			time.sleep(5)  # Wait longer
			game_status = status_element.text.strip().lower()
			
		if not game_status or game_status != 'finished':
			print(f'Match # {match} is not finished (with status: {game_status})... Continuing to next match!')
			return None
	except Exception as e:
		print(f"Error checking game status for match {match}: {e}")
		return None

	### Getting Team Logos (If we don't already have)
	try:
		get_team_logo(driver)
	except Exception as e:
		print('Couldnt get team Logos for ', match)
	
	###################################
	###### GETTING TO PLAYBYPLAY ######
	###################################
	try:
		WebDriverWait(driver, 10).until(
			EC.element_to_be_clickable((By.ID, "nav-playbyplay-tab"))
		).click()
	except Exception as e:
		print(f"Error clicking play-by-play tab for match {match}: {e}")
		return None
	
	# Initializing columns variable for DataFrame output
	cols = ['event_time', 'team_abrv', 'player_number', 'player_name', 'event_name', 'score', 'quarter']
	## Initializing Event Dict for each quarter
	meta = pd.DataFrame(columns = cols)
	### Getting href to each PBP quarter (including Shoot Outs)
	try:
		quarters = [i.get_attribute('href').split('/#')[-1] for i in driver.find_elements(By.XPATH, "//a[contains(@id, 'pills-pbp-')]")]
	except Exception as e:
		print(f"Error getting quarters for match {match}: {e}")
		return None
		
	# Iterating through each quarter
	for href in quarters:
		# initializing quarter dict
		quarter = href.split('-')[-1]

		# Opening quarter play by play
		try:
			WebDriverWait(driver, 10).until(
				EC.element_to_be_clickable((By.ID, f"pills-pbp-{quarter}-tab"))
			).click()
		except:
			continue

		# Print number of plays we are dealing with
		try:
			WebDriverWait(driver, 20).until(
				EC.visibility_of_element_located((By.ID, f"play-by-play-{quarter}"))
			)
			parent = driver.find_element(By.ID, f"play-by-play-{quarter}")
			div_elements = parent.find_elements(By.XPATH, "./div")
			# Initializing Col Names
			elem_lst = [div_element.text.split('\n') for div_element in div_elements if len(div_element.text.split('\n')) > 4]
			# Creating DF for current quarter data w/ ordered columns
			current = pd.DataFrame(elem_lst, columns = cols[:-1]).loc[::-1]
			
			# Creating Quarter Column for given quarter
			current.loc[:, 'quarter'] = quarter.upper()
			## Concatinating Current Quarters data with last quarters data
			meta = pd.concat([meta, current], ignore_index = True).fillna(method='ffill')
			meta.loc[:, 'score'].fillna('0 - 0', inplace = True)
			current = None
		except Exception as e:
			print(f"Error processing quarter {quarter} for match {match}: {e}")
			continue
	###################################
	###################################

	if meta.empty:
		print(f"No data found for match {match}")
		return None

	team_names = '_'.join(meta.team_abrv.unique())

	try:
		competition_name = driver.find_element(By.XPATH,"//body/div[1]/div[2]/div[1]/span[@tw-data='competitionName']").text
		match_details = driver.find_element(By.XPATH,"//*[@id='Wrapper']/div[2]/div[2]/div/div[1]").text
	except Exception as e:
		print(f"Error getting competition details for match {match}: {e}")
		return None

	#### Set League/Tournament, Game Date columns for given DF
	meta.loc[:, 'competition_name'] = competition_name
	meta.loc[:, 'match_details'] = match_details
	meta.loc[:, 'game_url'] = url

	### Getting final score
	try:
		home_team_goals = driver.find_element(By.XPATH, "//span[contains(@tw-data, 'hometeamgoals')]").text
		away_team_goals = driver.find_element(By.XPATH, "//span[contains(@tw-data, 'awayteamgoals')]").text
		meta.loc[:, 'final_score'] = home_team_goals + ' - '  + away_team_goals
	except Exception as e:
		print(f"Error getting final score for match {match}: {e}")
		meta.loc[:, 'final_score'] = 'N/A'

	### Getting quarter scores
	try:
		quarter_scores = [[i.get_attribute('tw-data'), i.text] for i in driver.find_elements(By.XPATH, "//div[contains(@class, 'part_score')]") if i.get_attribute('tw-data') is not None]
		for i in quarter_scores:
			meta.loc[:, f'{i[0]}'] = i[1]
	except Exception as e:
		print(f"Error getting quarter scores for match {match}: {e}")

	#### ADD Game Date to path
	try:
		# Create league directory if it doesn't exist
		if not os.path.exists(f'./{league}'):
			os.makedirs(f'./{league}')
		meta.to_excel(f'./{league}/{team_names}_{match}.xlsx', index = False)
		print(f"Successfully saved data for match {match}")
	except Exception as e:
		print(f"Error saving data for match {match}: {e}")

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
	# Generating fake user agent
	options = Options()
	ua = UserAgent()
	user_agent = ua.random
	options.add_argument(f'user-agent={user_agent}')
	options.add_argument("--headless=new")  # Updated headless mode syntax
	options.add_argument("--disable-gpu")
	options.add_argument("--no-sandbox")
	options.add_argument("--disable-dev-shm-usage")
	options.add_argument("--window-size=1920,1080")
	options.add_argument("--disable-blink-features=AutomationControlled")
	options.add_experimental_option("excludeSwitches", ["enable-automation"])
	options.add_experimental_option('useAutomationExtension', False)
	
	# Create a Service object with the system ChromeDriver
	service = Service()
	
	# Pass the service object to Chrome constructor
	driver = webdriver.Chrome(service=service, options=options)
	driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
	driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
	return driver

def get_links(url):
	
	driver.get(url)
	# Accepting and closing cookies popup
	accept_cookies(driver)

	try:
		# Navigate to the webpage

		# Find all elements with the 'tw-match-id' attribute
		elements = driver.find_elements(By.CSS_SELECTOR, "[tw-match-id]")

		# Extract and print the 'tw-match-id' values
		match_ids = [element.get_attribute("tw-match-id") for element in elements]
		return match_ids

	except:
		# Close the WebDriver
		driver.quit()
		driver.close

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
	url = "https://total-waterpolo.com/water-polo-champions-league-2024-25/"
	match_ids = get_links(url)
	# # ### Getting match links to pull
	# links = TWPConstructor().match_links

	# try: 
	# 	# Find all game links that contain 'play-by-play'
	# 	buttons = driver.find_elements(By.XPATH, "//a[contains(@class, 'match-link fad icon-chart-bar')]")
	# 	print(buttons)
	# except:
	# 	pass

	### Getting two gam
	links = [f'https://total-waterpolo.com/tw_match/{i}' for i in match_ids]
	print(links)
	for url in links:
		get_play_by_play(driver, url, 'Champions_League_2025')

	# # CLOSING DRIVER
	# driver.close()
	# driver.quit()
	
	# ### Getting the master df
	# ### Concatinating Champions League Games
	# files =	['./Champions_League_2024'
	# , './Champions_League_2223'
	# , './Champions_League']
	# # files = [i for i in glob.glob('./final_outputs/*') if os.path.isdir(i)]
	
	# main = pd.DataFrame() 
	# for file in files:
	# 	print('Getting data for: ', file.split('./')[-1])
	# 	if len([i for i in glob.glob(f'{file}/*')]) == 0:
	# 		print(f'No files contained in {file}. Deleting Directory')
	# 		os.rmdir(file)
	# 	### Concatinating all files in dir
	# 	for raw in glob.glob(f'{file}/*'):
	# 		match_id = raw.split('/')[-1].split('.xlsx')[0]
	# 		### Edge Cases
	# 		if 'null' in raw:
	# 			continue
	# 		new = pd.read_excel(raw)
	# 		new.loc[:, 'match_id'] = match_id
	# 		main = pd.concat([main, new], ignore_index = True)
	# 		new = None

	# main.to_excel('./Champions_League_Outputs.xlsx', index = False)
