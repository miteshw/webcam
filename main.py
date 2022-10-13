import selenium
import time
import urllib.request
import io
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pickle
from selenium.webdriver.chrome.options import Options
import shutil
import os
import warnings
from pymongo import MongoClient
warnings.filterwarnings("ignore")

class EpaperExtractor:
    def __init__(self):
        """
        Fetches Credentials from MongoDB
        """
        self.__client = MongoClient("localhost", 27017)
        self.__database = self.__client['credentialsDB']
        self.__collection = self.__database['credentials']
        document = self.__collection.find({"type":"creds"})
        self.username = document.get("Username")
        self.password = document.get("Password")

    def downloadEpaper(self):
        """
        Downloads ePaper clips from website
        """
        options = webdriver.ChromeOptions()
        preferences= {"profile.default_content_settings.popups": 0,"download.default_directory":r".\job\data\hindustan","directory_upgrade": True}
        options.add_experimental_option("prefs",preferences)
        chrome = r'.\webDriver\chromedriver_win32\chromedriver.exe'
        driver= webdriver.Chrome(chrome,chrome_options=options)
        driver.get('https://epaper.hindustantimes.com/Home/ArticleView')
        driver.maximize_window()


        wait = WebDriverWait(driver, 10)
        agree = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div[3]/a[1]')))
        agree.click()

        login=wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[3]/div[4]/div[3]/span[2]/span[1]')))
        login.click()
        time.sleep(5)
        username = driver.find_element_by_xpath("/html/body/div[3]/form/div[3]/input")
        password = driver.find_element_by_xpath("/html/body/div[3]/form/div[5]/input")

        username.send_keys(self.username)
        password.send_keys(self.password)

        driver.find_element_by_xpath('/html/body/div[3]/form/input').click()
        time.sleep(5)

        place=wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[3]/div[4]/div[3]/ul[1]/li[3]/div/span[3]/i")))
        place.click()

        region=[]
        region_list = ['Delhi','Mumbai', 'Pune','Rajasthan','Ranchi'] 
        html_list = driver.find_element_by_id("editionList")
        items = html_list.find_elements_by_tag_name("li")

        for a in range(len(items)):
            items = html_list.find_elements_by_tag_name("li")
            text = items[a].text
            edition_name = text
            region.append(text)
            print(region)
            if any(ele in region for ele in region_list):
                items[a].click()
                time.sleep(5)
                elements = driver.find_elements_by_class_name("pg_thumb_main_div")
                elements=wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "pg_thumb_main_div")))
                for i in range(len(elements)):
                    popup_element = driver.find_element_by_xpath("/html/body/div[7]/div[1]/button")
                    if popup_element.is_displayed():
                        driver.find_element_by_xpath("/html/body/div[7]/div[1]/button").click()
                    elements = driver.find_elements_by_class_name("pg_thumb_main_div")
                    elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "pg_thumb_main_div")))
                    elements[i].click()
                    time.sleep(2)
                    popup_element = driver.find_element_by_xpath("/html/body/div[7]/div[1]/button")
                    if popup_element.is_displayed():
                        driver.find_element_by_xpath("/html/body/div[7]/div[1]/button").click()
                    images = driver.find_elements_by_css_selector("div.pagerectangle")
                    images = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.pagerectangle")))
                    count=0
                    for j in range(len(images)):
                        time.sleep(2)
                        actions = ActionChains(driver)
                        popup_element = driver.find_element_by_xpath("/html/body/div[7]/div[1]/button")
                        if popup_element.is_displayed():
                            driver.find_element_by_xpath("/html/body/div[7]/div[1]/button").click()
                        images = driver.find_elements_by_css_selector("div.pagerectangle")
                        images = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.pagerectangle")))
                        actions.move_to_element(images[j]).click().perform()
                        time.sleep(2)
                        popup_element = driver.find_element_by_xpath("/html/body/div[7]/div[1]/button")
                        if popup_element.is_displayed():
                            driver.find_element_by_xpath("/html/body/div[7]/div[1]/button").click()
                        download=wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[3]/div[4]/div[5]/div/div[3]/div[1]/ul/li[5]/div/span')))
                        download.click()
                        time.sleep(2)
                        count+=1
                source = "./job/data/newsimages/"
                dest = "./job/data/{edition}".format(edition=edition_name)
                files = os.listdir(source)
                for f in files:
                    if os.path.splitext(f)[1] in (".jpg", ".gif", ".png"):
                        shutil.move(source + f, dest)
                place=wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[3]/div[4]/div[3]/ul[1]/li[3]/div/span[3]/i")))
                place.click()
                time.sleep(2)
