"""
This Python program scrapes job postings from Indeed.com based on a user-specified keyword and number of pages. It then saves the extracted data (titles, organizations, locations, and links) into a CSV file named "Indeed Job Postings.csv".
"""

# importing important libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd


# Function to initialize the Chrome driver with disabled cache
def driverIntialization():
    # created a chromeOptions object to customize the chrome browser
    options = webdriver.ChromeOptions()
    # Disable the cache to ensure fresh data on each run
    options.add_argument("--disable-cache")
    # Create a new Chrome driver instance with the specified options
    driver = webdriver.Chrome(options=options)
    # Return the initialized driver
    return driver


# Function to scrape job postings from Indeed
def scrape(driver,keyword, numpages):
    # Initialize lists to store job information
    title = []
    organization = []
    location = []
    link=[]

    # Initialize the URL for Indeed
    url = 'https://www.indeed.com'
    # Navigate to the Indeed homepage
    driver.get(url)
    # Identify the search box by its ID
    search_box = driver.find_element(By.ID, 'text-input-what')
    # Enter the keyword and submit the form
    search_box.send_keys(keyword + Keys.RETURN)
    # Loop through each page
    for i in range(1, numpages+1):
        # Get the page source (html)
        source = driver.page_source
        # Create a BeautifulSoup object to parse the HTML
        soup = BeautifulSoup(source, 'html.parser')
        # Extract job information from the page by calling info function
        page_titles, page_organizations, page_locations, page_link = info(soup)
        # Extend the lists with the extracted information
        title.extend(page_titles)
        organization.extend(page_organizations)
        location.extend(page_locations)
        link.extend(page_link)
        # Click the next page button if it exists
        if not click_next_page(driver):
            time.sleep(100)
            break

    # Quit the driver
    driver.quit()
    # Return the extracted job information
    return title,organization, location, link


# Function to click the next page button
def click_next_page(driver):
    # Look for and click the close button if present
    try:
        time.sleep(5)
        # Look for and click the close button if present
        button = driver.find_element(By.CSS_SELECTOR, "button.css-yi9ndv.e8ju0x51")
        button.click()
        time.sleep(2)  # Allow time for the close action to complete
    except:
        pass  # If the close button is not found, continue to the next page

    try:
        wait = 5
        # Look for and click the next button
        next_button = driver.find_element(By.XPATH, '//a[@data-testid="pagination-page-next"]').click()
        time.sleep(5)  # Ensure the page loads completely before proceeding
        return True
    except:
        return False

def info(soup):
    # Initialize lists to store job information
    title = []
    organization = []
    location = []
    link = []
    # Extract job title information
    h2 = soup.find_all("a", class_="jcs-JobTitle css-jspxzf eu4oa1w0")
    if h2:
        for t in h2:
            spans = t.find("span")
            if spans:
                for span in spans:
                    title.append(span.text.strip())

    # Extract job title link     
    if h2:
        for a in h2:
            links = a.get('href')
            links = "https://pk.indeed.com" +links
            link.append(links)

    # Extract organization information
    organization_div = soup.find_all('div', class_ = 'css-1qv0295 e37uo190')
    if organization_div:
        for org in organization_div:
            spans = org.find("span")
            if spans:
                for span in spans:
                    if span.text and not span.text.isnumeric() and span.text != '':
                        organization.append(span.text.strip())
        

    # Extract location information
    location_div = soup.find_all('div', class_ = "css-1p0sjhy eu4oa1w0")
    if location_div:
       for loc in location_div:
            location.append(loc.text.strip())

    # Return extracted data
    return title, organization, location, link

if __name__ == "__main__":
    keyword = input("Enter keyword: ")
    num_pages = int(input("Enter number of pages: "))
    driver = driverIntialization()
    titles, organizatons, locations, links,  =  scrape(driver, keyword, num_pages)
    all_info_df = pd.DataFrame({"Title": titles,
        "Organization": organizatons,
        "Location": locations,
        "Job Link": links} )
    all_info_df.to_csv('Indeed Job Postings.csv', index=False)