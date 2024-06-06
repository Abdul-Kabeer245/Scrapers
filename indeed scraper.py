from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd    
def driverIntialization():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-cache")
    driver = webdriver.Chrome(options=options)
    return driver

def scrape(driver,keyword, numpages):
    title = []
    organization = []
    location = []
    link=[]
    url = 'https://www.indeed.com'
    driver.get(url)
    search_box = driver.find_element(By.ID, 'text-input-what')
    search_box.send_keys(keyword + Keys.RETURN)
    for i in range(1, numpages+1):
        source = driver.page_source
        soup = BeautifulSoup(source, 'html.parser')
        page_titles, page_organizations, page_locations, page_link = info(soup)
        title.extend(page_titles)
        organization.extend(page_organizations)
        location.extend(page_locations)
        link.extend(page_link)
        
        if not click_next_page(driver):
            time.sleep(100)
            break

    driver.quit()
    return title,organization, location, link

def click_next_page(driver):
    
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
        next_button = driver.find_element(By.XPATH, '//a[@data-testid="pagination-page-next"]')
        next_button.click()
        time.sleep(5)  # Ensure the page loads completely before proceeding
        return True
    except:
        return False

def info(soup):
    title = []
    organization = []
    location = []
    link = []
    h2 = soup.find_all("a", class_="jcs-JobTitle css-jspxzf eu4oa1w0")
    organization_div = soup.find_all('div', class_ = 'css-1qv0295 e37uo190')
    location_div = soup.find_all('div', class_ = "css-1p0sjhy eu4oa1w0")

    if h2:
        for t in h2:
            spans = t.find("span")
            
            if spans:
                for span in spans:
                    title.append(span.text.strip())
            
    if h2:
        for a in h2:
            links = a.get('href')
            links = "https://pk.indeed.com" +links
            link.append(links)
    
    if organization_div:
        for org in organization_div:
            spans = org.find("span")
            if spans:
                for span in spans:
                  if span.text and not span.text.isnumeric() and span.text != '':
                        organization.append(span.text.strip())

    if location_div:
       for loc in location_div:
            location.append(loc.text.strip())    
    return title, organization, location, link



keyword = input("Enter keyword: ")
num_pages = int(input("Enter number of pages: "))
driver = driverIntialization()
titles, organizatons, locations, links =  scrape(driver, keyword, num_pages)

pd.set_option('display.max_colwidth', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

all_info_df = pd.DataFrame({"Title": titles,
    "Organization": organizatons,
    "Location": locations,
    "Extracted Links": links} )
print(all_info_df)
all_info_df.to_csv('Indeed Job Postings.csv', index=False)



# <button aria-label="close" type="button" class="css-yi9ndv e8ju0x51"><svg xmlns="http://www.w3.org/2000/svg" focusable="false" role="img" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true" class="css-1xqhio eac13zx0"><path d="M4.575 18.01a.5.5 0 000 .707l.708.708a.5.5 0 00.707 0l6.01-6.01 6.01 6.01a.5.5 0 00.707 0l.707-.707a.5.5 0 000-.708L13.414 12l6.01-6.01a.5.5 0 000-.707l-.706-.708a.5.5 0 00-.707 0L12 10.586l-6.01-6.01a.5.5 0 00-.708 0l-.707.707a.5.5 0 000 .707l6.01 6.01-6.01 6.01z"></path></svg></button>