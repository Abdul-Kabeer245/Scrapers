# Import necessary libraries for web scraping and data manipulation
from selenium import webdriver  # For automating web browser interaction
from selenium.webdriver.chrome.options import Options  # To set options for Chrome WebDriver
from selenium.webdriver.common.by import By  # To locate elements on a webpage
from selenium.common.exceptions import NoSuchElementException, TimeoutException  # For handling specific exceptions
from bs4 import BeautifulSoup  # For parsing HTML and extracting data
from time import sleep  # To introduce delays
import pandas as pd  # For data manipulation and storage
from selenium.webdriver.support.ui import WebDriverWait  # To wait for elements to be present
from selenium.webdriver.support import expected_conditions as EC  # To specify conditions for WebDriverWait
import random  # To generate random numbers for delays

def random_delay():
    """Introduces a random delay to mimic human behavior."""
    delay = random.randint(1, 11)  # Random delay between 1 and 11 seconds
    sleep(delay)  # Sleep for the random delay duration

def initialize_driver():
    """Initializes the Chrome WebDriver with specified options."""
    chrome_options = Options()  # Create an Options object for Chrome
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Disable automation detection
    chrome_options.add_argument("--disable-notifications")  # Disable notifications
    driver = webdriver.Chrome(options=chrome_options)  # Initialize the Chrome WebDriver with the options
    driver.delete_all_cookies()  # Delete all cookies
    return driver  # Return the driver instance

def login_to_facebook(driver, email, password):
    """Logs into Facebook using provided credentials."""
    driver.get("https://www.facebook.com/")  # Navigate to Facebook login page
    random_delay()  # Introduce random delay
    
    email_input = driver.find_element(By.ID, "email")  # Find the email input field
    email_input.send_keys(email)  # Enter the email
    
    password_input = driver.find_element(By.ID, "pass")  # Find the password input field
    password_input.send_keys(password)  # Enter the password
    
    login_button = driver.find_element(By.NAME, "login")  # Find the login button
    login_button.click()  # Click the login button
    random_delay()  # Introduce random delay

def navigate_to_group(driver, group_url):
    """Navigates to the specified Facebook group and clicks on the members tab."""
    driver.get(group_url)  # Navigate to the Facebook group URL
    random_delay()  # Introduce random delay
    try:
        members_tab = driver.find_element(By.CSS_SELECTOR, 'a[href*="/members/"]')  # Find the members tab
        members_tab.click()  # Click the members tab
        random_delay()  # Introduce random delay
    except NoSuchElementException:  # Handle case where members tab is not found
        print("Members tab not found!")  # Print error message
        driver.quit()  # Quit the driver

def scrape_member_data(driver):
    """Scrapes member profile links from the Facebook group."""
    for _ in range(10):  # Scroll down 10 times to load more members
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll to the bottom of the page
        random_delay()  # Introduce random delay
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')  # Parse the page source with BeautifulSoup
    member_divs = soup.find_all('div', {'class': re.compile('^x6s0dn4.*')})  # Find all member divs with the specified class pattern
    
    profile_links = set()  # Initialize a set to store unique profile links
    for div in member_divs:  # Iterate over each member div
        link = div.find('a', href=re.compile(r'/groups/.*?/user/'))  # Find the profile link within the div
        if link:  # If a link is found
            profile_links.add(link['href'])  # Add the link to the set
    print(f"Found {len(profile_links)} profile links.")  # Print the number of profile links found
    return profile_links  # Return the set of profile links

