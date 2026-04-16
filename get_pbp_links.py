from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import time

URL = (
    "https://scores.6-8sports.com/unity/leagues/52ce65b3-afdd-4ac8-86f2-d4f3bdaa8439"
    "/tournaments/ed213b32-cc68-4469-a893-f80f1d652483"
    "/teams/d7b96d80-c15f-4934-8034-a7ea2d44ef6c/schedule"
)

options = Options()
ua = UserAgent()
options.add_argument(f"user-agent={ua.random}")

driver = webdriver.Chrome(options=options)
driver.maximize_window()
driver.get(URL)
time.sleep(4)

wait = WebDriverWait(driver, 15)

# Dismiss popup if present
try:
    popup = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "close-dialog-btn")))
    driver.execute_script("arguments[0].click();", popup)
    time.sleep(1)
except Exception:
    pass

# Wait for button-container elements to appear
containers = wait.until(
    EC.presence_of_all_elements_located(
        (By.XPATH, "//*[contains(@class, 'button-container ng-star-inserted')]")
    )
)
print(f"Found {len(containers)} button-container elements\n")

links = []
for i, el in enumerate(containers):
    # Check the element itself for href or routerLink
    for attr in ("href", "routerlink", "ng-reflect-router-link"):
        val = el.get_attribute(attr)
        if val:
            links.append(val)
            break

    # Check all descendant <a> tags
    for a in el.find_elements(By.TAG_NAME, "a"):
        href = a.get_attribute("href")
        if href:
            links.append(href)

    # Debug: print innerHTML of first container so we can see structure
    if i == 0:
        print("DEBUG — first container innerHTML:")
        print(el.get_attribute("innerHTML"))
        print()

driver.quit()

if links:
    print("\nPlay-by-play links:")
    for link in links:
        print(link)
else:
    print("No links found — check innerHTML above to diagnose.")
