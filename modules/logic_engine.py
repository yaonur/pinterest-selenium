import json
from modules.utils import Driver, Search, Data
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from typing import Tuple, List
import requests
import requests.cookies
import os
from datetime import datetime


def directory_file_setup(key_word: str) -> Tuple[str, str, str]:
    key_word = Data.remove_spaces(key_word)
    file_name = key_word + "_" + datetime.now().strftime("%y%m%d%H")
    home_directory = os.getcwd()
    main_path = os.path.join(home_directory, f"data/{key_word}/" + file_name) + "/"
    images_path = (
            os.path.join(home_directory, f"data/{key_word}/" + file_name + "/images")
            + "/"
    )
    os.makedirs(main_path, exist_ok=True)
    os.makedirs(images_path, exist_ok=True)
    return file_name, main_path, images_path


def login(email, password, wait_time=10):
    driver = Driver.driver
    driver.get("https://pinterest.com/login")

    try:
        WebDriverWait(driver, wait_time).until(EC.element_to_be_clickable((By.ID, 'email')))
        driver.find_element_by_id("email").send_keys(email)
        driver.find_element_by_id("password").send_keys(password)

        logins = driver.find_elements_by_xpath("//*[contains(text(), 'Log in')]")

        for login in logins:
            login.click()

        WebDriverWait(driver, wait_time).until(EC.invisibility_of_element((By.ID, 'email')))

    #     cookies = driver.get_cookies()
    #
    #     http.cookies.clear()
    #     for cookie in cookies:
    #         http.cookies.set(cookie['name'], cookie['value'])
    #
    #     registry.update_all(http.cookies.get_dict())
    except Exception as e:
        print("Failed to login", e)

    print("Successfully logged in with account " + email)
    sleep(4)


def get_pins(key_word: str, number_of_pins_to_take: int) -> List:
    print(f'getting pins in keyword {key_word}')
    pin_links = []
    Driver.driver.get(
        f"https://tr.pinterest.com/search/pins/?q={key_word}&rs=rs&eq=&etslf=2120&term_meta[]={key_word}%7Crecentsearch%7C1"
    )
    sleep(2)

    while True:
        last_height = Driver.driver.execute_script(
            "return document.body.scrollHeight"
        )
        try:
            pins = Search.find_element_class("gridCentered").find_elements(By.TAG_NAME,
                                                                           "a"
                                                                           )
        except:
            print(f'no pin found keyword {key_word}')
            break
        for pin in pins:
            try:
                pin_links.append(pin.get_attribute("href"))
            except:
                print("pin_links.append exception")
                pass
        pin_links = list(dict.fromkeys(pin_links))
        Driver.driver.execute_script(f"window.scrollTo(0,{last_height})")
        sleep(2)

        if len(
                pin_links
        ) >= number_of_pins_to_take or last_height == Driver.driver.execute_script(
            "return document.body.scrollHeight"
        ):
            if len(pin_links) > number_of_pins_to_take:
                del pin_links[number_of_pins_to_take:]
            pin_links = list(
                filter(lambda key_word: key_word[25:29] == "pin/", pin_links)
            )
            return pin_links


def merge_pin_list(pin_links, keyword):
    print("mergin pin lists")
    try:
        with open(f"data/{keyword}/{keyword}_links.json") as file:
            old_links = json.load(file)
    except:
        old_links=False
        print("no old record for links")
        pass
    try:
        if old_links:
            pass
        with open(f"data/{keyword}/{keyword}_links.json") as file:
            json.dump(pin_links,file)

    except:
        print(f"big fail on mergin links skip {keyword}")
        return False




def grap_data_from_pins(pins_links: list, images_path: str, starting_index=0) -> list:
    pins_data = []
    have_owner = False
    have_sharer = False
    # get pin owner name link
    for index, link in enumerate(pins_links[starting_index:]):
        try:
            print("starting index:" + str(index + starting_index))
            owner_link, owner_name = Data.get_owner_name_and_link(link)
            if not owner_name:
                print(f"cant get pin owner info  {link}")
                have_owner = False
            else:
                have_owner = True
        except:
            print("**********exception on grap data getting owner name and link**********")
            owner_link, owner_name = ('', '')
            have_owner = False
        # get pin sharer name and link
        try:
            sharer_link, sharer_name = Data.get_sharer_name_link()
            if not sharer_name:
                have_sharer = False
            else:
                have_sharer = True
        except:
            print("*******exception on grap data getting sharer name and link**********")
            sharer_link, sharer_name = ('', '')
        if not have_sharer and not have_owner:
            print("cant get any user info passing link")
            continue

        # get feed comments story and image
        try:
            comments = Data.get_comments()

        except:
            print("exception on getting comments ")
            pass

        try:
            feed_story = Data.get_feed_story()
        except:
            print("exception on getting feed story ")
            pass
        # getting images and saving them
        try:
            image_link = Data.get_image(images_path, index)
            # image_link = ""
        except:
            print("exception on getting image or saving it")
            pass

        # get user page data
        try:
            if have_owner:
                (
                    owner_bio,
                    owner_follower_number,
                    owner_viewed_number,
                ) = Data.get_users_page_data(owner_link)

        except:
            print("*********exception on grap data getting user page***********")
            owner_bio = ''
            owner_follower_number = ''
            owner_viewed_number = ''
            pass
        # get sharer page data

        try:
            if have_sharer:
                (
                    sharer_bio,
                    sharer_follower_number,
                    sharer_viewed_number,
                ) = Data.get_users_page_data(sharer_link)
                if not have_owner:
                    owner_name = sharer_name
                    owner_link = sharer_link
                    owner_bio = sharer_bio
                    owner_follower_number = sharer_follower_number
                    owner_viewed_number = sharer_viewed_number
            else:
                sharer_name = owner_name
                sharer_link = owner_link
                sharer_bio = owner_bio
                sharer_follower_number = owner_follower_number
                sharer_viewed_number = owner_viewed_number

        except:
            print("*********exception on grap data getting user page***********")
            sharer_bio = ''
            sharer_follower_number = ''
            sharer_viewed_number = ''
            pass

        pin_data = {
            "id": index + starting_index,
            "feed_link": link,
            "feed_story": feed_story,
            "comments": comments,
            "image_link": image_link,

            "owner_link": owner_link,
            "owner_name": owner_name,
            "owner_bio": owner_bio,
            "owner_follower_number": owner_follower_number,
            "owner_viewed_number": owner_viewed_number,
            "sharer_link": sharer_link,
            "sharer_name": sharer_name,
            "sharer_bio": sharer_bio,
            "sharer_follower_number": sharer_follower_number,
            "sharer_viewed_number": sharer_viewed_number,
        }
        pins_data.append(pin_data)
    return pins_data


def save_json(file_path: str, file_name: str, data: list):
    print("converting to json with file name:" + file_name)
    with open(f"{file_path}{file_name}.json", "w", encoding="utf8") as out_data:
        json.dump(data, out_data, ensure_ascii=False)
