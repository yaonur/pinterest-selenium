from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections.abc import Callable
from time import sleep
from typing import Tuple
from bs4 import BeautifulSoup
import codecs
import os
import json
from PIL import Image
import requests
import modules.global_vars as global_vars


def numeric_to_digit(target_string: str) -> float:
    # print(f"target string is {target_string}")
    if target_string == None or target_string == '' or target_string[0] == 'M':
        return 0
    if not target_string.find(" ") == -1:
        temp_str = target_string[0: target_string.find(" ")]
    else:
        temp_str = target_string
    try:
        return float(temp_str)
    except:
        try:
            numeric = temp_str[-1]
            temp_str = temp_str[0:-1]
            if numeric == "+":
                numeric = temp_str[-1]
                temp_str = temp_str[0:-1]
            zeros = {"k": 1000, "m": 1000000, "b": 1000000000}
            numeric = zeros[numeric.lower()]
            return float(temp_str) * numeric
        except:
            # print("exception at numeric to digit")
            return 0


class Driver:
    driver = None

    @classmethod
    def start_driver(cls, headless=False, proxy=None):
        options = Options()
        if proxy:
            http_proxy = Proxy()
            http_proxy.proxy_type = ProxyType.MANUAL
            http_proxy.http_proxy = proxy
            http_proxy.socks_proxy = proxy
            http_proxy.ssl_proxy = proxy
            http_proxy.add_to_capabilities(options)
        driver_path = GeckoDriverManager().install()
        options.headless = headless
        cls.driver = webdriver.Firefox(executable_path=driver_path, options=options)


class Search:
    @classmethod
    def find_element_class(cls, class_name: str):
        try:
            return Driver.driver.find_element(By.CLASS_NAME, class_name)
        except:
            return ""

    @classmethod
    def find_element_xpath(cls, xpath: str):
        try:
            return Driver.driver.find_element(By.XPATH, xpath)
        except:
            return ""

    @classmethod
    def find_element_xpath_wait(cls, xpath: str, wait_time=4):
        try:
            return WebDriverWait(Driver.driver, wait_time).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
        except:
            return ""

    @classmethod
    def try_to(
            cls, process_function: Callable, number_of_retry: int, sleep_time: int, *args
    ) -> bool:
        for i in range(0, number_of_retry):
            result = process_function(*args)
            sleep(sleep_time)
            if result:
                return True
        return False

    @classmethod
    def try_safe(cls, process_function: Callable, *args) -> None:
        try:
            process_function(*args)
        except:
            pass


