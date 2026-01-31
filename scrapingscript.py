from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
import sqlite3
import time
from selenium.webdriver.chrome.options import Options
import os
import shutil
from webdriver_manager.chrome import ChromeDriverManager
import glob

# Use system chromedriver installed by GitHub Actions
chrome_driver_path = "/usr/local/bin/chromedriver"
print(f"✓ Using system chromedriver: {chrome_driver_path}")
service = Service(chrome_driver_path)


def resolve_chrome_binary():
    env_path = os.environ.get("CHROME_BIN")
    if env_path and os.path.isfile(env_path) and os.access(env_path, os.X_OK):
        return env_path

    candidates = [
        "/usr/local/bin/google-chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/local/bin/chrome-headless-shell",
        "/usr/local/bin/headless_shell",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]

    for candidate in candidates:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    for name in [
        "google-chrome",
        "google-chrome-stable",
        "chrome-headless-shell",
        "headless_shell",
        "chromium",
        "chromium-browser",
    ]:
        resolved = shutil.which(name)
        if resolved:
            return resolved

    raise FileNotFoundError(
        "Chrome binary not found. Set CHROME_BIN or install Chrome/Chromium."
    )
  
chrome_options = Options()
chrome_binary = resolve_chrome_binary()
print(f"✓ Using Chrome binary: {chrome_binary}")
chrome_options.binary_location = chrome_binary
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-plugins")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=service, options=chrome_options)


# Connect to SQLite database
conn = sqlite3.connect('listings.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS listings
             (title TEXT, PLN TEXT, EUR TEXT, listing_type TEXT, property_type TEXT, lot_size TEXT, image_src TEXT, link_to_offer TEXT)''')

# URL of the website
base_url = 'https://www.remax-polska.pl/listings?ListingClass=-1&TransactionTypeUID=-1&OfficeID=81029'

# Load the first page
page_number = 1
url = base_url.format(page_number)
driver.get(url)

# Function to accept cookies
def accept_cookies():
    try:
        cookie_banner = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, 'CybotCookiebotDialog')))
        accept_button = driver.find_element(By.ID, 'CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll')
        
        # Scroll to the accept button
        driver.execute_script("arguments[0].scrollIntoView();", accept_button)
        try:
            accept_button.click()
        except ElementClickInterceptedException:
            decline_button = driver.find_element(By.ID, 'CybotCookiebotDialogBodyLevelButtonLevelOptinDeclineAll')
            driver.execute_script("arguments[0].scrollIntoView();", decline_button)
            time.sleep(1)
            accept_button.click()
        
        WebDriverWait(driver, 30).until(EC.invisibility_of_element_located((By.ID, 'CybotCookiebotDialog')))
    except TimeoutException:
        pass

# Accept cookies
accept_cookies()

# Wait for the listings to be rendered
print("Waiting for listings to load...")
time.sleep(10)  # Reduced wait time for faster execution

# Scraping loop
page_count = 0
while True:
    page_count += 1
    print(f"Scraping page {page_count}...")
    
    # Find all listing card containers using new Material-UI structure
    listings = driver.find_elements(By.CSS_SELECTOR, '.MuiGrid-item .listing-card')
    print(f"Found {len(listings)} listings on page {page_count}")

    # Loop through the listings and extract data
    for i, listing in enumerate(listings):
        try:
            # Extract title from the link element
            title_element = listing.find_element(By.CSS_SELECTOR, '.listing-info')
            title = title_element.get_attribute('title')
            
            # Extract PLN price
            try:
                PLN_element = listing.find_element(By.CSS_SELECTOR, '.card-first-price')
                PLN = PLN_element.text
            except NoSuchElementException:
                PLN = "N/A"
            
            # Extract EUR price
            try:
                EUR_element = listing.find_element(By.CSS_SELECTOR, '.MuiTypography-body2 span')
                EUR = EUR_element.text
            except NoSuchElementException:
                EUR = "N/A"
            
            # Extract listing type (property type)
            try:
                listing_type_element = listing.find_element(By.CSS_SELECTOR, '.listing-type-address p:first-child')
                listing_type = listing_type_element.text
            except NoSuchElementException:
                listing_type = "N/A"
            
            # Extract property type (same as listing type in new structure)
            property_type = listing_type
            
            # Extract lot size (living area)
            try:
                lot_size_element = listing.find_element(By.CSS_SELECTOR, '[aria-label*="Pow. mieszkalna"] p')
                lot_size = lot_size_element.text + " m²"
            except NoSuchElementException:
                lot_size = "N/A"

            # Extract image source from the gallery
            try:
                # Find the first visible image in the gallery
                image_element = listing.find_element(By.CSS_SELECTOR, '.image-gallery-slide img[src]')
                image_src = image_element.get_attribute('src')
            except NoSuchElementException:
                image_src = "N/A"

            # Extract link to offer
            link_to_offer = title_element.get_attribute('href')

            # Insert data into the database
            c.execute("INSERT INTO listings VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (title, PLN, EUR, listing_type, property_type, lot_size, image_src, link_to_offer))
            print(f"  Processed listing {i+1}: {title}")
        except NoSuchElementException as e:
            print(f"  Skipped listing {i+1}: Missing element - {str(e)}")
            pass  # Handle missing elements
        
    # Commit changes to the database
    conn.commit()

    # Check if there's a next page using new Material-UI pagination
    try:
        # Look for the next page button with NavigateNextIcon
        next_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Go to next page"]')
        
        # Check if the button is disabled (no more pages)
        if next_button.get_attribute('disabled'):
            print("No more pages available. Scraping completed.")
            break
    except NoSuchElementException:
        print("No next page button found. Scraping completed.")
        break  # Break the loop if there's no next page

    print(f"Moving to page {page_count + 1}...")
    
    # Scroll to the next button to bring it into view
    driver.execute_script("arguments[0].scrollIntoView();", next_button)
    time.sleep(2)  # Brief wait for scroll

    # Click on the next page button
    driver.execute_script("arguments[0].click();", next_button)

    # Wait for the listings to be rendered after clicking
    time.sleep(10)  # Reduced wait time since we're not scrolling through images anymore

# Close the browser
driver.quit()

# Close the database connection
conn.close()

print(f"Scraping completed! Total pages processed: {page_count}")
print("Database updated with new listings.")
