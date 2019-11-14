from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

TIMEOUT = 10
URL = 'https://www.premierleague.com'
COLUMN_NAMES = ["name","club" ,"number", "position", "clean_sheets", "nationality", "appearances", "goals", "assists"]

class Player:
    def __init__(self, name="", number="",position="", clean_sheets="" ,nationality="" ,appearances="", goals="0", assists="0", team=""):
        self.name = name
        self.team = team
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
    players = []
    for i in range(len(player_names)):
        info = player_names[i].get_text().split()
        if len(info) > 3:
            number, name, position = info[0], info[1] + ' ' + info[2], info[3]
        else:
            number, name, position = info[0], info[1], info[2]
        p = Player(number=number, name=name, position=position)
        players.append(p)
    player_stats = soup.find_all(class_='squadPlayerStats')

    for i in range(len(player_stats)):
        print(player_stats[i].get_text().split())
        info = player_stats[i].get_text().split()
        j = 1
        nationality = ''
        while info[j] != 'Appearances':
            nationality += info[j] + ' '
        j += 1
        appearances = info[j]
        j += 1
        if len(info[j:]) == 3:
            clean_sheets = info[-1]
            player_stats[i].appearances = appearances
            player_stats[i].clean_sheets = clean_sheets
        elif len(info[j:]) == 5:
            clean_sheets = info[j+2]
            goals = info[-1]
            player_stats[i].appearances = appearances
            player_stats[i].goals = goals
            player_stats[i].clean_sheets = clean_sheets
        elif len(info[j:]) == 4:
            goals = info[j+1]
            assists = info[-1]
            player_stats[i].appearances = appearances
            player_stats[i].goals = goals
            player_stats[i].assists = assists
    return players


#TODO
def write_to_csv(players, team):
    return


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