import modules.logic_engine as le
from modules.utils import Driver, Data
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import modules.global_vars as global_vars
from time import sleep
import json


def console_commands():
    pin_links = le.get_pins("bira", 20)
    page_data = BeautifulSoup(Driver.driver.page_source, "html.parser")
    test_data = page_data.findAll("a", class_="Wk9 xQ4 CCY czT eEj kVc")[1]["href"]
    test_data = (
        WebDriverWait(Driver.driver, 1).until(EC.presence_of_element_located(
            (By.XPATH, global_vars.pin_owner_link_xpath))).get_attribute("href")
    )
    test_data = WebDriverWait(Driver.driver, 1).until(EC.presence_of_element_located(
        (By.XPATH, global_vars.pin_owner_name_xpath))).text

    WebDriverWait(Driver.driver, 10).until(EC.invisibility_of_element((By.XPATH, global_vars.pins_container_xpath)))


def start_driver():
    Driver.start_driver()
    le.login("xemere3366@erpipo.com", "pinterest123")


def test_keyword(key_word="test", number_of_pins_to_take=1):
    file_name, main_path, images_path = le.directory_file_setup(key_word="test")
    pin_links = le.get_pins("bira", number_of_pins_to_take)
    pins_data = le.grap_data_from_pins(pin_links, images_path, starting_index=0)
    le.save_json(main_path, file_name,pins_data)
    return pins_data

images_path=""
def test_link():
    pins_data = le.grap_data_from_pins(["https://tr.pinterest.com/pin/923237992332044142/"], images_path=images_path)
    return pins_data


def get_user_data():
    Driver.driver.get("https://tr.pinterest.com/pin/830280881308830894/")


start_driver()
# pins_data = test_keyword("test", 1)
# test_link()
