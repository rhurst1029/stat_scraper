from selenium import webdriver
from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeoutError
# from playwright.async_api import expect
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
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
def get_play_by_play(url, match_date):
	# Generating fake user agent
	options = Options()
	ua = UserAgent()
	user_agent = ua.random

	options.add_argument(f'user-agent={user_agent}')
	driver = webdriver.Chrome(options=options)
	driver.maximize_window()
	driver.get(url)
	time.sleep(3)
	
	cols = ['Time','Team', 'Cap Number', 'Player Name', 'Action Detail', 'Score', 'Quarter']
	try:
		
		wait = WebDriverWait(driver, 2)
		popup = wait.until(
			EC.element_to_be_clickable((By.CLASS_NAME, "close-dialog-btn"))
		)
		
		driver.execute_script("arguments[0].click();", popup)
		time.sleep(2)
	except Exception as e:
		print(f"No popup found: {str(e).split('Stacktrace:')[0]}")
	try:
		# Wait for play-by-play tab and click it
		wait = WebDriverWait(driver, 10)
		play_tab = wait.until(
			EC.element_to_be_clickable((By.LINK_TEXT, "Play-by-Play"))
		)
		
		driver.execute_script("arguments[0].click();", play_tab)
		time.sleep(2)
		
		quarter = 0
		master = {}
		meta = pd.DataFrame(columns=cols)
		# Get all quarter buttons
		try:
			buttons = wait.until(
				EC.presence_of_all_elements_located((By.CLASS_NAME, "ng-star-inserted"))
			)
			print('Found quarter buttons')
			# print([b.text for b in buttons])
			buttons = [b for b in buttons if b.text in ['1st Quarter', '2nd Quarter', '3rd Quarter', '4th Quarter']]
			for button in buttons:  # Limit to first 4 quarters
				# print(len(buttons),quarter, button.text)
				quarter += 1
				try:
					driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
					time.sleep(0.5)
					driver.execute_script("arguments[0].click();", button)
					time.sleep(0.5)
				except Exception as e:
					print(f"Error Opening quarter: {str(e).split('Stacktrace:')[0]}")
					continue
		
				# # Get quarter play-by-play table
				try:
					table = wait.until(
						EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'table acc-table ng-star-inserted')]"))
					)
				except Exception as e:
					print(f"Error table rows: {str(e).split('Stacktrace:')[0]}")
					continue
				
				# driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
				master['Q' + str(quarter)] = []
				
				for i in table.find_elements(By.TAG_NAME, 'tr'):
					master['Q' + str(quarter)].append([j.get_attribute('innerHTML') for j in i.find_elements(By.TAG_NAME, 'td')])


				### Creating temp df 'current' to concatinate each quarter's data with 'Master'
				current = pd.DataFrame(master['Q' + str(quarter)], columns=cols[:-1])
				current.dropna(axis=0, how='all', inplace=True)
				current.loc[:, 'Quarter'] = 'Q' + str(quarter)
				current.loc[:, 'Score'] = current.loc[:, 'Score'].replace('', np.nan)
				meta = pd.concat([meta, current], ignore_index=True)
				current = None
				print(f"Processed quarter {quarter}")
				
		except Exception as e:
			print(f"Error processing quarter {quarter}: {str(e).split('Stacktrace:')[0]}")
			return
		
		### Removing quarter start and end dup rows
		meta = meta[(~meta['Time'].str.contains('finished</'))\
			  & (~meta['Time'].str.contains('started</'))]
		# Process the data
		meta = meta.ffill()
		meta.loc[:, 'Score'].fillna('0 - 0', inplace=True)
		### parsing out team names ##
		
		### Cleaning out first and last blank row 
		meta.dropna(axis=0, how='any', inplace=True)
		meta['Team'] = [i.split('="">')[-1].split('</span')[0] for i in meta['Team'].values]
		# Export the data
		teams = meta['Team'].unique() if not meta.empty else []
		if len(teams) > 0:
			team_names = [i.replace(' NL ', '').replace('/', '_').strip().split(' ') for i in teams]
			game_name = '_VS_'.join(['_'.join(i) for i in team_names])
			## Setting name of the game in the dataframe for export
			meta['Game'] = game_name.replace('_', ' ')
			print(f'Exporting data for {game_name}')
			# # Clean the game name first, then use in f-string
			clean_name = re.sub(r"\W+", "", game_name)
			meta.to_excel(f'./{clean_name.replace("-", "").lower()}_{match_date}.xlsx', index=False)
		else:
			print("No team data found, unable to export")
			
	except Exception as e:
		print(f"Error in play-by-play: {str(e).split('Stacktrace:')[0]}")
		driver.quit()
	finally:
		print("Closing browser...")
		driver.quit()

