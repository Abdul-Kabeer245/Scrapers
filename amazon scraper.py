# Import necessary libraries and modules
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
from time import sleep
import pandas as pd
from amazoncaptcha import AmazonCaptcha
import os

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

def bypass_captcha(driver):
    """Bypass captcha on Amazon."""
    # Open Amazon homepage
    driver.get('https://www.amazon.com/')
    # Loop to handle captcha
    while True:
        try:
            # Find the captcha image link
            link = driver.find_element(By.XPATH, "//div[@class = 'a-row a-text-center']//img").get_attribute('src')
            # Solve the captcha
            captcha = AmazonCaptcha.fromlink(link)
            captchaValue = AmazonCaptcha.solve(captcha)
            # Enter the captcha value and submit
            driver.find_element(by=By.XPATH, value='//input[@placeholder="Type characters"]').send_keys(captchaValue + Keys.RETURN)
            sleep(3)  # Wait for page to reload
        except:
            return  # Exit loop if no captcha is found

def search_items(driver, query):
    """Search for items on Amazon."""
    # Find the search box element
    search = driver.find_element(By.ID, 'twotabsearchtextbox')
    # Enter the search query and submit
    search.send_keys(query + Keys.RETURN)
    sleep(3)  # Wait for the search results to load

def get_product_links(driver, limit):
    """Get product links from the search results page."""
    links = list()
    while True:
        # Find all product links on the current page
        product_headings = driver.find_elements(By.CSS_SELECTOR, 'a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')
        for a in product_headings:
            links.append(a.get_attribute('href'))
        if len(set(links)) >= limit:
            return set(links[:limit])
        try:
            # Click the 'Next' button to go to the next page of results
            next_button = driver.find_element(By.CSS_SELECTOR, 'a.s-pagination-next')
            next_button.click()
            sleep(3)  # Wait for the next page to load
        except NoSuchElementException:
            break
    return set(links[:limit])

def extract_avg_rating(soup):
    """Extract the average rating from the product page."""
    try:
        # Find the average rating element
        rating_element = soup.select_one('.a-icon-alt')
        if rating_element:
            avg_ratings = re.search(r'[\d.]+', rating_element.text).group()
            return avg_ratings
    except Exception as e:
        print(f"Error extracting rating: {e}")
    return None

def extract_product_price(soup):
    """Extract the price from the product page."""
    try:
        # Find the product price element
        price_element = soup.select_one('.a-price .a-offscreen')
        if price_element:
            return price_element.text.strip()
    except Exception as e:
        print(f"Error extracting price: {e}")
    return None

def extract_product_data(driver, product_url):
    """Extract data from a product page."""
    # Open the product page URL
    driver.get(product_url)
    source = driver.page_source
    soup = BeautifulSoup(source, "html.parser")

    avg_ratings = extract_avg_rating(soup)
    product_price = extract_product_price(soup)

    # Extract various product details
    product_data = {
        "Product URL": product_url,
        'product_img': soup.find('img', {'id': 'landingImage'}).get("src"),
        'product_title': soup.find('span', {'id': 'productTitle'}).get_text(strip=True) if soup.find('span', {'id': 'productTitle'}) else None,
        'avrg_ratings': avg_ratings,
        'number_ratings': soup.find('span', {'id': "acrCustomerReviewText"}).get_text(strip=True) if soup.find('span', {'id': "acrCustomerReviewText"}) else None,
        'product_prices': product_price,
        'about_item': soup.find('div', {"id": 'feature-bullets'}).get_text(separator=' ', strip=True) if soup.find('div', {"id": 'feature-bullets'}) else None,
        'seller_info': about_seller(driver)
    }
    return product_data

def about_seller(driver):
    """Extract information about the seller."""
    try:
        # Click the seller profile link
        seller_link = driver.find_element(By.ID, "sellerProfileTriggerId")
        seller_link.click()
        sleep(2)  # Wait for the seller profile page to load
        source = driver.page_source
        soup = BeautifulSoup(source, "html.parser")
        div_element = soup.find('div', id='page-section-detail-seller-info')
        if div_element:
            all_text = div_element.get_text(separator=' ', strip=True)
            return all_text
        else:
            return "Amazon Warehouse"
    except NoSuchElementException:
        return "Amazon.com"

def create_dataframe(product_list):
    """Create a DataFrame from the product list."""
    return pd.DataFrame(product_list)

if __name__ == "__main__":
    output = 'amazon_products.csv'
    query = input("Enter the keywords to search for: ")
    limit = int(input("Enter the limit of products to scrape: "))
    try:
        all_product_data = []
        with initialize_driver() as driver:
            bypass_captcha(driver)
            search_items(driver, query)
            product_urls = get_product_links(driver, limit)
            for index, url in enumerate(product_urls):
                try:
                    if len(all_product_data) >= limit:
                        break
                    print("url no: ", index)
                    product_data = extract_product_data(driver, url)
                    all_product_data.append(product_data)
                    # Save periodically to avoid losing progress
                    if len(all_product_data) % 5 == 0:  # Adjust the frequency as needed
                        all_data = create_dataframe(all_product_data)
                        if os.path.exists(output):
                            all_data.to_csv(output, index=False, mode='a', header=False)
                        else:
                            all_data.to_csv(output, index=False)
                        print(f"Data saved to {output} (progress checkpoint)")
                        all_product_data = []  # Clear list after saving
                except Exception as e:
                    print(f"Error processing {url}: {e}")
            
            # Save remaining data
            if all_product_data:
                all_data = create_dataframe(all_product_data)
                if os.path.exists(output):
                    all_data.to_csv(output, index=False, mode='a', header=False)
                else:
                    all_data.to_csv(output, index=False)
                print(f"Data successfully saved to {output}")
    except PermissionError:
        print(f"Permission denied: Unable to write to {output}. The file might be open in another program or locked.")
    except Exception as e:
        print(f"An error occurred: {e}")