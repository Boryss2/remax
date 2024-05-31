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

# Determine the ChromeDriver path based on the environment
chrome_driver_path = r"chromedriver" if os.name == 'nt' else "/home/runner/work/remax/remax/chromedriver"

# Initialize Chrome WebDriver with headless option
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Connect to SQLite database
conn = sqlite3.connect('listings.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS listings
             (title TEXT, PLN TEXT, EUR TEXT, listing_type TEXT, property_type TEXT, lot_size TEXT, image_src TEXT, link_to_offer TEXT)''')

# URL of the website
base_url = 'https://www.remax-polska.pl/PublicListingList.aspx?SelectedCountryID=47#mode=gallery&cur=PLN&sb=PriceDecreasing&page={}&sc=47&sid=56ec9c63-76d3-4376-86c3-e70a93dd7f63&oid=81029'

# Function to accept cookies
def accept_cookies():
    try:
        cookie_banner = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'CybotCookiebotDialog')))
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
        
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.ID, 'CybotCookiebotDialog')))
    except TimeoutException:
        pass

# Load the first page and accept cookies
driver.get(base_url.format(1))
accept_cookies()

# Wait for the listings to be rendered
time.sleep(20)  # Adjust the wait time as needed

# Scraping loop
page_number = 1
while True:
    url = base_url.format(page_number)
    driver.get(url)
    time.sleep(10)  # Adjust the wait time as needed
    
    # Find all gallery item containers
    listings = driver.find_elements(By.CLASS_NAME, 'gallery-item-container')

    # Loop through the listings and extract data
    for listing in listings:
        try:
            # Extract data from each listing
            title = listing.find_element(By.CLASS_NAME, 'gallery-title').text
            PLN = listing.find_element(By.CLASS_NAME, 'proplist_price').text
            EUR = listing.find_element(By.CLASS_NAME, 'proplist_price_alt').text
            listing_type = listing.find_element(By.CLASS_NAME, 'card-trans-type').text
            property_type = listing.find_element(By.CLASS_NAME, 'gallery-transtype').text
            lot_size = listing.find_element(By.CLASS_NAME, 'gallery-attr-item-value').text

            # Click on the listing to trigger the image load
            driver.execute_script("arguments[0].scrollIntoView();", listing)
            driver.execute_script("arguments[0].click();", listing)

            # Wait for the image to be fully loaded
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='gallery-photo']//img[@src!='']")))

            # Extract image source and link to offer
            image_src = listing.find_element(By.TAG_NAME, 'img').get_attribute('src')
            link_to_offer = listing.find_element(By.TAG_NAME, 'a').get_attribute('href')

            # Insert data into the database
            c.execute("INSERT INTO listings VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (title, PLN, EUR, listing_type, property_type, lot_size, image_src, link_to_offer))
        except NoSuchElementException:
            pass  # Handle missing elements
        
    # Commit changes to the database
    conn.commit()

    # Check if there's a next page
    try:
        next_button = driver.find_element(By.XPATH, "//li[@class='active']/following-sibling::li/a[@class='ajax-page-link']")
        next_button.click()
        page_number += 1
    except NoSuchElementException:
        break  # Break the loop if there's no next page

    # Wait for the listings to be rendered after clicking the next button
    time.sleep(10)  # Adjust the wait time as needed

# Close the browser and database connection
driver.quit()
conn.close()
