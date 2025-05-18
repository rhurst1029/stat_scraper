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



class TWPConstructor:
	"""
		Class that essentially decides whether to check TWP for all links, or build new set of links
		Default pulls links from existing json file
	"""
	def __init__(self, get_fresh_links = False):
		self.get_fresh_links = get_fresh_links
		self.match_links = self.create_link_object()


	def create_link_object(self):
		'''
			If get_fresh_links = True:
				i. Check if existing dict of links exists
				ii. Update existing, or create new dict if it doesn't exist
		'''
		if self.get_fresh_links == False:
			# Opening JSON file
			with open('match_links.json') as json_file:
				data = json.load(json_file)
			return data
		else:
			### First, check if match_links.json exists
			if './match_links.json' in [i for i in glob.glob('./*.json')]:
				with open('match_links.json') as json_file:
					data = json.load(json_file)
				### Create list of existing match #s if the match_links obj exists
				current_keys = []
				for matches in data.values():
					[current_keys.append(int(j.split('/')[-1])) for j in matches]
				### Calling function with existing values to collect new values
				return create_final_link_file(current_keys, data)
			else:
				### Returning fresh link dict object
				return create_final_link_file()


	def create_final_link_file(self, current_keys = [], data = None):
		### If data is passed, use existing data as final
		if data:
			final = data
		# Otherwise, initialize new dict
		else:
			final = {}
		## Now, collect all links
		for n in range(1,150): 
			for j in range((n -1) * 100,(n * 100) ,10):
				### If match ID already exists, continue to next match
				if j in current_keys:
					continue
				output = get_all_links(j,j+10,1)
				### Creating or appending key value pairs to final
				for league, match_links in output.items():
					if league in final.keys():
						[final[league].append(i) for i in match_links if i not in final[league].values()]
					else:
						final[league] = []
						[final[league].append(i) for i in match_links if i not in final[league].values()]
		[print('League: ', k, '# Games: ', len(v)) for k,v in final.items()]
		### Dumping outputs to json file 
		with open(f'match_links.json', 'w') as out:
			json.dump(final, out)
			out.close()
		return final

	def get_all_links(self, start, stop, step):
		"""
			Given start, stop, step of game IDs:
				i. Searches through given range of game IDs
				ii. For each game ID, checks URL for that ID to see if a match exists for the given url gameID
				iii. Creates output json from dict of League/Tournaments as keys and valid games URLs as values
		"""
		with sync_playwright() as playwright_agent:
			browser = playwright_agent.chromium.launch()
			# Generating fake user agent
			options = Options()
			ua = UserAgent()
			user_agent = ua.random
			context = browser.new_context(user_agent = user_agent)
			match_map = {}
			# Exploring all links on site to get complete ones mapped to competition
			# print('Running through range',start, ' ', stop)
			for i in range(start, stop, step):
				
				link = f"https://total-waterpolo.com/tw_match/{str(i)}"

				league, match_link = check_game_url(link, context)
				# Checking for null response
				if league is None:
					continue
				elif league in match_map.keys():
					match_map[league].append(match_link)
				else:
					match_map[league] = []
					match_map[league].append(match_link)
			return match_map

	def check_game_url(self, url, context):
		"""
			Given a URL to a potential match for corresponding match ID:
				i. Accept cookies if they exist on the given page
				ii. Check if the given URL exists for a given competition/tournament name
				iii. Double check competition name if blank
			Returns competition name and given URL for use in output to get_all_links
		"""
		
		page = context.new_page()
		
		try:
			page.goto(url)
			
			expect(page.locator('//body/div[1]/div[2]/div[1]/span[@tw-data="competitionName"]')).to_be_visible(timeout = 2500)
			locator = page.locator('//body/div[1]/div[2]/div[1]/span[@tw-data="competitionName"]')
			### Waiting for it to return anything other than blanks
			expect(locator).not_to_have_text('', timeout=100)
		except Exception as e:
			print(e)
			return None, url
		return locator.inner_html().strip(), url