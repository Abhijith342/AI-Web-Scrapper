#This file contains a function that takes a website url and just returns all of the contents from the website

#Selenium is a framework for automating web browsers

#NOTE: With selenium we can scrape but many websites may have blocked it by captcha so it may not work 
# so we are using brightdata

import selenium.webdriver as webdriver  # webdriver is like the controller to control the site 
from selenium.webdriver.chrome.service import Service   ## Import Service class to tell Selenium where the ChromeDriver executable is
from config import SBR_WEBDRIVER    # A file config containing the API Key 

from bs4 import BeautifulSoup

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

# We only need the body from the html so we use this function
def extract_body_content(htmlcontent):
    soup = BeautifulSoup(htmlcontent,"html.parser") # BeautifulSoup is a Python library used to read and work with HTML

    body_content = soup.body # This provides the body

    if body_content:    #If body exists
        return str(body_content)
    
    return ""   #else empty string

# We must remove the scripts and style tags in the body content, so we are using this functio
def clean_body_content(body_content):

    soup = BeautifulSoup(body_content,"html.parser")

    for script_or_style  in soup(["script","style"]):   # Fetch the script and style
        script_or_style.extract()   # Extract/Remove them

    cleaned_content = soup.get_text(separator="\n")     # Add new line as separator for the text

    # If new line is extra we remove it with this
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip() 
    )

    return cleaned_content

# LLM's can read upto 8000 characters of data as they have limit so we just give the data in chunks
# allowing it to read everything
def split_dom_content(dom_content,maxlength = 6000):
    return [
        dom_content[i:i+maxlength] for i in range(0,len(dom_content),maxlength)
    ]