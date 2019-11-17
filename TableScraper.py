from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
from bs4 import BeautifulSoup
import pandas as pd
from argparse import ArgumentParser
import sys

TIMEOUT = 3
PAUSE_TIME = 2
COLUMN_NUMBER = 10


def set_filters(driver, season, match_week, home_or_away):
    """Set required filters to get the right result page"""

    if season:
        try:
            season_elem = driver.find_element(By.CSS_SELECTOR, f"li[data-option-name='{season}']")
        except NoSuchElementException:
            print(f"Error: Season '{season}' was not found. Please choose from the following list:")
            soup = BeautifulSoup(driver.page_source, "html.parser")
            current_season = soup.find(class_="dropdownList", attrs={"data-dropdown-list": "compSeasons"})
            season_list = current_season.find_all('li')
            for season_ in season_list:
                print(season_.get_text())
            sys.exit(1)
        driver.execute_script("arguments[0].click();", season_elem)
        time.sleep(PAUSE_TIME)

    if match_week:
        try:
            match_week_elem = driver.find_element(By.CSS_SELECTOR, f"li[data-option-name='{match_week}']")
        except NoSuchElementException:
            print(f"Error: Match week '{match_week}' was not found. Please choose from the following list:")
            soup = BeautifulSoup(driver.page_source, "html.parser")
            current_match_week = soup.find(class_="dropdownList", attrs={"data-dropdown-list": "gameweekNumbers"})
            match_week_list = current_match_week.find_all('li')
            for match_week_ in match_week_list:
                print(match_week_.get_text())
            sys.exit(1)
        driver.execute_script("arguments[0].click();", match_week_elem)
        time.sleep(PAUSE_TIME)

    if home_or_away:
        try:
            home_or_away_elem = driver.find_element(By.CSS_SELECTOR, f"li[data-option-name='{home_or_away}']")
        except NoSuchElementException:
            print(f"Error: Matches type '{home_or_away}' was not found. Please choose from the following list:")
            soup = BeautifulSoup(driver.page_source, "html.parser")
            current_home_or_away = soup.find(class_="dropdownList", attrs={"data-dropdown-list": "homeaway"})
            home_or_away_list = current_home_or_away.find_all('li')
            for home_or_away_ in home_or_away_list:
                print(home_or_away_.get_text())
            sys.exit(1)
        driver.execute_script("arguments[0].click();", home_or_away_elem)
        time.sleep(PAUSE_TIME)


def get_current_filters(driver):
    """Returns the filters for current page"""
    soup = BeautifulSoup(driver.page_source, "html.parser")
    current_season = soup.find(class_="current", attrs={"data-dropdown-current": "compSeasons"})
    season = current_season.get_text().strip("\"").replace("/", "-")
    current_match_week = soup.find(class_="current", attrs={"data-dropdown-current": "gameweekNumbers"})
    match_week = current_match_week.get_text().strip("\"")
    current_home_or_away = soup.find(class_="current", attrs={"data-dropdown-current": "homeaway"})
    home_or_away = current_home_or_away.get_text().strip("\"")
    return season, match_week, home_or_away


def scrape_table(driver, season, match_week, home_or_away):
    """Scrapes the Premier League table according to given filters"""

    table = []
    table_headers = []
    driver.get('https://www.premierleague.com/tables')

    try:
        webdriver_wait = WebDriverWait(driver, TIMEOUT)
        condition = EC.presence_of_element_located((By.CLASS_NAME, "mainTableTab active"))
        webdriver_wait.until(condition)
    except TimeoutException:
        pass

    set_filters(driver, season, match_week, home_or_away)

    season, match_week, home_or_away = get_current_filters(driver)

    print(f"Scraping table for season {season}, match week {match_week}, match type {home_or_away}")

    soup = BeautifulSoup(driver.page_source, "html.parser")
    table_tag = soup.find(class_="mainTableTab active")
    header = table_tag.find("thead")
    for column in header.find_all("th"):
        thFull = column.find(class_="thFull")
        if thFull:
            column_header = thFull.get_text()
        else:
            column_header = column.get_text()
        table_headers.append(column_header)
    offset = 0
    if table_headers[0] == "More":
        offset = 1
    table_headers = table_headers[offset:COLUMN_NUMBER + offset]

    body = table_tag.find("tbody")
    for row in body.find_all("tr"):
        if row.get("class") and row.get("class")[0] == "expandable":
            continue
        else:
            table_line = []
            for cell in row.find_all("td"):
                value = cell.find(class_="value")
                if value:
                    cell_content = value.get_text()
                else:
                    long = cell.find(class_="long")
                    if long:
                        cell_content = long.get_text()
                    else:
                        cell_content = cell.get_text()
                table_line.append(cell_content)
            table_line = table_line[offset:COLUMN_NUMBER + offset]
            table.append(table_line)

    df = pd.DataFrame(table, columns=table_headers)
    filename = f"table_Premier League_{season}_{match_week}_{home_or_away}.csv"
    df.to_csv(filename, index=False)
    return filename


def main():
    parser = ArgumentParser()

    parser.add_argument("--season", action="store", default="", nargs='+')
    parser.add_argument("--match_week", action="store", default="", nargs='+')
    parser.add_argument("--home_or_away", action="store", default="", nargs='+')
    args = parser.parse_args()
    season = ' '.join(args.season)
    match_week = ' '.join(args.match_week)
    home_or_away = ' '.join(args.home_or_away)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("headless")
    with webdriver.Chrome(chrome_options=chrome_options) as driver:
        filename = scrape_table(driver, season, match_week, home_or_away)
        print(f"Successfully scraped table to {filename}")


if __name__ == "__main__":
    main()
