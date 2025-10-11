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

# Try to use webdriver-manager for automatic ChromeDriver management
try:
    from webdriver_manager.chrome import ChromeDriverManager
    service = Service(ChromeDriverManager().install())
except ImportError:
    # Fallback to manual ChromeDriver path
    chrome_driver_path = r"chromedriver.exe" if os.name == 'nt' else "/usr/local/bin/chromedriver"
    service = Service(chrome_driver_path)

# Initialize Chrome WebDriver with headless option
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--remote-debugging-port=9222')
driver = webdriver.Chrome(service=service, options=chrome_options)

# Connect to SQLite database
conn = sqlite3.connect('listings.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS listings
             (title TEXT, PLN TEXT, EUR TEXT, listing_type TEXT, property_type TEXT, lot_size TEXT, image_src TEXT, link_to_offer TEXT)''')

# URL of the website
base_url = 'https://www.remax-polska.pl/PublicListingList.aspx?SelectedCountryID=47#mode=gallery&cur=PLN&sb=PriceDecreasing&page=1&sc=47&sid=56ec9c63-76d3-4376-86c3-e70a93dd7f63&oid=81029'

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
time.sleep(30)  # Adjust the wait time as needed

# Scraping loop
while True:
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
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@class='gallery-photo']//img[@src!='']")))

            # Extract image source and link to offer
            image_container = listing.find_element(By.CLASS_NAME, 'gallery-photo')
            image_elements = image_container.find_elements(By.TAG_NAME, 'img')

            # Initialize image source
            image_src = ""

            # Loop through image elements to find the correct source
            for img in image_elements:
                img_src = img.get_attribute('src')
                if 'video-icon.svg' not in img_src:
                    image_src = img_src
                    break

            # If no image source found yet, take the last image source
            if not image_src and image_elements:
                image_src = image_elements[-1].get_attribute('src')

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
    except NoSuchElementException:
        break  # Break the loop if there's no next page

    # Scroll to the next button to bring it into view
    driver.execute_script("arguments[0].scrollIntoView();", next_button)

    # Click on the next page button
    driver.execute_script("arguments[0].click();", next_button)

    # Wait for the listings to be rendered after scrolling
    time.sleep(30)  # Adjust the wait time as needed

# Close the browser
driver.quit()

# Close the database connection
conn.close()
