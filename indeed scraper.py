"""
This Python program scrapes job postings from Indeed.com based on a user-specified keyword and number of pages. It then saves the extracted data (titles, organizations, locations, salary, description and links) into a CSV file named "Indeed Job Postings.csv".
"""

# importing important libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import random

#This function generates a random delay between 1 and 10 seconds
def random_delay():
    time.sleep(random.randint(1, 10))


# Function to initialize the Chrome driver with disabled cache
def driverIntialization():
    # created a chromeOptions object to customize the chrome browser
    options = webdriver.ChromeOptions()
    # Disable the cache to ensure fresh data on each run
    options.add_argument("--disable-cache")
    options.add_argument("--start-maximized")
    # Create a new Chrome driver instance with the specified options
    driver = webdriver.Chrome(options=options)
    # Return the initialized driver
    return driver


# Function to click the next page button
def click_next_page(driver):
    # Look for and click the close button if present
    try:
        random_delay()
        # Look for and click the close button if present
        button = driver.find_element(By.CSS_SELECTOR, "button.css-yi9ndv.e8ju0x51").click()
        random_delay()
    except:
        pass  # If the close button is not found, continue to the next page

    try:
        wait = 5
        # Look for and click the next button
        next_button = driver.find_element(By.XPATH, '//a[@data-testid="pagination-page-next"]').click()
        random_delay()
        return True
    except:
        return False
    

# Function to get the jobs links
def get_links(keyword, num_links):
    LINKS = set()
    driver = driverIntialization()
    url = 'https://www.indeed.com'
    driver.get(url)
    # Identify the search box by its ID
    search_box = driver.find_element(By.ID, 'text-input-what')
    random_delay()
    # Enter the keyword and submit the form
    search_box.send_keys(keyword + Keys.RETURN)
    random_delay()
    while len(LINKS) < num_links:
        links = driver.find_elements(By.CLASS_NAME, 'jcs-JobTitle')
        for link in links:
            LINKS.add(link.get_attribute('href'))
        if not click_next_page(driver):
            random_delay()
            break
    driver.quit()
    return  list(LINKS)[:num_links]


def get_data(link):
    driver = driverIntialization()
    driver.get(link)
    random_delay()

    # Initialize variables with default values
    title = 'N/A'
    organization_name = 'N/A'
    location = 'N/A'
    salary = 'N/A'
    job_type = 'N/A'
    job_desc = 'N/A'

    try:
        title_elem = driver.find_element(By.CLASS_NAME, 'jobsearch-JobInfoHeader-title')
        title = title_elem.text.strip()
    except:
        pass

    try:
        org_name_elem = driver.find_element(By.CSS_SELECTOR, '[data-testid="inlineHeader-companyName"]')
        organization_name = org_name_elem.text.strip()
    except:
        pass

    try:
        location_elem = driver.find_element(By.CSS_SELECTOR, '[data-testid="inlineHeader-companyLocation"]')
        location = location_elem.text.strip()
    except:
        pass

    try:
        salary_elem = driver.find_element(By.ID, 'salaryInfoAndJobType')
        salary = salary_elem.text.strip()
    except:
        pass

    try:
        job_type_elem = driver.find_element(By.CSS_SELECTOR, '[data-testid="Full-time-tile"]')
        job_type = job_type_elem.text.strip()
    except:
        pass

    try:
        job_desc_elem = driver.find_element(By.XPATH, '//*[@id="jobDescriptionText"]')
        job_desc = job_desc_elem.text.strip()
    except:
        pass

    return title, organization_name, location, salary, job_type, job_desc




if __name__ == "__main__":
    keyword = input("Enter keyword: ")
    num_links = int(input("Enter number of links: "))
    df = pd.DataFrame(columns=['Title','Organzation name','Location','Pay','Job type','Job description','Link'])
    df.to_csv('Indeed job data.csv', index=False)
    links = get_links(keyword, num_links)
    for link in links:
        random_delay()
        title, org_name, location, salary, job_type, job_desc = get_data(link)
        JOB_DATA = {
            'Title': title,
            'Organzation name': org_name,
            'Location': location,
            'Pay': salary,
            'Job type': job_type,
            'Job description': job_desc,
            'Link': link
        }
        df = pd.DataFrame(JOB_DATA, index=[1])
        df.to_csv('Indeed job data.csv', index=False, header= False, mode='a')