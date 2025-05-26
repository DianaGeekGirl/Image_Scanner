import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import logging
import re
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
class ReverseImageSearch:
    def __init__(self):
        # Initialize Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
    def setup_driver(self):
        """Set up and return a Chrome WebDriver instance."""
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self.chrome_options)
            return driver
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {str(e)}")
            raise
    def search_similar_images(self, image_path):
        """Search for similar images using Google Images."""
        driver = None
        try:
            logger.info("Initializing WebDriver...")
            driver = self.setup_driver()
            logger.info("Navigating to Google Images...")
            driver.get('https://images.google.com')
            time.sleep(5)
            logger.info("Looking for image search button...")
            search_button = driver.find_element(By.CSS_SELECTOR, "[aria-label='Search by image']")
            driver.execute_script("arguments[0].click();", search_button)
            logger.info("Looking for file input...")
            file_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )
            abs_path = os.path.abspath(image_path)
            logger.info(f"Uploading image: {abs_path}")
            file_input.send_keys(abs_path)
            logger.info("Waiting for results to load...")
            time.sleep(7)
            try:
                logger.info("Looking for 'See exact matches' link...")
                exact_matches_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'See exact matches')]"))
                )
                exact_matches_button.click()
                logger.info("'See exact matches' clicked successfully")
                time.sleep(5)  # Allow time for the page to load exact matches
            except TimeoutException:
                logger.warning("'See exact matches' button not found or clickable")
            # Collect all website links from the "Exact matches" section
            website_links = self.collect_website_links(driver)
            # Return the collected website links
            return website_links
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []
        finally:
            if driver:
                try:
                    driver.quit()
                    logger.info("WebDriver closed successfully")
                except Exception as e:
                    logger.error(f"Error closing WebDriver: {str(e)}")
    def collect_website_links(self, driver):
        """Collect all website links from the Exact matches page, excluding URLs with certain keywords."""
        website_links = []
        time.sleep(5)  # Allow extra time for links to load

        # List of excluded keywords
        excluded_keywords = [
            'vidio', 'facebook', 'instagram', 'laodong.vn', 'kjhou.com', 'www.sanathaber.com',
            'www.liputan6.com', 'tiktok', 'twitter', 'watch.plex.tv', 'youtube', 'idntimes',
            'wattpad', 'liputan6', 'accounts.google', 'wiki', 'imdb', 'news', 'google'
        ]

        # Attempt to find all links in the exact matches section
        results = driver.find_elements(By.CSS_SELECTOR, 'a[href]')  # All anchor tags with href attributes
        logger.info(f"Found {len(results)} potential links in 'Exact matches' section")
        
        # Regular expression to identify IP-based URLs
        ip_pattern = re.compile(r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        
        for result in results:
            href = result.get_attribute('href')
            # Check if the link exists, starts with 'http' or matches an IP, and does not contain any excluded keywords
            if href and (href.startswith('http') or ip_pattern.match(href)):
                if not any(keyword in href for keyword in excluded_keywords):
                    website_links.append(href)
    
    # Remove duplicates
        website_links = list(set(website_links))
        logger.info(f"Collected {len(website_links)} website links after excluding specified keywords")
        return website_links

    def search(self, image_path):
        """Main method to perform reverse image search."""
        if not os.path.exists(image_path):
            logger.error("Image file not found")
            return "Error: Image file not found"
        print("Searching for similar images...")
        results = self.search_similar_images(image_path)
        if not results:
            return "No exact matches found"
        return results
def save_results_to_file(results, base_filename):
    """Save the results to a text file with a user-specified name."""
    # Generate a unique filename by appending a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_filename}_{timestamp}.txt"
    with open(filename, 'w') as f:
        for url in results:
            f.write(f"{url}\n")
    logger.info(f"Results saved to {filename}")
def main():
    try:
        searcher = ReverseImageSearch()
        image_path = input("Enter the path to your image: ")
        results = searcher.search(image_path)
        if isinstance(results, list):
            print("\nFound website links:")
            for idx, result in enumerate(results, 1):
                print(f"\n{idx}. URL: {result}")
            # Ask the user for a base filename to save the results
            base_filename = input("Enter a base filename for the results: ")
            save_results_to_file(results, base_filename)
        else:
            print(results)
    except Exception as e:
        logger.error(f"Main execution error: {str(e)}")
        print(f"An error occurred: {str(e)}")
if __name__ == "__main__":
    main()