def member_info(driver, profile_links):
    """Extracts member information from their profiles."""
    links = []  # Initialize list to store profile links
    names = []  # Initialize list to store names
    profiles = []  # Initialize list to store profiles
    lives_in = []  # Initialize list to store live-in locations
    works = []  # Initialize list to store work information
    from_ = []  # Initialize list to store hometowns
    relationship_status = []  # Initialize list to store relationship statuses
    
    wait = WebDriverWait(driver, 10)  # Initialize WebDriverWait with a timeout of 10 seconds
    for link in profile_links:  # Iterate over each profile link
        member_profile_url = 'https://www.facebook.com' + link if not link.startswith('http') else link  # Construct full profile URL
        print(f"Scraping {member_profile_url}")  # Print the profile URL being scraped
        driver.get(member_profile_url)  # Navigate to the profile URL
        try:
            element = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//a[@class="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x1ypdohk xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x87ps6o x1lku1pv x1a2a7pz x9f619 x3nfvp2 xdt5ytf xl56j7k x1n2onr6 xh8yej3"][@aria-label="View profile"]')))  # Wait for the profile link to be clickable
            element.click()  # Click the profile link
            random_delay()  # Introduce random delay
            profile_html = driver.page_source  # Get the page source of the profile
            name, profile, live_in, work, from_location, relationship = extract_info(profile_html)  # Extract information from the profile
            links.append(driver.current_url)  # Append the profile URL to the links list
            names.append(name)  # Append the name to the names list
            profiles.append(profile)  # Append the profile information to the profiles list
            lives_in.append(live_in)  # Append the live-in location to the lives_in list
            works.append(work)  # Append the work information to the works list
            relationship_status.append(relationship)  # Append the relationship status to the relationship_status list
            from_.append(from_location)  # Append the hometown to the from_ list
        except TimeoutException:  # Handle case where profile link is not clickable within the timeout period
            print('Error: Timeout waiting for the profile link to be clickable')  # Print error message
        except NoSuchElementException:  # Handle case where profile link is not found
            print('Error: Profile link not found')  # Print error message
    
    data = {  # Create a dictionary to store the extracted data
        'links': links,
        'names': names,
        'profiles': profiles,
        'lives_in': lives_in,
        'from': from_,
        'works': works,
        'relationship_status': relationship_status,
    }
    return data  # Return the data dictionary

def extract_info(html):
    """Extracts information from the member's profile page."""
    soup = BeautifulSoup(html, 'html.parser')  # Parse the profile HTML with BeautifulSoup
    
    # Initialize variables
    name = "Not found"
    profile = "Not found"
    live_in = "Not found"
    work = "Not found"
    from_location = "Not found"
    relationship = "Not found"
    
    try:
        name_element = soup.find_all('h1', {'class': 'html-h1 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1vvkbs x1heor9g x1qlqyl8 x1pd3egz x1a2a7pz'})  # Find the name element
        if len(name_element) > 1:  # If there are multiple name elements
            name = name_element[1].text.strip()  # Use the second one
        else:
            name = name_element[0].text.strip() if name_element else "Not found"  # Use the first one if available
        print("name:", name)  # Print the extracted name
    except AttributeError:  # Handle case where name element is not found
        name = "Not found"  # Set name to "Not found"
        print("No name found")  # Print error message
    
    try:
        elems = soup.find_all('div', {'class': "x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x193iq5w xeuugli x1r8uery x1iyjqo2 xs83m0k xamitd3 xsyo7zv x16hj40l x10b6aqq x1yrsyyn"})  # Find all elements with the specified class
        # Add more logic here to extract additional information from elems as needed
    except AttributeError:  # Handle case where elements are not found
        print("No additional profile information found")  # Print error message
    
    return name, profile, live_in, work, from_location, relationship  # Return the extracted information

# Main function to execute the scraping process
if __name__ == "__main__":
    email =  input("Enter your Facebook email: ")
    password = input("Enter your Facebook password: ")
    group_url = input("Enter the URL of the Facebook group: ")
    
    driver = initialize_driver()  # Initialize the WebDriver
    login_to_facebook(driver, email, password)  # Log in to Facebook
    navigate_to_group(driver, group_url)  # Navigate to the specified Facebook group
    
    profile_links = scrape_member_data(driver)  # Scrape member profile links
    data = member_info(driver, profile_links)  # Extract member information
    
    df = pd.DataFrame(data)  # Create a DataFrame from the extracted data
    df.to_csv("facebook_group_members.csv", index=False)  # Save the DataFrame to a CSV file
    
    driver.quit()  # Quit the WebDriver

