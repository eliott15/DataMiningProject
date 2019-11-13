from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

TIMEOUT = 10
URL = 'https://www.premierleague.com'


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


def scrape_team_stat(driver, url):
    driver.get(url)
    webdriver_wait = WebDriverWait(driver, TIMEOUT)
    condition = EC.presence_of_element_located((By.CLASS_NAME, "stadium"))
    webdriver_wait.until(condition)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    stadium = soup.find(class_='stadium').get_text()
    stat_names = soup.find_all(class_='stat')
    stats = []
    for stat in stat_names:
        stats.append(stat.get_text().split())
    stats = filter(lambda x: len(x) > 1, stats)
    stats = filter(lambda x: x[0] != 'team', stats)
    new_stats = []
    for stat in stats:
        new_stat = ['_'.join(stat[:-1]), stat[-1].strip('"').replace(",", "")]
        new_stats.append(new_stat)
    new_stats = [["Stadium", stadium]] + new_stats
    return new_stats


def scrape_all_teams_stat(driver, urls):
    dictionary = {}
    for url in urls:
        club_name = url.split('/')[-2]
        print("Scrapping data on " + club_name + "...")
        stats = scrape_team_stat(driver, url)
        dictionary[club_name] = stats
    return dictionary


def stats_to_csv(dictionary):
    values = list(dictionary.values())[0]
    number_of_columns = len(values)
    column_names = ["Club"] + [list(dictionary.values())[0][i][0] for i in range(number_of_columns)]
    result = []
    for index, club_name in enumerate(list(dictionary.keys())):
        res = [club_name] + [list(dictionary.values())[index][i][1] for i in range(number_of_columns)]
        result.append(res)
    df = pd.DataFrame(result, columns=column_names)
    df.to_csv("Team_stats.csv", index=False)


def convert_url_to_stats(url):
    words = url.split('/')
    words[-1] = 'stats'
    words[0] = URL
    new_url = '/'.join(words)
    return new_url


def convert_urls_to_stats(urls):
    return list(map(convert_url_to_stats, urls))


def main():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("headless")

    with webdriver.Chrome(chrome_options=chrome_options) as driver:
        urls = scrape_url_team(driver)
    urls = convert_urls_to_stats(urls)
    print(urls)
    with webdriver.Chrome(chrome_options=chrome_options) as driver:
        D = scrape_all_teams_stat(driver, urls)
    stats_to_csv(D)


if __name__ == '__main__':
    main()
