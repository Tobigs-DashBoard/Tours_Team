from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import time
import re
import numpy as np
import pandas as pd
from tqdm import tqdm


class InterparkCrawler:
    def __init__(self, departure, country):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument("--window-size=1920x1080")
        self.options.add_argument("--log-level=3")
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=self.options)
        
        self.base_url = f'''
        https://travel.interpark.com/tour/search?category=package&q={country}&domain=r&startDate=&endDate=&departure={departure}
        '''
    
    def get_tour_list(self):
        self.driver.get(self.base_url)
        self.driver.implicitly_wait(3)


        num_clicks = int(int(self.driver.find_element(By.CSS_SELECTOR, '#__next > div > main > div.packageSearchContents.tourCompFilterRight > div.packageSearchResultWrap > div.resultHeader > div.headerTotal').text.split()[1]) / 20)
        button_selector = '#__next > div > main > div.packageSearchContents.tourCompFilterRight > div.packageSearchResultWrap > div.resultContent > button'

        for _ in tqdm(range(num_clicks), desc='Loading pages'):
            try:
                loading_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector))
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", loading_button)
                time.sleep(0.5)
                loading_button.click()
            except ElementClickInterceptedException:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", loading_button)
                time.sleep(0.5)
                loading_button.click()
            except TimeoutException:
                print("Loading button not found or not clickable.")
                break

        self.tour_list = self.driver.find_elements(By.CSS_SELECTOR, '#__next > div > main > div.packageSearchContents.tourCompFilterRight > div.packageSearchResultWrap > div.resultContent > ul > li')

        return self.tour_list

    def get_data(self, item):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of(item)
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", item)

        url = item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
        tags = item.find_element(By.CSS_SELECTOR, 'div.itemInfo > div.badge').text.split('\n')
        title = item.find_element(By.CSS_SELECTOR, 'a > div.itemInfo > div.itemInfoTop > div.itemInfoMain > div.title').text
        schedule = item.find_element(By.CSS_SELECTOR, 'a > div.itemInfo > div.itemInfoTop > div.itemInfoMain > div.place > span:nth-child(1)').text
        price = int(item.find_element(By.CSS_SELECTOR, 'a > div.itemInfo > div.itemInfoTop > div.itemInfoPrice > div > strong').text.replace(',', ''))
        info = item.find_element(By.CSS_SELECTOR, 'a > div.itemInfo > div.itemInfoBottom > div.event').text

        try:
            rating = float(re.sub(r'[()]', '', item.find_element(By.CSS_SELECTOR, 'a > div.itemInfo > div.itemInfoBottom > div.rating > span.star').text.strip()))
        except:
            rating = None

        try:
            reviews = int(item.find_element(By.CSS_SELECTOR, 'a > div.itemInfo > div.itemInfoBottom > div.rating > span.review').text)
        except:
            reviews = None
        
        print(f'''
              URL: {url}
              Tags: {tags}
              Title: {title}
              Schedule: {schedule}
              Price: {price}
              Info: {info}
              Rating: {rating}
              Reviews: {reviews}''')


if __name__ == '__main__':
    crawler = InterparkCrawler('인천', '일본')
    tour_list = crawler.get_tour_list()
    
    '''
    추후 구현 예정사항

    1. 각 상품 페이지에 접속하여 상세 정보 크롤링하는 코드 짜기 (현재는 썸네일 수준)
    2. 크롤링한 데이터를 json 형태로 저장
    3. 일본 뿐만 아니라 더 많은 여행지들 크롤링할 수 있도록 하기
    '''