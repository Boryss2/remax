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
from webdriver_manager.chrome import ChromeDriverManager
import glob

# Function to get ChromeDriver path with fallback
def get_chromedriver_path():
    try:
        # Try webdriver-manager first
        driver_path = ChromeDriverManager().install()
        print(f"✓ webdriver-manager downloaded to: {driver_path}")
        
        # Check if the downloaded file is actually executable
        if os.path.exists(driver_path) and os.access(driver_path, os.X_OK):
            print(f"✓ Using webdriver-manager executable: {driver_path}")
            return driver_path
        else:
            print("⚠️ Downloaded file is not executable, searching for chromedriver binary...")
            
            # Get the base directory where webdriver-manager downloaded files
            base_dir = os.path.dirname(driver_path)
            print(f"Searching in directory: {base_dir}")
            
            # Search recursively for chromedriver executable
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if file == "chromedriver" or file.startswith("chromedriver"):
                        full_path = os.path.join(root, file)
                        print(f"Found potential chromedriver: {full_path}")
                        
                        # Check if it's executable and not a text file
                        if (os.access(full_path, os.X_OK) and 
                            not file.endswith('.txt') and 
                            not file.endswith('.md') and
                            not file.endswith('.notice') and
                            not file.endswith('.NOTICE') and
                            not 'THIRD_PARTY' in file and
                            not 'LICENSE' in file and
                            not 'README' in file):
                            
                            # Additional check: try to read first few bytes to verify it's a binary
                            try:
                                with open(full_path, 'rb') as f:
                                    first_bytes = f.read(4)
                                    # Check if it starts with ELF magic number (Linux binary)
                                    if first_bytes.startswith(b'\x7fELF'):
                                        print(f"✓ Found executable chromedriver (ELF binary): {full_path}")
                                        return full_path
                                    # Check if it starts with MZ (Windows PE binary)
                                    elif first_bytes.startswith(b'MZ'):
                                        print(f"✓ Found executable chromedriver (PE binary): {full_path}")
                                        return full_path
                                    else:
                                        print(f"⚠️ File is not a binary executable: {full_path}")
                                        continue
                            except Exception as e:
                                print(f"⚠️ Error reading file {full_path}: {e}")
                                continue
            
            # If no executable found in download directory, try parent directories
            current_dir = base_dir
            for _ in range(3):  # Go up 3 levels max
                parent_dir = os.path.dirname(current_dir)
                if parent_dir == current_dir:  # Reached root
                    break
                    
                print(f"Searching in parent directory: {parent_dir}")
                chromedriver_files = glob.glob(os.path.join(parent_dir, "chromedriver*"))
                
                for file in chromedriver_files:
                    if (os.access(file, os.X_OK) and 
                        not file.endswith('.txt') and 
                        not file.endswith('.md') and
                        not file.endswith('.notice') and
                        not file.endswith('.NOTICE') and
                        not 'THIRD_PARTY' in file and
                        not 'LICENSE' in file and
                        not 'README' in file):
                        
                        # Additional check: try to read first few bytes to verify it's a binary
                        try:
                            with open(file, 'rb') as f:
                                first_bytes = f.read(4)
                                # Check if it starts with ELF magic number (Linux binary)
                                if first_bytes.startswith(b'\x7fELF'):
                                    print(f"✓ Found executable chromedriver in parent dir (ELF binary): {file}")
                                    return file
                                # Check if it starts with MZ (Windows PE binary)
                                elif first_bytes.startswith(b'MZ'):
                                    print(f"✓ Found executable chromedriver in parent dir (PE binary): {file}")
                                    return file
                                else:
                                    print(f"⚠️ File in parent dir is not a binary executable: {file}")
                                    continue
                        except Exception as e:
                            print(f"⚠️ Error reading file {file}: {e}")
                            continue
                
                current_dir = parent_dir
            
            raise Exception("No executable chromedriver found in download directories")
            
    except Exception as e:
        print(f"⚠️ webdriver-manager search failed: {e}")
        # Fallback to system chromedriver
        system_paths = ["/usr/local/bin/chromedriver", "/usr/bin/chromedriver", "chromedriver"]
        for path in system_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                print(f"✓ Using system chromedriver: {path}")
                return path
        
        raise Exception("No chromedriver found in system paths")

# Get ChromeDriver path with fallback
chrome_driver_path = get_chromedriver_path()
service = Service(chrome_driver_path)

# Initialize Chrome WebDriver with headless option
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--remote-debugging-port=9222')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-plugins')
chrome_options.add_argument('--window-size=1920,1080')
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
