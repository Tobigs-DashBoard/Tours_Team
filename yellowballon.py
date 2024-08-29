import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import re

want_month = int(input("총 몇 달의 정보를 얻고 싶나요? : "))


# 최종 데이터프레임 초기화
Packages = pd.DataFrame()
Flight = pd.DataFrame()
Hotels = pd.DataFrame()
Itinerary = pd.DataFrame()
Inclusions = pd.DataFrame()

# 데이터를 저장할 리스트들
package_name = []
adult = []
child = []
baby = []
start_date = []
end_date = []
duration = []
all_links = []
airline = []
departure_city = []
departure_time = []
arrival_city = []
arrival_time = []
flight_number = []
hotel = []
all_links_hotel = []
day_hotel = []
all_links_activites = []
date_itinerary = []
city_itinerary = []
day_itinerary = []
package_name_itinerary = []
activities_title= []

# 스크래핑할 URL 설정
url = "https://www.ybtour.co.kr/search/searchPdt.yb?query=%EC%9D%BC%EB%B3%B8"

# 1단계: Selenium WebDriver 초기화 및 총 항목 수 가져오기
driver = webdriver.Chrome()
driver.get(url)

# 검색 결과의 총 개수 추출
contents_num_element = driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div[5]/ul/li[1]/a')
contents_num_text = contents_num_element.text.replace(',', '')  # 쉼표 제거
contents_num_text1 = re.findall(r'\d+', contents_num_text)
inte = int(contents_num_text1[0])  # 검색 결과 수를 정수로 변환
driver.close()

print(inte)

# 2단계: 각 페이지의 링크 수집

k = 1  # 초기 카운터 설정

for j in range(1):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(2)  # 페이지 로드 대기
    driver.find_element(By.XPATH, f'//*[@id="prdtList"]/li[{k}]/a').click()
    time.sleep(2)  # 상세 페이지 로드 대기
    links = driver.find_elements(By.CSS_SELECTOR, 'td.pdt_name > a')

    for link in links:
        href = link.get_attribute('href')  # 각 링크의 href 속성 가져오기
        all_links.append(href)  # 링크 리스트에 추가

# 다음 달 페이지로 넘어가서 수집
    if want_month > 1 :
        for n in range(want_month-1) :
            driver.find_element(By.XPATH, '//*[@id="nextMonthBtn"]').click()
            time.sleep(1)  # 상세 페이지 로드 대기
            links = driver.find_elements(By.CSS_SELECTOR, 'td.pdt_name > a')
            for link in links:
                href = link.get_attribute('href')  # 각 링크의 href 속성 가져오기
                all_links.append(href)  # 링크 리스트에 추가

    time.sleep(2)
    driver.close()
    k += 1  # 다음 페이지로 이동

# 3단계: 수집한 링크를 이용하여 상세 정보 스크래핑
for i in all_links:
    url1 = i
    driver = webdriver.Chrome()
    driver.get(url1)
    time.sleep(1)

#    try:
        # 요소가 존재하는지 확인
#        buttons = driver.find_elements(By.CSS_SELECTOR, "#__next > div:nth-child(1) > div.sc-6550da1b-0.gXWxNL > div.sc-3ed68ec3-0.fmhFPT > div.sc-3ed68ec3-6.kbyXry > div.sc-3ed68ec3-7.PxIhA > div.sc-59819a3c-18.bybwKi > div.sc-59819a3c-31.cSUIvJ > button")

#        if buttons:
            # 버튼이 존재하는 경우 첫 번째 버튼을 가져옴
#            button = buttons[0]

            # JavaScript를 사용하여 해당 버튼으로 스크롤
#            driver.execute_script("arguments[0].scrollIntoView();", button)
#            time.sleep(1)  # 스크롤 완료 후 잠시 대기

            # 버튼 클릭
#           button.click()

