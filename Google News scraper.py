# Import necessary modules
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox
from PyQt5.QtCore import QThread, pyqtSignal
from urllib.parse import urljoin
from selenium.webdriver import Chrome, ChromeOptions
from selenium import webdriver
from selenium.webdriver.common.by import By as by
from webdriver_manager.chrome import ChromeDriverManager
from parsel import Selector
import pandas as pd
from time import sleep
from datetime import datetime
import os

# Filename for the output CSV file
filename = "GoogleNews.csv"

# Function to check if the date is in the given range
def dateInRange(date, startdate, enddate, format="%d/%m/%Y", isScrapAll=False):
    if not isScrapAll:
        datetime_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        try:
            startdate_obj = datetime.strptime(startdate, format)
            enddate_obj = datetime.strptime(enddate, format)
        except ValueError:
            print(f"The Start Date {startdate} or End Date {enddate} Format Doesn't Match With dd/mm/yyyy")
            return False
        return startdate_obj.date() <= datetime_obj.date() <= enddate_obj.date()
    else:
        return True

# Thread class for running the scraping process
class ScraperThread(QThread):
    finished = pyqtSignal(str)
    scrapingFinished = pyqtSignal()
    newstypes = None
    
    def __init__(self, start_date, end_date):
        QThread.__init__(self)
        self.start_date = start_date
        self.end_date = end_date
        self.selection = Selector
        
    def search(self):
        # Initialize Chrome options
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Initialize the Chrome driver
        self.driver = webdriver.Chrome(options=chrome_options)
        PATH = ChromeDriverManager().install()
        
        # Open Google News homepage
        self.driver.get("https://news.google.com/home?hl=en-CA&gl=CA&ceid=CA%3Aen")
        sleep(2)  # Wait for the page to load
        
        # Parse the page source with Parsel
        response = Selector(self.driver.page_source)
        
        # Get news topic URLs and names
        self.newstypes = [urljoin("https://news.google.com/", u) for u in response.xpath("//div[contains(@class,'EctEBd')]/a[contains(@href,'topic')]/@href").extract()]
        topicnames = [u for u in response.xpath("//div[contains(@class,'EctEBd')]/a[contains(@href,'topic')]/@aria-label").extract()]
        self.topics = {topicnames[i]: self.newstypes[i] for i in range(len(topicnames))}
        return self.topics, self.newstypes
    
    def run(self, selection):
        self.search()
        filename = "GoogleNews.csv"
        
        # Open selected topic URL
        self.driver.get(self.topics.get(selection))
        sleep(0.5)
        
        # Find subtypes of news if available
        newssubtypes = self.driver.find_elements(by.XPATH, "//div[@class = 'VfPpkd-dgl2Hf-ppHlrf-sM5MNb']/button[@role = 'tab']")
        
        if newssubtypes:
            for i in range(len(newssubtypes)):
                newssubtypes = self.driver.find_elements(by.XPATH, "//div[@class = 'VfPpkd-dgl2Hf-ppHlrf-sM5MNb']/button[@role = 'tab']")
                newssubtypes[i].click()
                sleep(2)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(2)
                
                # Parse the page source with Parsel
                response = Selector(self.driver.page_source)
                
                # Extract article details
                for article in response.xpath("//c-wiz[@jsrenderer = 'ARwRbe']/c-wiz/div/article | //div[@class = 'f9uzM']/article | //c-wiz[@jsrenderer = 'ARwRbe']/c-wiz/article"):
                    title = article.xpath(".//h4/text()").get()
                    source = article.xpath(".//div/div/div/div[@class = 'vr1PYe']/text()").get()
                    date = article.xpath(".//div/time/@datetime").get()
                    link = urljoin("https://news.google.com/", article.xpath(".//div/a/@href").get())
                    
                    # Create a frame for storing article details
                    frame = {"Headline": [], "NewsSource": [], "Link": [], "DatePosted": []}
                    
                    # Check if the article date is in the given range
                    if dateInRange(date, self.start_date, self.end_date):
                        frame['Headline'].append(title)
                        frame['NewsSource'].append(source)
                        frame['Link'].append(link)
                        frame['DatePosted'].append(date)
                        
                        # Save the article details to CSV
                        if not os.path.exists(filename):
                            pd.DataFrame(frame).to_csv(filename, index=False)
                        else:
                            pd.DataFrame(frame).to_csv(filename, index=False, mode='a', header=False)
                self.driver.execute_script("window.scrollTo(document.body.scrollHeight, 0);")
        else:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(2)
            
            # Parse the page source with Parsel
            response = Selector(self.driver.page_source)
            
            # Extract article details
            for article in response.xpath("//c-wiz[@jsrenderer = 'ARwRbe']/c-wiz/div/article | //div[@class = 'f9uzM']/article | //c-wiz[@jsrenderer = 'ARwRbe']/c-wiz/article"):
                title = article.xpath(".//h4/text()").get()
                source = article.xpath(".//div/div/div/div[@class = 'vr1PYe']/text()").get()
                date = article.xpath(".//div/time/@datetime").get()
                link = urljoin("https://news.google.com/", article.xpath(".//div/a/@href").get())
                
                # Create a frame for storing article details
                frame = {"Headline": [], "NewsSource": [], "Link": [], "DatePosted": []}
                
                # Check if the article date is in the given range
                if dateInRange(date, self.start_date, self.end_date):
                    frame['Headline'].append(title)
                    frame['NewsSource'].append(source)
                    frame['Link'].append(link)
                    frame['DatePosted'].append(date)
                    
                    # Save the article details to CSV
                    if not os.path.exists(filename):
                        pd.DataFrame(frame).to_csv(filename, index=False)
                    else:
                        pd.DataFrame(frame).to_csv(filename, index=False, mode='a', header=False)
        
        # Remove duplicate entries in the CSV file
        pd.read_csv(filename).drop_duplicates().to_csv(filename, index=False)
        
        # Close the browser and emit signals
        self.driver.close()
        self.scrapingFinished.emit()
        self.finished.emit("Scraping completed successfully!")

