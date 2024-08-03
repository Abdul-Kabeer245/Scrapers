from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from bs4 import BeautifulSoup
import re
from time import sleep
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random

def random_delay():
    delay = random.randint(1, 11)
    sleep(delay)
    
def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(options=chrome_options)
    driver.delete_all_cookies()
    return driver

def login_to_facebook(driver, email, password):
    driver.get("https://www.facebook.com/")
    random_delay()
    
    email_input = driver.find_element(By.ID, "email")
    email_input.send_keys(email)
    
    password_input = driver.find_element(By.ID, "pass")
    password_input.send_keys(password)
    
    login_button = driver.find_element(By.NAME, "login")
    login_button.click()
    random_delay()

def navigate_to_group(driver, group_url):
    driver.get(group_url)
    random_delay()
    try:
        members_tab = driver.find_element(By.CSS_SELECTOR, 'a[href*="/members/"]')
        members_tab.click()
        random_delay()
    except NoSuchElementException:
        print("Members tab not found!")
        driver.quit()

def scrape_member_data(driver):
    for _ in range(10):  # Increased scrolling to load more members
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        random_delay()
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    member_divs = soup.find_all('div', {'class': re.compile('^x6s0dn4.*')})
    
    profile_links = set()
    for div in member_divs:
        link = div.find('a', href=re.compile(r'/groups/.*?/user/'))
        if link:
            profile_links.add(link['href'])
    print(f"Found {len(profile_links)} profile links.")
    return profile_links

def member_info(driver, profile_links):
    links = []
    names = []
    profiles = []
    lives_in = []
    works = []
    from_ = []
    relationship_status = []
    
    wait = WebDriverWait(driver, 10)
    for link in profile_links:
        member_profile_url = 'https://www.facebook.com' + link if not link.startswith('http') else link
        print(f"Scraping {member_profile_url}")
        driver.get(member_profile_url)
        try:
            element = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//a[@class="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x1ypdohk xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x87ps6o x1lku1pv x1a2a7pz x9f619 x3nfvp2 xdt5ytf xl56j7k x1n2onr6 xh8yej3"][@aria-label="View profile"]')))
            element.click()
            random_delay()
            profile_html = driver.page_source
            name, profile, live_in, work, from_location, relationship = extract_info(profile_html)
            links.append(driver.current_url)
            names.append(name)
            profiles.append(profile)
            lives_in.append(live_in)
            works.append(work)
            relationship_status.append(relationship)
            from_.append(from_location)
        except TimeoutException:
            print('Error: Timeout waiting for the profile link to be clickable')
        except NoSuchElementException:
            print('Error: Profile link not found')
    
    data = {
        'links': links,
        'names': names,
        'profiles': profiles,
        'lives_in': lives_in,
        'from': from_,
        'works': works,
        'relationship_status': relationship_status,
    }
    return data

def extract_info(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Initialize variables
    name = "Not found"
    profile = "Not found"
    live_in = "Not found"
    work = "Not found"
    from_location = "Not found"
    relationship = "Not found"
    
    try:
        name_element = soup.find_all('h1', {'class': 'html-h1 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1vvkbs x1heor9g x1qlqyl8 x1pd3egz x1a2a7pz'})
        if len(name_element) > 1:
            name = name_element[1].text.strip()
        else:
            name = name_element[0].text.strip() if name_element else "Not found"
        print("name:", name)
    except AttributeError:
        name = "Not found"
        print("No name found")
    
    try:
        elems = soup.find_all('div', {'class': "x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x193iq5w xeuugli x1r8uery x1iyjqo2 xs83m0k xamitd3 xsyo7zv x16hj40l x10b6aqq x1yrsyyn"})
        for e in elems:
            if 'Profile' in e.text:
                profile = e.text.strip()
            elif 'Works at' in e.text:
                work = e.text.strip()
            elif 'Lives in' in e.text:
                live_in = e.text.strip()
            elif 'From' in e.text:
                from_location = e.text.strip()
            elif e.text in ['Single', 'In a relationship', 'Engaged', 'Married', 'In a civil union', 'In a domestic partnership', 'In an open relationship', "It's complicated", 'Separated', 'Divorced']:
                relationship = e.text.strip()
    except:
        print("Error parsing profile details")
    
    return name, profile, live_in, work, from_location, relationship

if __name__ == "__main__":
    email =  input("Enter your Facebook email: ")
    password = input("Enter your Facebook password: ")
    group_url = input("Enter the URL of the Facebook group: ")
    
    driver = initialize_driver()
    login_to_facebook(driver, email, password)
    navigate_to_group(driver, group_url)
    
    profile_links = scrape_member_data(driver)
    data = member_info(driver, profile_links)
    driver.quit()
    
    df = pd.DataFrame(data)
    df.to_csv('facebook_group_members.csv', index=False)
    print("Data saved to facebook_group_members.csv")