class Data:

    @classmethod
    def get_owner_name_and_link(cls, link: str) -> Tuple[str, str]:
        print("starting link " + link)
        Driver.driver.get(link)
        pin_owner_name = None
        pin_owner_link = None
        sleep(4)

        try:
            pin_owner_name = WebDriverWait(Driver.driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, global_vars.pin_owner_name_xpath))).text
            pin_owner_link = (
                WebDriverWait(Driver.driver, 1).until(EC.presence_of_element_located(
                    (By.XPATH, global_vars.pin_owner_link_xpath))).get_attribute("href")
            )
            return pin_owner_link, pin_owner_name
        except:
            print(f"cant find owner name or owner link")
            if pin_owner_name:
                pin_owner_link = "not_pinterest_account"
            return pin_owner_link, pin_owner_name

    @classmethod
    def get_sharer_name_link(cls) -> Tuple[str, str]:
        sharer_name = None
        sharer_link = None

        try:
            for i in range(2):
                sleep(1)
                page_data = BeautifulSoup(Driver.driver.page_source, "html.parser")
                if sharer_name := page_data.find(
                        "a", class_="Wk9 xQ4 CCY czT eEj KhY uCz iyn"
                ):
                    sharer_link = "https://tr.pinterest.com" + sharer_name["href"]
                    sharer_name = sharer_name.text
                    return sharer_link, sharer_name

        except:
            exception_happened = True
            print(
                "*****************exception on getting sharer name or link "
            )
            pass
        print("cant find sharer name and link")
        return sharer_link, sharer_name

    @classmethod
    def get_feed_story(cls):
        try:
            page = BeautifulSoup(Driver.driver.page_source, "html.parser")
            if feed_caption := page.find(
                    "h1", class_="lH1 dyH iFc mWe ky3 pBj zDA IZT"
            ):
                feed_caption = feed_caption.text
            else:
                feed_caption = "no caption"
            if feed_information := page.find_all(
                    "span", class_="tBJ dyH iFc MF7 pBj zDA IZT swG"
            ):
                data = ""
                for span in feed_information:
                    data = data + span.text
                feed_information = data
            else:
                feed_information = "no information"
        except:
            print("***********exception on feed story************")
            feed_caption, feed_information = ""

        return {"feed_caption": feed_caption, "feed_information": feed_information}

    @classmethod
    def get_comments(cls):
        comments = []
        try:
            comment_container = WebDriverWait(Driver.driver, 2).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="canonical-card"]/div[3]/div')
                )
            )
            soup = BeautifulSoup(
                comment_container.get_attribute("innerHTML"), "html.parser"
            )
            soup = soup.find_all(class_="LJB Pw5 Zr3 daS hUC ho- zI7 iyn Hsu")
            for data in soup:
                commenting_user_name = data.find("a").text
                commenting_user_link = (
                        "https//tr.pinterest.com" + data.find("a")["href"]
                )
                comment = data.find("span").text
                comments.append(
                    {
                        "commenting_user_name": commenting_user_name,
                        "commenting_user_link": commenting_user_link,
                        "comment": comment,
                    }
                )
            return comments
        except:
            print("no comments")
            pass

    @classmethod
    def get_image(cls, images_path: str, index: int) -> str:
        source_link=''
        try:
            print("trying image ")
            try:
                source_link = (
                    WebDriverWait(Driver.driver, 1).until(EC.presence_of_element_located(
                        (By.XPATH, global_vars.pin_video_xpath))).get_attribute("poster")
                )
            except:
                soup = BeautifulSoup(Driver.driver.page_source, "html.parser")
                source_link = soup.find("img", class_="hCL kVc L4E MIw")["src"]
                pass
            # image = Image.open(requests.get(source_link, stream=True).raw)
            # image.save(images_path + str(index) + ".png")
        except Exception as e:
            print("image download failed")
            return source_link
        return source_link

    @classmethod
    def get_users_page_data(cls, user_link):
        try:
            Driver.driver.get(user_link)
            user_page = WebDriverWait(Driver.driver, 5).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="__PWS_ROOT__"]/div[1]/div[2]/div/div/div/div[1]/div/div',
                    )
                )
            )

            try:
                user_bio = WebDriverWait(Driver.driver, 4).until(
                    EC.presence_of_element_located((By.XPATH, global_vars.user_bio))).text
            except:
                print("no user bio")
                user_bio = ""
                pass

            try:
                user_follower_number = WebDriverWait(Driver.driver, 4).until(
                    EC.presence_of_element_located((By.XPATH, global_vars.user_follower_num))).text
                user_follower_number = numeric_to_digit(user_follower_number)
            except:
                print("exception at getting user follower number")
                user_follower_number = ""
                pass

            try:
                user_viewed_number = WebDriverWait(Driver.driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, global_vars.user_viewed_num))).text
                user_viewed_number = numeric_to_digit(user_viewed_number)
            except:
                print("exception at getting user viewed number")
                user_viewed_number = ""
                pass
        except Exception as e:
            print("Exception at getting user data inner")
            user_bio = ""
            user_follower_number = ""
            user_viewed_number = ""
            pass
        return user_bio, user_follower_number, user_viewed_number

    @classmethod


    @classmethod
    def save_page(cls, file_name):
        path = os.getcwd() + "/"
        file_object = codecs.open(path + file_name, "w", "utf-8")
        html = Driver.driver.page_source
        file_object.write(html)

    @classmethod
    def remove_spaces(cls, word):
        return word.replace(" ", "_")


class Decorators:
    pass
