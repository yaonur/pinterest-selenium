from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
options.headless=True
# options.binary_location = "/usr/lib/firefox/firefox"
# chrome_driver = ChromeDriverManager().install()
# driver = webdriver.Chrome(chrome_driver,options=options)
firefox_driver = GeckoDriverManager().install()
driver = webdriver.Firefox(options=options ,executable_path=firefox_driver)
# driver=webdriver.Chrome(executable_path="/home/ynr/driver/chromedriver")
# driver = webdriver.Firefox(executable_path="/home/ynr/driver/geckodriver", options=options)
driver.get("https://www.google.com.tr/")
print("finished")