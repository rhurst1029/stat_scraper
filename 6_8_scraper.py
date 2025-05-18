from selenium import webdriver
from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeoutError
# from playwright.async_api import expect
from selenium.webdriver.chrome.service import Service
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

# RUN IN TERMINAL IF OUT CHROMEDRIVER WONT RUN DUE TO UNVERIFIED DEVELOPER #
# xattr -d com.apple.quarantine chromedriver 
def get_play_by_play(driver, button):
	cols = ['Time','Team', 'Cap Number', 'Player Name', 'Action Detail', 'Score', 'Quarter']
	
	button.click()
	driver.maximize_window()
	time.sleep(3)
	
	
	play_tab = WebDriverWait(driver, 10).until(
		EC.element_to_be_clickable((By.LINK_TEXT, "Play-by-Play"))
	)
	play_tab.click()
	# driver.execute_script("arguments[0].click();", pbp)
	
	try: 
		# Wait for play-by-play content to load
		WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'arrow-down ng-star-inserted')]")))
		buttons = driver.find_elements(By.XPATH, "//*[contains(@class, 'arrow-down ng-star-inserted')]")
	except: 
		print(f"Play-by-play data NOT found")
		return
	
	for button in buttons:
		driver.execute_script("arguments[0].scrollIntoView();", button)
		time.sleep(0.5)
		button.click()

	## STARTING DATA PULL ## 
	tables = driver.find_elements(By.XPATH, "//div[contains(@class, 'container ng-star-inserted')]")
	quarter = 1
	master = {}
	meta = pd.DataFrame(columns=cols)
	
	for table in tables:
		# Scrolling table into view
		driver.execute_script("arguments[0].scrollIntoView();", table)
		print([i.get_attribute('innerHTML') for i in table.find_elements(By.TAG_NAME, 'h2')])
		master['Q' + str(quarter)] = []
		
		# Getting rowwise data for each row in a quarters table
		for i in table.find_elements(By.TAG_NAME, 'tr'):
			master['Q' + str(quarter)].append([j.get_attribute('innerHTML') for j in i.find_elements(By.TAG_NAME, 'td')])
		
		# Creating DF for current quarter data
		current = pd.DataFrame(master['Q' + str(quarter)], columns=cols[:-1])
		current.dropna(axis=0, how='all', inplace=True)
		
		# Creating Quarter Column for given quarter
		current.loc[:, 'Quarter'] = 'Q' + str(quarter)

		# Setting blank scores to null for backfill
		current.loc[:, 'Score'] = current.loc[:, 'Score'].replace('', np.nan)
		
		## Concatenating Current Quarters data with previous quarters data
		meta = pd.concat([meta, current], ignore_index=True)
		current = None
		quarter += 1
		print(master.keys())
	
	# Forward filling scores 
	meta = meta.ffill()  # Updated method to avoid future warning
	# Filling in initial score
	meta.loc[:, 'Score'].fillna('0 - 0', inplace=True)
	
	# Getting game name for export - handle empty case
	teams = meta['Team'].unique() if not meta.empty else []
	if len(teams) > 0:
		game_name = '_vs_'.join(['_'.join(i.replace('- MNL', '').strip().lower().split(' ')) for i in teams])
		print(f'Exporting data for {game_name}')
		meta.to_excel(f'./{game_name}.xlsx')
	else:
		print("No team data found, unable to export")
	 # Return to main page after each game
def get_games(url, driver_path):
	# Generating fake user agent
	options = Options()
	ua = UserAgent()
	user_agent = ua.random
	print(user_agent)

	options.add_argument(f'user-agent={user_agent}')
	driver = webdriver.Chrome(options=options)
	driver.get(url)
	time.sleep(3)
	
	try: 
		# Find all game links that contain 'play-by-play'
		buttons = driver.find_elements(By.XPATH, "//a[contains(@class, 'play-btn ng-tns-c136-7')]")
		if not buttons:
			# Try alternative selector for game buttons with proper completion
			wait = WebDriverWait(driver, 15)
			wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@class, 'button-container ng-star-inserted')]")))
			buttons = driver.find_elements(By.XPATH, "//*[contains(@class, 'button-container ng-star-inserted')]")
		
		print(f"Found {len(buttons)} play-by-play buttons")
		
		if buttons:
			for button in buttons:
				get_play_by_play(driver, button)
				driver.get(url)  # Return to main page after each game
				time.sleep(2)  # Wait before processing next game
		
		driver.quit()
		return buttons
		
	except Exception as e: 
		print(f"Error finding buttons: {e}")
		driver.quit()
		return []

def accept_cookies(driver):
	button = driver.find_element(by = By.XPATH, value = '//*[@id="cookie_action_close_header"]')
	driver.execute_script("arguments[0].click();", button)

if __name__ == "__main__":
	# List of links to pull data from
	lst = ['https://scores.6-8sports.com/unity/leagues/6fd5663d-68e9-4f1f-95cc-34378de6a868/tournaments/2336fb8d-794e-4a3d-9a3d-42ec500e8f13/teams/136cc53e-b67b-4da9-8d28-46072047201f/schedule']
	# Path for Chrome Driver
	driver_path = '/Users/ryanhurst/Desktop/chromedriver_mac64/chromedriver'
	for url in lst:
		game_urls = get_games(url, driver_path)
		print(game_urls)
		for game in game_urls:
			get_play_by_play(url,driver_path)