#    except NoSuchElementException:
#        pass


    # 제목 추출
    title2 = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div[1]/div[2]/div[1]/div[2]/h2').text.strip()
    title1 = ''
    for n in title2:
        title1 += n
        if n == '#':
            break
    package_name.append(title1)

    # 성인 가격 추출
    pr_adult1 = driver.find_element(By.XPATH,
                                    '//*[@id="__next"]/div[1]/div[1]/div[2]/div[2]/div[2]/div[5]/table/tbody/tr[2]/td[2]/div/em/strong').text.strip()
    adult.append(pr_adult1)

    # 아동 가격 추출
    pr_children1 = driver.find_element(By.XPATH,
                                       '//*[@id="__next"]/div[1]/div[1]/div[2]/div[2]/div[2]/div[5]/table/tbody/tr[2]/td[3]/div/em/strong').text.strip()
    child.append(pr_children1)

    # 유아 가격 추출
    pr_baby1 = driver.find_element(By.XPATH,
                                   '//*[@id="__next"]/div[1]/div[1]/div[2]/div[2]/div[2]/div[5]/table/tbody/tr[2]/td[4]/div/em/strong').text.strip()
    baby.append(pr_baby1)

    # 출발 날짜 추출
    date_go1 = driver.find_element(By.XPATH,
                                   '//*[@id="__next"]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div/ul/li[1]/em').text.strip()
    start_date.append(date_go1)

    # 도착 날짜 추출
    date_come1 = driver.find_element(By.XPATH,
                                     '//*[@id="__next"]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div/ul/li[2]/em').text.strip()
    end_date.append(date_come1)

    # 기간 추출
    duration1 = driver.find_element(By.XPATH,
                                     '//*[@id="__next"]/div[1]/div[1]/div[2]/div[1]/ul/li[1]/span[2]').text.strip()
    duration.append(duration1)

    # 항공사 이름 추출
    airline1 = driver.find_element(By.XPATH,
                                     '//*[@id="__next"]/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[1]/table/tbody/tr[1]/td/div[1]/div/em').text.strip()
    airline.append(airline1)

    #  추출
    departure_city1 = driver.find_element(By.XPATH,
                                     '//*[@id="__next"]/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[2]/div/ul/li[1]/ul/li[1]/span').text.strip()
    departure_city.append(departure_city1)

    #  추출
    departure_time1 = driver.find_element(By.XPATH,
                      '//*[@id="__next"]/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[1]/table/tbody/tr[1]/td/div[2]/div/div[1]/div[1]/span[3]').text.strip()
    departure_time.append(departure_time1)


    #  도착 도시 추출
    arrival_city1= driver.find_element(By.XPATH,
                                       '//*[@id="__next"]/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[2]/div/ul/li[1]/ul/li[2]/span').text.strip()
    arrival_city.append(arrival_city1)

    #  도착 시간 추출
    arrival_time1= driver.find_element(By.XPATH,
                                       '//*[@id="__next"]/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[1]/table/tbody/tr[1]/td/div[2]/div/div[1]/div[2]/span[2]').text.strip()
    arrival_time.append(arrival_time1)

    #  항공기 번호 추출
    flight_number1= driver.find_element(By.XPATH,
                                       '//*[@id="__next"]/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[1]/table/tbody/tr[1]/td/div[2]/div/div[1]/div[1]/span[1]').text.strip()
    flight_number.append(flight_number1)


    # 숙소 정보 추출
    hotel_1_elements = driver.find_elements(By.CSS_SELECTOR, 'dd > a')
    hotel_1_texts = [element.text.strip() for element in hotel_1_elements]  # 요소에서 텍스트 추출

    m = 1
    for p in hotel_1_texts :
        hotel.append(p)
        all_links_hotel.append(i)
        day_hotel.append(m)
        m += 1



    #  일정 정보 추출

    cities = driver.find_elements(By.CSS_SELECTOR, 'div.sc-685bb308-8.fqdeBw > span')
    for city in cities:
        # 날짜 추출
        city_text = city.text

        date_match = re.match(r'^\d{4}\.\d{2}\.\d{2}\(.\)', city_text)
        dates = date_match.group() if date_match else None
        date_itinerary.append(dates)  # 날짜 리스트에 추가

        # 도시 추출
        locations_part = city_text.split(" - ")[1]  # " - "를 기준으로 두 번째 부분 추출
        locations = locations_part.split('/')  # '/'로 장소 구분
        city_itinerary.append(locations)  # 장소 리스트에 추가

    x = 1
    for z in date_itinerary :
        all_links_activites.append(i)
        package_name_itinerary.append(package_name)
        day_itinerary.append(x)
        x += 1



    # 활동 정보 추출

    a=0
    for activity in date_itinerary :
        activities = driver.find_elements(By.CSS_SELECTOR, f"#dayContents[a] > div.sc-685bb308-7.fxdwwo > div.sc-685bb308-20.BXXMG > div > ul > h5")
        activities_text = [element.text.strip() for element in activities]
        activities_title.append(activities_text)
        a += 1





    driver.close()


# 4단계: 수집한 데이터를 DataFrame에 저장

# Packages 테이블
Packages["url"] = all_links
Packages["패키지 이름"] = package_name
Packages["여행 기간"] = duration
Packages["출발 날짜"] = start_date
Packages["종료 날짜"] = end_date
Packages["항공사 이름"] = airline

# Flight 테이블
Flight["url"] = all_links
Flight["출발 도시"] = departure_city
Flight["출발 시간"] = departure_time
Flight["도착 도시"] = arrival_city
Flight["도착 시간"] = arrival_time
Flight["항공편 번호"] = flight_number
Flight["패키지 이름"] = package_name

# Hotels 테이블
Hotels["url"] = all_links_hotel
Hotels["호텔 이름"] = hotel
Hotels["일차"] = day_hotel

# Itinerary 테이블
Itinerary["url"] = all_links_activites
Itinerary["패키지 이름"] = package_name_itinerary
Itinerary["여행 일차"] = day_itinerary
Itinerary["해당 일차의 날짜"] = date_itinerary
Itinerary["방문 도시"] = city_itinerary
Itinerary["당일 활동 제목"] = activities_title


# Inclusions 테이블
Inclusions["url"] = all_links
Inclusions["패키지 이름"] = package_name
Inclusions["성인 가격"] = adult
Inclusions["아동 가격"] = child
Inclusions["유아 가격"] = baby





# 결과 확인
print(Hotels.head(1).to_dict())
