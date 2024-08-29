import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup
import re

# 최종으로 만들 데이터 프레임
Yellowballon_df = pd.DataFrame(
                      columns=["url", "제목", "성인가격", "아동가격", "유아가격", "출발일시", "도착일시"])

title = []
pr_adult = []
pr_children =[]
pr_baby = []
date_go = []
date_come = []
feature = []
nanocity = []

url = "https://www.ybtour.co.kr/search/searchPdt.yb?query=%EC%9D%BC%EB%B3%B8"
driver = webdriver.Chrome()
driver.get(url)

contents_num_element = driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div[5]/ul/li[1]/a')
contents_num_text = contents_num_element.text.replace(',', '')  # 쉼표 제거
contents_num_text1 = re.findall(r'\d+', contents_num_text)
inte=int(contents_num_text1[0])
k=1
driver.close()

print(inte)

links=[]
all_links=[]

for j in range(inte):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(2)
    driver.find_element(By.XPATH,f'//*[@id="prdtList"]/li[{k}]/a').click()
    time.sleep(2)
    links = driver.find_elements(By.CSS_SELECTOR, 'td.pdt_name > a')
    for link in links:
        href = link.get_attribute('href')
        all_links.append(href)
    time.sleep(2)
    driver.close()
    k = k + 1


for i in all_links:
    url1=i
    driver = webdriver.Chrome()
    driver.get(url1)

    #제목
    title2=driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div[1]/div[2]/div[1]/div[2]/h2').text.strip()
    title1 = ''
    for n in title2:
        title1 += n
        if n=='#':
            break;
    title.append(title1)

    #어른 가격
    pr_adult1=driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div[1]/div[2]/div[2]/div[2]/div[5]/table/tbody/tr[2]/td[2]/div/em/strong').text.strip()
    pr_adult.append(pr_adult1)

    #아동 가격
    pr_children1=driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div[1]/div[2]/div[2]/div[2]/div[5]/table/tbody/tr[2]/td[3]/div/em/strong').text.strip()
    pr_children.append(pr_children1)

    #유아 가격
    pr_baby1=driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div[1]/div[2]/div[2]/div[2]/div[5]/table/tbody/tr[2]/td[4]/div/em/strong').text.strip()
    pr_baby.append(pr_baby1)

    #날짜
    date_go1 = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div/ul/li[1]/em').text.strip()
    date_go.append(date_go1)

    date_come1 = driver.find_element(By.XPATH,'//*[@id="__next"]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div/ul/li[2]/em').text.strip()
    date_come.append(date_come1)

Yellowballon_df["url"] = all_links
Yellowballon_df["제목"] = title
Yellowballon_df["성인가격"] = pr_adult
Yellowballon_df["아동가격"] = pr_children
Yellowballon_df["유아가격"] = pr_baby
Yellowballon_df["출발일시"] = date_go
Yellowballon_df["도착일시"] = date_come

Yellowballon_df.head(1).to_dict()