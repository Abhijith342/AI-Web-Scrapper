#This file contains a function that takes a website url and just returns all of the contents from the website

#Selenium is a framework for automating web browsers

#NOTE: With selenium we can scrape but many websites may have blocked it by captcha so it may not work 
# so we are using brightdata

import selenium.webdriver as webdriver  # webdriver is like the controller to control the site 
from selenium.webdriver.chrome.service import Service   ## Import Service class to tell Selenium where the ChromeDriver executable is
import time ## Import time module to add delays (sleep)


# Define a function that takes a website URL and returns its HTML content
def scrape_website(website):
    print("Launching chrome browser...")

    # Path to your ChromeDriver executable (must match your Chrome version)
    chrome_driver_path = "./chromedriver.exe"

    options = webdriver.ChromeOptions() # Create Chrome options (you can add settings here like headless mode)

    # Start a new Chrome browser using the driver and options
    driver = webdriver.Chrome(service=Service(chrome_driver_path),options=options)

    try:
        # Open the given website in the browser
        driver.get(website)
        print("Page loaded...")


        html = driver.page_source

        # Pause for 10 seconds (so you can see the browser before it closes)
        time.sleep(10)

        return html

    finally:
        # Close the browser window and end the session
        driver.quit()