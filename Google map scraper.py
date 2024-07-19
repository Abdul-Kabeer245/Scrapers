# Import necessary libraries and modules
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd

def initialize_driver():
    """Initialize Chrome WebDriver with options."""
    # Set Chrome options to disable automation flags
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    # Clear all cookies to avoid any potential issues
    driver.delete_all_cookies()
    return driver

def get_link(driver):
    """Navigate to Google Maps."""
    # Open Google Maps in the browser
    driver.get('https://www.google.com/maps')
    # Wait for the page to load
    sleep(5)

def search_items(driver, location, item):
    """Search for items in a specific location on Google Maps."""
    # Find the search box element
    search = driver.find_element(By.ID, 'searchboxinput')
    # Create a search query with the item and location
    search_query = f"{item} in {location}"
    # Enter the search query and submit
    search.send_keys(search_query + Keys.RETURN)
    # Wait for the search results to load
    sleep(5)

def scroll_results(driver):
    """Scroll the search results to load more items."""
    # Find the scrollable div element containing the search results
    scrollable_div = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]')
    # Get the initial height of the scrollable div
    last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
    
    while True:
        # Scroll down to the bottom of the scrollable div
        driver.execute_script("arguments[0].scrollBy(0, arguments[0].scrollHeight);", scrollable_div)
        # Wait for new results to load
        sleep(3)
        # Get the new height of the scrollable div
        new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        # Break the loop if no new results have loaded
        if new_height == last_height:
            break
        # Update the last height
        last_height = new_height

def extract_links(driver):
    """Extract links to detailed pages for each search result."""
    # Get the page source of the search results page
    page_source = driver.page_source
    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')
    # Find all elements containing the links to detailed pages
    result_divs = soup.find_all('a', class_='hfpxzc')
    # Extract the href attribute from each element and store in a list
    links = [div['href'] for div in result_divs]
    return links

def scrape_data(driver, url):
    """Scrape the data from the location details page."""
    # Open the detailed page URL in the browser
    driver.get(url)
    # Wait for the page to load
    sleep(4)
    
    # Get the page source of the detailed page
    source = driver.page_source
    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(source, 'html.parser')
    
    # Extract the name of the location
    name_div = soup.find('h1', class_='DUwDvf lfPIob')
    name = name_div.get_text(separator=' ', strip=True) if name_div else 'Name not found'
    
    # Extract the location address
    location_div = soup.find('div', class_='Io6YTe fontBodyMedium kR99db')
    location = location_div.get_text(separator=' ', strip=True) if location_div else 'Location not found'
    
    # Extract the website link
    website_link_tag = soup.find('a', class_='CsEnBe')
    website_link = website_link_tag['href'] if website_link_tag else 'Website not found'
    
    # Extract the opening time
    opening_time_div = soup.find('div', class_='OqCZI fontBodyMedium WVXvdc')
    opening_time = opening_time_div.get_text(separator=' ', strip=True) if opening_time_div else 'Opening time not found'
    
    # Extract the phone number
    phone_divs = soup.find_all('button', class_='CsEnBe')
    phone_number = None
    for div in phone_divs:
        if 'Phone:' in div.get('aria-label'):
            phone_number = div.get('aria-label')[8:]
    phone_number = phone_number if phone_number else 'Phone number not found'
    
    # Extract the rating
    rating_div = soup.find('div', class_='F7nice')
    if rating_div:
        rating_span = rating_div.find('span')
        rating = rating_span.get_text(strip=True) if rating_span else 'Rating not found'
    else:
        rating = 'Rating not found'
    
    # Extract the number of reviews
    number_of_reviews = 'Number of reviews not found'
    reviews_span = rating_div.find_all('span') if rating_div else []
    for span in reviews_span:
        if 'reviews' in span.get('aria-label', ''):
            number_of_reviews = span.get_text(strip=True)[1:-1]
            break
    
    # Return the extracted data as a dictionary
    return {
        'name': name,
        'location': location,
        'website_link': website_link,
        'opening_time': opening_time,
        'phone': phone_number,
        'rating': rating,
        'number_of_reviews': number_of_reviews
    }

def main():
    # Prompt user for location and item to search for
    location = input("Enter the location to search in: ")
    item = input("Enter the item to search for: ")

    # Initialize the WebDriver
    driver = initialize_driver()
    # Navigate to Google Maps
    get_link(driver)
    # Search for the item in the specified location
    search_items(driver, location, item)
    # Scroll through the search results to load more items
    scroll_results(driver)
    # Extract links to detailed pages for each search result
    links = extract_links(driver)
    
    # Initialize a list to store the scraped data
    data = []
    # Scrape data from each detailed page
    for url in links:
        data.append(scrape_data(driver, url))
    
    # Quit the WebDriver
    driver.quit()

    # Save the scraped data to a CSV file
    df = pd.DataFrame(data)
    df.to_csv(f'{item}_in_{location}.csv', index=False)
    print(f'Successfully saved data to {item}_in_{location}.csv')

if __name__ == "__main__":
    main()
