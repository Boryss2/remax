from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import sqlite3
import time

# Initialize Chrome WebDriver
chrome_driver_path = r"D:\app\visual studio\Remax\chromedriver-win64\chromedriver-win64\chromedriver.exe"
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

# Connect to SQLite database
conn = sqlite3.connect('listings.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS listings
             (title TEXT, PLN TEXT, EUR TEXT, listing_type TEXT, property_type TEXT, lot_size TEXT, image_src TEXT, link_to_offer TEXT)''')

# URL of the website
base_url = 'https://www.remax-polska.pl/PublicListingList.aspx?SelectedCountryID=47#mode=hybrid&cur=PLN&sb=PriceDecreasing&page={}&sc=47&lat=52.30396870443272&lng=19.874267578125004&zoom=7&nelat=54.36775852406841&nelng=23.994140625000004&swlat=50.240178884797025&swlng=15.754394531250002&sid=56ec9c63-76d3-4376-86c3-e70a93dd7f63&oid=81029'

# Load the first page
page_number = 1
url = base_url.format(page_number)
driver.get(url)

# Wait for the cookie consent banner to appear
cookie_banner = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'CybotCookiebotDialog')))

# Accept cookies if the banner is present
if cookie_banner:
    accept_button = driver.find_element(By.ID, 'CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll')
    accept_button.click()

# Wait for the cookie consent banner to disappear
try:
    WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.ID, 'CybotCookiebotDialog')))
except TimeoutException:
    pass

# Wait for the listings to be rendered
time.sleep(20)  # Adjust the wait time as needed

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
    except NoSuchElementException:
        break  # Break the loop if there's no next page

    # Scroll to the next button to bring it into view
    driver.execute_script("arguments[0].scrollIntoView();", next_button)

    # Click on the next page button
    driver.execute_script("arguments[0].click();", next_button)

    # Wait for the listings to be rendered after scrolling
    time.sleep(10)  # Adjust the wait time as needed

# Close the browser
driver.quit()

# Close the database connection
conn.close()
