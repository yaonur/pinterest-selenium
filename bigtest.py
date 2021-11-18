import modules.logic_engine as le
from modules.utils import Driver, Data
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import modules.global_vars as global_vars
from time import sleep
import json


def start_driver():
    Driver.start_driver()
    le.login("xemere3366@erpipo.com", "pinterest123")


def test_keyword(key_word, number_of_pins_to_take=1):
    file_name, main_path, images_path = le.directory_file_setup(key_word)
    pin_links = le.get_pins(key_word, number_of_pins_to_take)
    if not pin_links:
        print('no pin links gonnna skip')
        return None
    pins_data = le.grap_data_from_pins(pin_links, images_path, starting_index=0)
    le.save_json(main_path, file_name, pins_data)
    return pins_data


start_driver()
with open('keywords.json') as keywords_data:
    json_data = json.load(keywords_data)
for keyword in json_data[3:100]:
    keyword = keyword["keyword"]
    pins_data=test_keyword(keyword,1)

