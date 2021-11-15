from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

chrome_driver = ChromeDriverManager().install()
driver=webdriver.Chrome(chrome_driver)