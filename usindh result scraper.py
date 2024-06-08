from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd

driver = webdriver.Chrome()

def search(roll_no):
    url = r'https://exam.usindh.edu.pk/v2/marksheet.php'
    driver.get(url)
    roll_no_box = driver.find_element(By.ID, 'roll_no')
    roll_no_box.send_keys(roll_no)
    year = driver.find_element(By.XPATH, '//*[@id="part"]/option[4]')
    year.click()  
    view = driver.find_element(By.ID, 'display')
    view.click()
    wait = WebDriverWait(driver, 4)
    try:
        element = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'info')))
        return driver.page_source
    except TimeoutException:
        return 'No data found'
    

def student_info(soup):
    table = soup.find('table', {'table table-hover'})
    table_row = table.find_all('tr')
    data = []
    for row in table_row:
        cols = row.find_all('td')
        for col in cols:
            data.append(col.text)
    return data

def result(soup):
    tbody = soup.find_all('tbody')
    tr = tbody[-1].find_all('tr')
    data = []
    for row in tr:
        row_data = []
        for cell in row:
            row_data.append(cell.text.strip())
        data.append(row_data)

    return data

def info_to_df(list, gpa):
    data = {
        list[0]: list[1],
        list[-2]: list[-1],
        gpa[0][0]: gpa[0][2],
        gpa[1][1]: gpa[1][3],
        gpa[2][1]: gpa[2][3],
        gpa[3][1]: gpa[3][3]
    }
    df = pd.DataFrame(data, index=[0])
    return df

all_data = pd.DataFrame()

roll_no_prefix = '2k20/swe/'
for i in range(1, 130):
    roll_no = roll_no_prefix + str(i)
    html = search(roll_no)
    if html != 'No data found':
        soup = BeautifulSoup(html, 'html.parser')
        about = student_info(soup)
        gpa = result(soup)
        df = info_to_df(about, gpa)
        all_data = pd.concat([all_data, df], ignore_index=True)
    else: print(f"No data found for: {roll_no}")

driver.quit()
all_data.to_csv('all_data.csv', index=False)