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
def get_play_by_play(driver, match_date):
	cols = ['Time','Team', 'Cap Number', 'Player Name', 'Action Detail', 'Score', 'Quarter']
	try:
		# Wait for play-by-play tab and click it
		wait = WebDriverWait(driver, 10)
		play_tab = wait.until(
			EC.element_to_be_clickable((By.LINK_TEXT, "Play-by-Play"))
		)
		
		driver.execute_script("arguments[0].click();", play_tab)
		time.sleep(2)
		
		# Wait for and expand all quarters
		try:
			buttons = wait.until(
				EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@class, 'arrow-down ng-star-inserted')]"))
			)
			print('Found quarter buttons')
			
			for button in buttons:
				try:
					driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
					time.sleep(0.5)
					driver.execute_script("arguments[0].click();", button)
					time.sleep(0.5)
				except Exception as e:
					print(f"Error expanding quarter: {str(e).split('Stacktrace:')[0]}")
					continue
		except Exception as e:
			print(f"Error finding quarter buttons: {str(e).split('Stacktrace:')[0]}")
			return
		
		# Get all quarter tables
		tables = driver.find_elements(By.XPATH, "//div[contains(@class, 'container ng-star-inserted')]")
		quarter = 1
		master = {}
		meta = pd.DataFrame(columns=cols)
		
		for table in tables:
			try:
				driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", table)
				print([i.get_attribute('innerHTML') for i in table.find_elements(By.TAG_NAME, 'h2')])
				master['Q' + str(quarter)] = []
				
				for i in table.find_elements(By.TAG_NAME, 'tr'):
					master['Q' + str(quarter)].append([j.get_attribute('innerHTML') for j in i.find_elements(By.TAG_NAME, 'td')])
				
				current = pd.DataFrame(master['Q' + str(quarter)], columns=cols[:-1])
				current.dropna(axis=0, how='all', inplace=True)
				current.loc[:, 'Quarter'] = 'Q' + str(quarter)
				current.loc[:, 'Score'] = current.loc[:, 'Score'].replace('', np.nan)
				meta = pd.concat([meta, current], ignore_index=True)
				current = None
				quarter += 1
				print(f"Processed quarter {quarter-1}")
				
			except Exception as e:
				print(f"Error processing quarter {quarter}: {str(e).split('Stacktrace:')[0]}")
				continue
		
		# Process the data
		meta = meta.ffill()
		meta.loc[:, 'Score'].fillna('0 - 0', inplace=True)
		
		# Export the data
		teams = meta['Team'].unique() if not meta.empty else []
		if len(teams) > 0:
			game_name = '_vs_'.join(['_'.join(i.replace('- MNL', '').strip().lower().split(' ')) for i in teams])
			print(f'Exporting data for {game_name}')
			# Clean the game name first, then use in f-string
			clean_name = re.sub(r"\W+", "", game_name)
			meta.to_excel(f'./{clean_name}_{match_date}.xlsx')
		else:
			print("No team data found, unable to export")
			
	except Exception as e:
		print(f"Error in play-by-play: {str(e).split('Stacktrace:')[0]}")

def get_games(url, driver_path):
	# Generating fake user agent
	options = Options()
	ua = UserAgent()
	user_agent = ua.random
	print(user_agent)

	options.add_argument(f'user-agent={user_agent}')
	driver = webdriver.Chrome(options=options)
	driver.maximize_window()
	driver.get(url)
	time.sleep(3)

	try:
		# Wait for page to load completely
		wait = WebDriverWait(driver, 5)
		
		# Find all play-by-play buttons using both selectors
		buttons = []
		try:
			buttons = wait.until(
				EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'play-btn ng-tns-c136-7')]"))
			)
			print("Found buttons using primary selector")
		except:
			try:
				buttons = wait.until(
					EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@class, 'button-container ng-star-inserted')]"))
				)
				print("Found buttons using secondary selector")
			except:
				print("No buttons found with either selector")
				return
		
		# Get initial count of Play-by-Play buttons
		play_by_play_count = len([b for b in buttons if 'Play-by' in b.text])
		print(f"Found {play_by_play_count} Play-by-Play buttons")
		
		# Process each game
		for game_num in range(play_by_play_count):
			try:
				print(f'Processing Game {game_num+1} of {play_by_play_count}')
				
				# Refresh button list after returning to main page
				try:
					buttons = wait.until(
						EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'play-btn ng-tns-c136-7')]"))
					)
				except:
					buttons = wait.until(
						EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@class, 'button-container ng-star-inserted')]"))
					)
				
				# Filter for Play-by-Play buttons
				play_by_play_buttons = [b for b in buttons if 'Play-by' in b.text]
				if not play_by_play_buttons:
					print("No Play-by-Play buttons found after refresh")
					continue
				
				button = play_by_play_buttons[game_num]
				
				# Get dates for reference
				dates = WebDriverWait(driver, 10).until(
					EC.presence_of_all_elements_located((
						By.XPATH, "//span[contains(@class,'date')]"
					))
				)
				# Convert date to YYYYMMDD format
				match_date = pd.to_datetime(dates[game_num].text).strftime("%Y%m%d")
				print(f"Processing game from {match_date}")
				
				# Scroll button into view and wait
				driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
				time.sleep(1)
				
				# Verify button is clickable
				wait.until(EC.element_to_be_clickable(button))
				
				# Click using JavaScript
				driver.execute_script("arguments[0].click();", button)
				time.sleep(2)
				
				# Process the play-by-play data
				get_play_by_play(driver, match_date)
				
				# Return to main page
				driver.get(url)
				time.sleep(2)
				
			except Exception as e:
				print(f"Error processing game {game_num+1}: {str(e).split('Stacktrace:')[0]}")
				continue
				
	except Exception as e:
		print(f"Error in get_games: {str(e).split('Stacktrace:')[0]}")
	finally:
		driver.quit()

def accept_cookies(driver):
	button = driver.find_element(by = By.XPATH, value = '//*[@id="cookie_action_close_header"]')
	driver.execute_script("arguments[0].click();", button)

if __name__ == "__main__":
	# List of links to pull data from
	lst = ['https://scores.6-8sports.com/unity/leagues/6fd5663d-68e9-4f1f-95cc-34378de6a868/tournaments/2336fb8d-794e-4a3d-9a3d-42ec500e8f13/teams/136cc53e-b67b-4da9-8d28-46072047201f/schedule']
	# Path for Chrome Driver
	driver_path = '/Users/ryanhurst/Desktop/chromedriver_mac64/chromedriver'
	
	for url in lst:
		try:
			get_games(url, driver_path)
		except Exception as e:
			print(f"Error in main loop: {str(e).split('Stacktrace:')[0]}")
			continue
