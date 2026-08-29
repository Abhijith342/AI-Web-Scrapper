#This file contains a function that takes a website url and just returns all of the contents from the website

#Selenium is a framework for automating web browsers

#NOTE: With selenium we can scrape but many websites may have blocked it by captcha so it may not work 
# so we are using brightdata

import selenium.webdriver as webdriver  # webdriver is like the controller to control the site 
from selenium.webdriver.chrome.service import Service   ## Import Service class to tell Selenium where the ChromeDriver executable is
from config import SBR_WEBDRIVER    # A file config containing the API Key 

# Define a function that takes a website URL and returns its HTML content
def scrape_website(website):
    print("Launching chrome browser...")

    options = webdriver.ChromeOptions() # Create Chrome options (you can add settings here like headless mode)

    # Start a new Chrome browser using the driver and options
    # driver = webdriver.Chrome(service=Service(chrome_driver_path),options=options)

    # driver is now Remote based on the API options
    driver = webdriver.Remote(
        command_executor=SBR_WEBDRIVER,
        options=options
    )

    try:
        # Open the given website in the browser
        driver.get(website)
        print("Page loaded...")

        html = driver.page_source

        return html

    finally:
        # Close the browser window and end the session
        driver.quit()