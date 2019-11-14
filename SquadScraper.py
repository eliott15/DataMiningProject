from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

TIMEOUT = 10
URL = 'https://www.premierleague.com'


class Player:
    def __init__(self, name="", number="",position="", clean_sheets="" ,nationality="" ,appearances="", goals="0", assists="0"):
        self.name = name
        self.number = number
        self.position = position
        self.nationality = nationality
        self.appearances = appearances
        self.clean_sheets = clean_sheets
        self.goals = goals
        self.assists = assists


def scrape_url_team(driver):
    """Scrape all match results for specified, competition, season and team"""
    urls = []
    driver.get('https://www.premierleague.com/clubs')
    webdriver_wait = WebDriverWait(driver, TIMEOUT)
    condition = EC.presence_of_element_located((By.CLASS_NAME, "indexBadge"))
    webdriver_wait.until(condition)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    tags = soup.find_all('a', class_='indexItem', href=True)
    for tag in tags:
        url = tag['href']
        urls.append(url)
    return urls


def convert_url_to_stats(url):
    words = url.split('/')
    words[-1] = 'squad'
    words[0] = URL
    new_url = '/'.join(words)
    return new_url


def convert_urls_to_stats(urls):
    return list(map(convert_url_to_stats, urls))


def scrape_team_squad(driver, url):
    driver.get(url)
    webdriver_wait = WebDriverWait(driver, TIMEOUT)
    condition = EC.presence_of_element_located((By.CLASS_NAME, "playerCardInfo"))
    webdriver_wait.until(condition)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    player_names = soup.find_all(class_='playerCardInfo')
    print(player_names[0].get_text().split())
    print(player_names[-1])
    players = []
    for i in range(len(player_names)):
        info = player_names[i].get_text().split()
        if len(info) > 3:
            number, name, position = info[0], info[1] + ' ' + info[2], info[3]
        else:
            number, name, position = info[0], info[1], info[2]
        p = Player(number=number, name = name, position=position)
        players.append(p)



def main():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("headless")

    with webdriver.Chrome(chrome_options=chrome_options) as driver:
        urls = scrape_url_team(driver)
    urls = convert_urls_to_stats(urls)
    with webdriver.Chrome(chrome_options=chrome_options) as driver:
        scrape_team_squad(driver, urls[0])


if __name__ == '__main__':
    main()