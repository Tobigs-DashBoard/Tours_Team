import logging
import os
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_logger(log_file):
    if os.path.exists(log_file):
        os.remove(log_file)

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    return logging.getLogger()

def clean_date(date_str):
    date_format = "%Y.%m.%d %H:%M"
    date_str = date_str.split('(')[0].strip() + ' ' + date_str[-5:].strip()
    return datetime.strptime(date_str, date_format)


def clean_price(price_str):
    if price_str == '문의요망':
        return -1
    return int(price_str.replace(',', '').replace('원', ''))

def scroll_to_element(driver, element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)

def wait_for_element_to_be_visible(driver, element, timeout=10):
    WebDriverWait(driver, timeout).until(EC.visibility_of(element))