def get_games(url, driver_path):
	# Generating fake user agent
	options = Options()
	ua = UserAgent()
	user_agent = ua.random

	options.add_argument(f'user-agent={user_agent}')
	driver = webdriver.Chrome(options=options)
	driver.maximize_window()
	driver.get(url)
	time.sleep(3)

	def get_date_selector():
		print("Looking for date selector...")
		wait = WebDriverWait(driver, 15)
		date_selector = wait.until(EC.presence_of_element_located((
			By.CSS_SELECTOR,
			"azv-date-selector div"
		)))
		print("Found date selector successfully")
		return date_selector

	try:
		date_selector = get_date_selector()
		
		# Process each highlighted day
		while True:
			print("\nLooking for highlighted days...")
			# Find current set of highlighted days
			days = date_selector.find_elements(
				By.CSS_SELECTOR,
				"div.week-day.highlighted span.day"
			)
			if not days:
				print("No more highlighted days found, breaking loop")
				break

			print(f"Found {len(days)} highlighted days")

			for idx in range(len(days)):
				try:
					print(f"\nProcessing day index {idx}")
					# Re-locate days to avoid stale elements
					days = date_selector.find_elements(
						By.CSS_SELECTOR,
						"div.week-day.highlighted span.day"
					)
					btn = days[idx]
					print(f"Processing date: {btn.text}")

					# Scroll into view and click
					print("Scrolling to date button...")
					driver.execute_script("arguments[0].scrollIntoView(true);", btn)
					print("Clicking date button...")
					driver.execute_script("arguments[0].click();", btn)
					time.sleep(2)  # Wait for schedule to load
					print("Schedule should be loaded now")

					# Wait for page to load completely
					wait = WebDriverWait(driver, 5)
					
					# Find all play-by-play buttons using both selectors
					buttons = []
					try:
						print("Trying primary selector for buttons...")
						buttons = wait.until(
							EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'play-btn ng-tns-c136-7')]"))
						)
						print("Found buttons using primary selector")
					except:
						try:
							print("Trying secondary selector for buttons...")
							buttons = wait.until(
								EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@class, 'button-container ng-star-inserted')]"))
							)
							print("Found buttons using secondary selector")
						except:
							print("No buttons found with either selector")
							continue
					
					# Get initial count of Play-by-Play buttons
					play_by_play_count = len([b for b in buttons if 'Play-by' in b.text])
					print(f"Found {play_by_play_count} Play-by-Play buttons")
					
					# Process each game for this date
					for game_num in range(play_by_play_count):
						max_retries = 3
						retry_count = 0
						
						while retry_count < max_retries:
							try:
								print(f'\nProcessing Game {game_num+1} of {play_by_play_count} (Attempt {retry_count + 1})')
								
								# Refresh button list
								print("Refreshing button list...")
								try:
									buttons = wait.until(
										EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'play-btn ng-tns-c136-7')]"))
									)
									print("Refreshed buttons using primary selector")
								except:
									buttons = wait.until(
										EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@class, 'button-container ng-star-inserted')]"))
									)
									print("Refreshed buttons using secondary selector")
								
								# Filter for Play-by-Play buttons
								play_by_play_buttons = [b for b in buttons if 'Play-by' in b.text]
								if not play_by_play_buttons:
									print("No Play-by-Play buttons found after refresh")
									break
								
								button = play_by_play_buttons[game_num]
								
								# Get match date
								try:
									match_date = pd.to_datetime(btn.text).strftime("%Y%m%d")
								except:
									match_date = pd.to_datetime('today').strftime("%Y%m%d")
								print(f"Processing game from {match_date}")
								
								# Scroll button into view and wait
								print("Scrolling to game button...")
								driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
								time.sleep(1)
								
								# Verify button is clickable
								print("Verifying button is clickable...")
								wait.until(EC.element_to_be_clickable(button))
								
								# Click using JavaScript
								print("Clicking game button...")
								driver.execute_script("arguments[0].click();", button)
								time.sleep(2)
								
								# Process the play-by-play data
								print("Starting play-by-play processing...")
								get_play_by_play(driver, match_date)
								
								# Return to schedule page
								print("Returning to schedule page...")
								driver.get(url)
								time.sleep(2)
								
								# Re-establish context after page refresh
								print("Re-establishing context after page refresh...")
								date_selector = get_date_selector()
								print("Successfully returned to schedule page")
								break  # Success, exit retry loop
								
							except Exception as e:
								print(f"Error processing game {game_num+1}: {str(e).split('Stacktrace:')[0]}")
								retry_count += 1
								if retry_count < max_retries:
									print(f"Retrying... (Attempt {retry_count + 1} of {max_retries})")
									# Return to main page and re-establish context
									driver.get(url)
									time.sleep(2)
									date_selector = get_date_selector()
								else:
									print("Max retries reached, moving to next game")
									break

				except Exception as e:
					print(f"Error processing date: {str(e).split('Stacktrace:')[0]}")
					print("Attempting to continue with next date...")
					continue

	except Exception as e:
		print(f"Error in get_games: {str(e).split('Stacktrace:')[0]}")
	finally:
		print("Closing browser...")
		driver.quit()

