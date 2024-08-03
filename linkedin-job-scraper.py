import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome import options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import random
import pandas as pd

def random_delay():
    time.sleep(random.randint(1,10))

def proxies():
    with open('valid_proxies.txt', 'r') as f:
        proxy = f.read().split('\n')
        return random.choice(proxy)

def driver_init():
    chrome_options = options.Options()
    chrome_options.add_argument('--disable-cache')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--start-maximized')
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument(f'--proxy-server={proxies()}')
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def search_job(driver, job_title, job_location):
    try:
        search_box = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'job-search-bar-keywords')))
        search_box.send_keys(job_title)
        random_delay()
        location_box = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'job-search-bar-location')))
        location_box.clear()
        location_box.send_keys(job_location + Keys.RETURN)
        return True

    except Exception as e :
        return False


def job_listing(driver, num_jobs):
    # Checking available jobs
    available_jobs_element = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, 'results-context-header__job-count')))
    available_jobs_text = available_jobs_element.text.strip()
    
    # Extract numeric part of available jobs count
    available_jobs_count = int(re.search(r'\d+', available_jobs_text.replace(',', '')).group())
    unique_links = set()
    if available_jobs_count == 0:
        return 'No Job found'
    else:
        while len(unique_links) < num_jobs:
            # Scroll to the bottom of the page to load more jobs
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight - 200)')
            try:
                # Wait for the 'viewed all' notification
                viewed_all = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'inline-notification__text')))
                
                # Check if 'viewed all' text is present
                if 'viewed all' in viewed_all.text.lower():
                    # Find all job links on the page
                    links = driver.find_elements(By.CLASS_NAME, 'base-card__full-link')
                    
                    # Extract href attributes from links and store them in JOB_LISTING
                    unique_links.update(l.get_attribute('href') for l in links)
                            
                    # return set of job links
                    return unique_links
            except:
                # check if show more button is present
                try:
                    show_more_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'infinite-scroller__show-more-button')))
                    current_height = driver.execute_script('window.scrollTo(0, document.body.scrollHeight - 200)')
                    show_more_button.click()
                    random_delay()
                    
                    # scroll down
                    new_height = driver.execute_script('return document.body.scrollHeight - 200)')
                    
                    if current_height == new_height or len(unique_links)== num_jobs:
                        
                        # Find all job links on the page
                        links = driver.find_elements(By.CLASS_NAME, 'base-card__full-link')
                    
                        # Extract href attributes from links and store them in JOB_LISTING
                        unique_links.update(l.get_attribute('href') for l in links)
                    
                        return unique_links
                except:
                    try: 
                        driver.execute_script('window.scrollTo(0, document.body.scrollHeight - 200)')
                        random_delay()

                        # Find all job links on the page
                        links = driver.find_elements(By.CLASS_NAME, 'base-card__full-link')
                    
                        # Extract href attributes from links and store them in JOB_LISTING
                        unique_links.update(l.get_attribute('href') for l in links)

                        if len(unique_links)== num_jobs:
                            return unique_links
                        
                    except Exception as e:
                        # Log any exceptions that occur during the process
                        return 'No Job found'

def extract_data(link):
    driver = driver_init()
    driver.get(link)
    random_delay()
    
    # find name
    job_title = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'top-card-layout__title')))
    job_title = job_title.text.strip()
    
    # find organization name
    org_name = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'topcard__flavor')))
    org_name = org_name.text.strip()

    # find location
    job_location = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="main-content"]/section[1]/div/section[2]/div/div[1]/div/h4/div[1]/span[2]')))
    job_location = job_location.text.strip()

    # find posted time
    posted_date = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="main-content"]/section[1]/div/section[2]/div/div[1]/div/h4/div[2]/span')))
    posted_date = posted_date.text.strip()
    
    random_delay()
    # click show more button
    show_more_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'show-more-less-html__button')))
    show_more_button.click()
    # find job description
    job_description = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "show-more-less-html__markup")))
    job_description = job_description.text.strip()

    # Find job criteria items
    job_criteria_items = driver.find_elements(By.CLASS_NAME, 'description__job-criteria-item')
    employment_type = 'N/A'
    job_function = 'N/A'
    industries = 'N/A'
    # Extract job type, function, and industries
    for item in job_criteria_items:
        header = item.find_element(By.CLASS_NAME, 'description__job-criteria-subheader').text.strip()
        criteria_text = item.find_element(By.CLASS_NAME, 'description__job-criteria-text--criteria').text.strip()
        
        if header and header == "Employment type":
            employment_type = criteria_text
        elif header and header == "Job function":
            job_function = criteria_text
        elif header and header == "Industries":
            industries = criteria_text
        
    driver.quit()
    return job_title, org_name, job_location, posted_date, job_description, employment_type, job_function, industries  

def main():
    URL = r'https://www.linkedin.com/jobs/search?trk=guest_homepage-basic_guest_nav_menu_jobs&position=1&pageNum=0'
    JOB_TITLE = input("Enter job title: ")
    LOCATION = input("Enter job city with country name: ")
    num_jobs = int(input("Enter number of jobs to scrape: ")) 
    job_title, org_name, job_location, posted_date, job_desc, employment_type, job_func, industries, links = ([] for i in range(9))    
    while True:
        driver = driver_init()
        driver.get(URL)
        random_delay()
        if search_job(driver, JOB_TITLE, LOCATION):
            job_links = job_listing(driver, num_jobs)
            driver.quit()
            break
        else:
            driver.quit()
            random_delay()    
    if isinstance(job_links, set):
        for link in job_links:
            title, name, location, date, desc, employment, job, industry = extract_data(link)
            random_delay()
            # job_title.append(title)
            # org_name.append(name)
            # job_location.append(location)
            # posted_date.append(date)
            # job_desc.append(desc)
            # employment_type.append(employment)
            # job_func.append(job)
            # industries.append(industry)
            # links.append(link)
            JOB_DATA = {
                "Job Title": title,
            "Link": link,
            "Organization Name": name,
            "Job Location": location,
            "Posted Date": date,
            "Job Description": desc,
            "Employment Type": employment,
            "Job Function": job,
            "Industries": industry 
            }
            df = pd.DataFrame(JOB_DATA)
            df.to_csv("linkedin job data.csv", index=False, header= False, mode= 'a+')

if __name__ == '__main__':
    main()