# Main GUI class
class WebScraperGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.close()

    def initUI(self):
        # Create the layout
        layout = QVBoxLayout()

        # Create and add start date label and input
        self.start_date_label = QLabel('Start Date (dd/mm/yyyy):', self)
        layout.addWidget(self.start_date_label)
        self.start_date_input = QLineEdit(self)
        layout.addWidget(self.start_date_input)

        # Create and add end date label and input
        self.end_date_label = QLabel('End Date (dd/mm/yyyy):', self)
        layout.addWidget(self.end_date_label)
        self.end_date_input = QLineEdit(self)
        layout.addWidget(self.end_date_input)

        # Create and add news type label and dropdown
        self.news_type_label = QLabel('Select News Type:', self)
        layout.addWidget(self.news_type_label)
        self.news_type_dropdown = QComboBox(self)
        
        # Initialize the scraper thread to get topics
        scraper = ScraperThread(self.start_date_input, self.end_date_input)
        topics, news = scraper.search()
        self.news_type_dropdown.addItems(topics)  # Add more types as needed
        layout.addWidget(self.news_type_dropdown)

        # Set default selection
        self.selection = self.news_type_dropdown.currentText()

        # Connect currentTextChanged signal to updateSelection method
        self.news_type_dropdown.currentTextChanged.connect(self.updateSelection)

        # Create and add scrape button
        self.scrape_button = QPushButton('Scrape', self)
        self.scrape_button.clicked.connect(self.startScraping)
        layout.addWidget(self.scrape_button)

        # Set the layout and window title
        self.setLayout(layout)
        self.setWindowTitle('Web Scraper GUI')

    def updateSelection(self, text):
        # Update the selected news type
        self.selection = text

    def startScraping(self):
        # Get start and end dates from input fields
        start_date = self.start_date_input.text()
        end_date = self.end_date_input.text()
        
        # Initialize the scraper thread and start it
        scraper = ScraperThread(start_date, end_date)
        self.thread = scraper.run(self.selection)
        self.thread = ScraperThread(start_date, end_date)
        self.thread.scrapingFinished.connect(self.closeWindow)  # Connect signal to slot
        scraper.start()  # Start the thread

    def onScrapingFinished(self, message):
        # Notify the user that scraping is finished
        pass

    def closeWindow(self):
        # Close the application window
        self.close()

# Main entry point for the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WebScraperGUI()
    ex.show()
    sys.exit(app.exec_())
