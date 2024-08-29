import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import argparse
from datetime import datetime, timedelta
from configs import (SEA_regions, NEA_regions, MEA_regions, AUS_regions, EUR_regions, AME_regions, korean_airports,
                     package_columns, flight_columns, hotel_columns, itinerary_columns, inclusion_columns)
from utils import setup_logger, clean_date, clean_price, scroll_to_element, wait_for_element_to_be_visible

logger = setup_logger('interpark.log')

class InterparkCrawler:
    def __init__(self, args):
        logger.info("Initializing the InterparkCrawler")
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument("--window-size=1920x1080")
        self.options.add_argument("--log-level=3")
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=self.options)
        
        self.package_df = pd.DataFrame(columns=package_columns)
        self.flight_df = pd.DataFrame(columns=flight_columns)
        self.hotel_df = pd.DataFrame(columns=hotel_columns)
        self.itinerary_df = pd.DataFrame(columns=itinerary_columns)
        self.inclusion_df = pd.DataFrame(columns=inclusion_columns)
        self.checkpoint_dir = args.ckpt_dir
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        self.load_checkpoint()

    def load_checkpoint(self):
        """이전 체크포인트가 존재하면 데이터를 불러와서 데이터프레임에 저장."""
        try:
            latest_checkpoint = max([f for f in os.listdir(self.checkpoint_dir) if f.endswith('.csv')], key=lambda x: os.path.getmtime(os.path.join(self.checkpoint_dir, x)))
            logger.info(f"Loading checkpoint: {latest_checkpoint}")
            self.package_df = pd.read_csv(f'{self.checkpoint_dir}/packages_{latest_checkpoint}.csv')
            self.flight_df = pd.read_csv(f'{self.checkpoint_dir}/flights_{latest_checkpoint}.csv')
            self.hotel_df = pd.read_csv(f'{self.checkpoint_dir}/hotels_{latest_checkpoint}.csv')
            self.itinerary_df = pd.read_csv(f'{self.checkpoint_dir}/itinerary_{latest_checkpoint}.csv')
            self.inclusion_df = pd.read_csv(f'{self.checkpoint_dir}/inclusions_{latest_checkpoint}.csv')
        except (ValueError, FileNotFoundError):
            logger.warning("No checkpoint found. Starting from scratch.")

    def get_tour_list(self, region, departure):
        logger.info(f"Fetching tour list for region: {region}, departure: {departure}")
        self.url = f'''
        https://travel.interpark.com/tour/search?category=package&q={region}&domain=r&startDate=&endDate=&departure={departure}
        '''
        self.driver.get(self.url)
        self.driver.implicitly_wait(3)

        num_clicks = int(self.driver.find_element(By.CSS_SELECTOR, '#__next > div > main > div.packageSearchContents.tourCompFilterRight > div.packageSearchResultWrap > div.resultContent > button > span').text.split('/')[1]) - 1
        button_selector = '#__next > div > main > div.packageSearchContents.tourCompFilterRight > div.packageSearchResultWrap > div.resultContent > button'

        for _ in range(num_clicks):
            try:
                loading_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector))
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", loading_button)
                time.sleep(0.5)
                loading_button.click()
            except:
                logger.info("No more pages to load or error occurred while loading more pages")
                break

        self.tour_list = self.driver.find_elements(By.CSS_SELECTOR, '#__next > div > main > div.packageSearchContents.tourCompFilterRight > div.packageSearchResultWrap > div.resultContent > ul > li')

        logger.info(f"Found {len(self.tour_list)} tours")
        return self.tour_list

    def get_data(self, item):
        self.start_time = time.time()
        try:
            target_url = item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            package_id = target_url.lower().split('goodscd=')[1]

            # 이미 처리된 패키지인지 확인
            if len(self.package_df) != 0:
                if package_id in self.package_df['package_id'].values:
                    logger.info(f"Skipping already processed package: {package_id}")
                    return None, None, None, None, None

            self.driver.get(target_url)
            self.driver.implicitly_wait(2)

            price_block = self.driver.find_element(By.CSS_SELECTOR, '#__next > div > section > div.detail > div.detailReservation > div > div.selectOptionWrap > div > div.selectOption > div.detailOptionWrap > div > details > div').text.split('\n')
            price_original, child_price, infant_price = map(clean_price, [price_block[1], price_block[3], price_block[5]])

            # Package table contents
            package_name = self.driver.find_element(By.CSS_SELECTOR, '#__next > div > section > article > div.mainInfo > div.mainInfoDetail > div.productTitle > h2').text
            duration = self.driver.find_element(By.CSS_SELECTOR, '#__next > div > section > div.detail > div.detailContent > article.detailTravel > div > div:nth-child(1) > ul > li:nth-child(3) > span').text

            start_departure_time, start_flight_number = self.driver.find_element(By.CSS_SELECTOR, '#__next > div > section > div.detail > div.detailContent > article.detailTravel > div > div:nth-child(3) > dl:nth-child(2) > dd').text.split('/')
            end_arrival_time, end_flight_number = self.driver.find_element(By.CSS_SELECTOR, '#__next > div > section > div.detail > div.detailContent > article.detailTravel > div > div:nth-child(3) > dl:nth-child(3) > dd').text.split('/')
            start_date = clean_date(start_departure_time).date().strftime('%Y-%m-%d')
            end_date = clean_date(end_arrival_time).date().strftime('%Y-%m-%d')

            package_dict = {'package_id': package_id,
                            'package_name': package_name,
                            'duration': duration,
                            'start_date': start_date,
                            'end_date': end_date,
                            'price_original': price_original}

            # Flight table contents
            start_departure_time = clean_date(start_departure_time).strftime('%Y-%m-%d %H:%M:%S')
            end_arrival_time = clean_date(end_arrival_time).strftime('%Y-%m-%d %H:%M:%S')
            airline = self.driver.find_element(By.CSS_SELECTOR, '#__next > div > section > div.detail > div.detailContent > article.detailTravel > div > div:nth-child(3) > dl:nth-child(1) > dd').text

            flight_dict = {
                            'package_id': package_id,
                            'start_departure_time': start_departure_time,
                            'start_arrival_time': None,
                            'end_departure_time': None,
                            'end_arrival_time': end_arrival_time,
                            'start_flight_number': start_flight_number,
                            'end_flight_number': end_flight_number,
                            'airline': airline}

            # Activate schedule tab
            intro_tab = self.driver.find_element(By.CSS_SELECTOR, '#divTabContent > div:nth-child(1)')
            schedule_tab = self.driver.find_element(By.CSS_SELECTOR, '#divTabContent > div:nth-child(2)')
            self.driver.execute_script("arguments[0].setAttribute('class', 'tabPanel active')", schedule_tab)
            self.driver.execute_script("arguments[0].setAttribute('class', 'tabPanel')", intro_tab)

            # Hotel table contents
            hotel_dict = {}
            try:
                hotel_list = self.driver.find_elements(By.CLASS_NAME, 'dataBed')
                for day, hotel_candidates in enumerate(hotel_list):
                    if type(hotel_candidates) == list:  
                        for hotel in hotel_candidates:
                            hotel_name = hotel.text   
                            hotel_link = hotel.get_attribute('href') 
                            hotel_dict[day+1] = (hotel_name, hotel_link)
                    else:
                        hotel_name = hotel_candidates.text
                        hotel_link = hotel_candidates.get_attribute('href')
                        hotel_dict[day+1] = (hotel_name, hotel_link)
            except Exception as e:
                logger.warning(f"Failed to fetch hotel data: {e}")
                hotel_dict = None

            # Itinerary table contents
            schedule_dict = {}
            try:
                schedule_list = self.driver.find_elements(By.CLASS_NAME, 'scheduleInfoList')  # 1~N일차 일정 리스트
                for day, schedule in enumerate(schedule_list):
                    activities = f'{day+1}일차 일정'
                    activity_list = schedule.find_elements(By.CSS_SELECTOR, 'ul > li')
                    for activity in activity_list:
                        try:
                            activity_name_element = activity.find_element(By.CSS_SELECTOR, 'li > h4')
                            scroll_to_element(self.driver, activity_name_element)  # 요소가 보일 때까지 스크롤
                            wait_for_element_to_be_visible(self.driver, activity_name_element)  # 요소가 보일 때까지 기다림
                            activity_name = activity_name_element.text
                            activities = "\n".join([activities, activity_name])
                        except Exception as e:
                            logger.warning(f"Failed to fetch activity name: {e}")
                    schedule_dict[day+1] = activities
            except Exception as e:
                logger.warning(f"Failed to fetch itinerary data: {e}")
                schedule_dict = None


            # Inclusion table contents
            inclusion_dict = {'package_id': package_id,
                              'adult': price_original,
                              'child': child_price,
                              'baby': infant_price}

            logger.info(f"Fetched data for package: {package_id}, time spent: {time.time() - self.start_time:.2f} seconds")
            return package_dict, flight_dict, hotel_dict, schedule_dict, inclusion_dict
        except Exception as e:
            logger.error(f"Error: {e} from {target_url}")
            return None, None, None, None, None

    def save_checkpoint(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        logger.info(f"Saving checkpoint at {timestamp}")
        self.package_df.to_csv(f'{self.checkpoint_dir}/packages_{timestamp}.csv', index=False)
        self.flight_df.to_csv(f'{self.checkpoint_dir}/flights_{timestamp}.csv', index=False)
        self.hotel_df.to_csv(f'{self.checkpoint_dir}/hotels_{timestamp}.csv', index=False)
        self.itinerary_df.to_csv(f'{self.checkpoint_dir}/itinerary_{timestamp}.csv', index=False)
        self.inclusion_df.to_csv(f'{self.checkpoint_dir}/inclusions_{timestamp}.csv', index=False)

    def quit(self):
        logger.info("Shutting down the crawler")
        self.driver.quit()

def get_args():
    parser = argparse.ArgumentParser(description='Interpark Crawler')
    parser.add_argument('--ckpt_dir', type=str, default='./checkpoint', help='checkpoint directory')
    parser.add_argument('--ckpt_int', type=int, default=50, help='checkpoint interval')
    return parser.parse_args()


if __name__ == '__main__':
    target_regions = ['일본']

    args = get_args()
    CHECKPOINT_INTERVAL = args.ckpt_int

    crawler = InterparkCrawler(args)

    for region in target_regions:
        for airport in korean_airports:
            logger.info(f"Processing region: {region}, airport: {airport}")
            tour_list = crawler.get_tour_list(region, airport)
            for idx, item in enumerate(tour_list):
                package_dict, flight_dict, hotel_dict, schedule_dict, inclusion_dict = crawler.get_data(item)
                if package_dict and flight_dict and inclusion_dict:

                    # Append data to DataFrames
                    crawler.package_df = pd.concat([crawler.package_df, pd.DataFrame(package_dict)], ignore_index=True)
                    crawler.inclusion_df = pd.concat([crawler.inclusion_df, pd.DataFrame(inclusion_dict)], ignore_index=True)
                    crawler.flight_df = pd.concat([crawler.flight_df, pd.DataFrame({'package_id': package_dict['package_id'],
                                                                                    'departure_city': airport,
                                                                                    'departure_time': flight_dict['start_departure_time'],
                                                                                    'arrival_city': region,
                                                                                    'arrival_time': flight_dict['start_arrival_time'],
                                                                                    'flight_number': flight_dict['start_flight_number'],
                                                                                    'airline': flight_dict['airline']}, index=[0])], ignore_index=True)

                    crawler.flight_df = pd.concat([crawler.flight_df, pd.DataFrame({'package_id': package_dict['package_id'],
                                                                                    'departure_city': region,
                                                                                    'departure_time': flight_dict['end_departure_time'],
                                                                                    'arrival_city': airport,
                                                                                    'arrival_time': flight_dict['end_arrival_time'],
                                                                                    'flight_number': flight_dict['end_flight_number'],
                                                                                    'airline': flight_dict['airline']}, index=[0])], ignore_index=True)

                    if hotel_dict:
                        for day, hotels in hotel_dict.items():
                            for hotel_name, hotel_link in hotels.items():
                                crawler.hotel_df = pd.concat([crawler.hotel_df, pd.DataFrame({'package_id': package_dict['package_id'], 'hotel_name': hotel_name, 'hotel_link': hotel_link, 'day': day}, index=[0])], ignore_index=True)
                    if schedule_dict:
                        for day, activities in schedule_dict.items():
                            date = package_dict['start_date'] + timedelta(days=day-1)
                            date = date.strftime('%Y-%m-%d')
                            crawler.itinerary_df = pd.concat([crawler.itinerary_df, pd.DataFrame({'package_id': package_dict['package_id'], 'day': day, 'date': date, 'activities_title': activities}, index=[0])], ignore_index=True)

                    if idx > 0 and idx % CHECKPOINT_INTERVAL == 0:
                        crawler.save_checkpoint()

    crawler.quit()
