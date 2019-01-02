##Tests Using Selenium / Sauce Labs

import os
import sys
import urllib3
from sauceclient import SauceClient
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #dont squawk about insecure requests for now

# The command_executor tells the test to run on Sauce, while the desired_capabilities
# parameter tells us which browsers and OS to spin up.

# this could be made into a loop (or something ~) that runs the same tests across multiple browsers
desired_cap = {
    'platform': "Mac OS X 10.12",
    'browserName': "chrome",
    'version': "latest",
}
#creds to access sauce
username = os.environ["SAUCE_USER"]
access_key = os.environ["SAUCE_KEY"]

#auth for sauce client reporting at completion of tests
sauce_client = SauceClient(username, access_key)

#load the driver
driver = webdriver.Remote(command_executor='https://{}:{}@ondemand.saucelabs.com/wd/hub'.format(username, access_key),desired_capabilities=desired_cap)

#load the homepage and check that its the right page by title
driver.get("http://localhost:3000/#!/") # load the home page
driver.implicitly_wait(30) # wait for page to load, server might be slow, this is an actual page load, future tests will not be
if "AlgoLIFT" not in driver.title:
    raise Exception("Title is Wrong or Missing")
else: print("home page loaded")

#type in the email for login
driver.find_element_by_name("email").click()
driver.find_element_by_name("email").clear()
driver.find_element_by_name("email").send_keys(os.environ["APP_TEST_USER_ADMIN_EMAIL"])

#enter the password for login
driver.find_element_by_id("password").click()
driver.find_element_by_id("password").clear()
driver.find_element_by_id("password").send_keys(os.environ["APP_TEST_USER_PASSWORD"])

#click the login button
driver.find_element_by_xpath("//button[@type='button']").click()

#wait until the the page loads completely by waiting for an element to exist
pageLoaded = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "last-visite"))
    )

#scrape the html contents into a variable
elem = driver.find_element_by_xpath("/html/body")
html = elem.get_attribute("outerHTML")

#for debugging
#print(html)

user_email = os.environ["APP_TEST_USER_ADMIN_EMAIL"]

assert user_email in html

status = (sys.exc_info() == (None, None, None))
if status == True:
    sauce_client.jobs.update_job(driver.session_id, passed=True)
elif status == False:
    sauce_client.jobs.update_job(driver.session_id, passed=False)
driver.quit() #end the sauce labs session and shut down the VM