def accept_cookies(driver):
	button = driver.find_element(by = By.XPATH, value = '//*[@id="cookie_action_close_header"]')
	driver.execute_script("arguments[0].click();", button)

if __name__ == "__main__":
	# List of links to pull data from
	# lst = ['https://scores.6-8sports.com/unity/leagues/6fd5663d-68e9-4f1f-95cc-34378de6a868/tournaments/2336fb8d-794e-4a3d-9a3d-42ec500e8f13/teams/136cc53e-b67b-4da9-8d28-46072047201f/schedule']
	# lst = ['https://scores.6-8sports.com/unity/leagues/ed3c47a9-d55f-4505-b7be-82dcbe1c693b/conferences/8df7f8c1-884a-47d3-961f-ceb69c3d859a/schedule/games/86b1d19c-eeef-4143-a8db-24408b644371/play-by-play?is_shared=True'
	# 	, 'https://scores.6-8sports.com/unity/leagues/ed3c47a9-d55f-4505-b7be-82dcbe1c693b/conferences/8df7f8c1-884a-47d3-961f-ceb69c3d859a/schedule/games/9cf059c0-a9dd-475b-a692-aa26fa8e41fe/play-by-play'
	# 	, 'https://scores.6-8sports.com/unity/leagues/ed3c47a9-d55f-4505-b7be-82dcbe1c693b/conferences/8df7f8c1-884a-47d3-961f-ceb69c3d859a/schedule/games/49ef5812-55e5-4ae0-9c36-abc8c5d3cb67/play-by-play']
	lst =[ 'https://scores.6-8sports.com/scoreboard/games/a4349f7a-1cac-40c9-94de-c77ef46f8f81/play-by-play']
	# Path for Chrome Driver
	driver_path = '/Users/ryanhurst/Desktop/chromedriver_mac64/chromedriver'
	
	for url in lst:
		try:
			# get_games(url, driver_path)
			match_date = pd.to_datetime('today').strftime("%Y%m%d")
			get_play_by_play(url, match_date)
		except Exception as e:
			print(f"Error in main loop: {str(e).split('Stacktrace:')[0]}")
			continue
