import os
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
from bs4 import BeautifulSoup
import pandas as pd
import csv
from argparse import ArgumentParser
import sys

TIMEOUT = 3
SCORE_HOME = 0
SCORE_AWAY = 2
RESULTS_COLUMNS = ["Match ID", "Date", "Home Team", "Away Team", "Stadium", "Home Score", "Away Score"]
STATS_COLUMNS = ["Match ID", "Referee", "Attendance", "Kick Off", "HT Score", "Home Goals", "Home RC events",
                 "Away Goals", "Away RC events", "Home Assists", "Away Assists", "King of the Match"]
PAUSE_TIME = 2


def parse_events(events):
    """Parse an event to Goal or Red Card"""
    goals = ""
    red_cards = ""
    for event in events:
        event_list = event.get_text().split()
        if event_list[-1] == "Goal" or event_list[-1] == "label.penalty.scored":
            if goals != "":
                goals += "\n"
            goals += " ".join(event_list[:-1])
        elif event_list[-1] == "Card":
            if red_cards != "":
                red_cards += "\n"
            red_cards += " ".join(event_list[:-2])
        elif event_list[-1] == "Card)":
            if red_cards != "":
                red_cards += "\n"
            red_cards += " ".join(event_list[:-5])
    return goals, red_cards


def parse_assists(events):
    """Parse Assists events"""
    assists = ""
    for event in events:
        event_list = event.get_text().split()
        if assists != "":
            assists += "\n"
        assists += " ".join(event_list)
    return assists


def scrape_match_stats(driver, match_id):
    """Scrape the stats for a specific match"""
    print(f"Scraping match stats for match_id: {match_id}")
    driver.get("https://www.premierleague.com/match/" + match_id)
    webdriver_wait = WebDriverWait(driver, TIMEOUT)

    try:
        condition = EC.presence_of_element_located((By.CLASS_NAME, "kotm-player__first-name"))
        webdriver_wait.until(condition)
        has_king_of_match = True
    except TimeoutException:
        has_king_of_match = False

    soup = BeautifulSoup(driver.page_source, "html.parser")

    referee = soup.find(class_="referee").get_text().strip(" \n")
    attendance = soup.find(class_="attendance hide-m").get_text().replace("Att: ", "")
    kick_off = soup.find(class_="renderKOContainer").get_text()
    half_time_score = soup.find(class_="halfTime").get_text().split()[3]

    events = soup.find(class_="matchEvents matchEventsContainer")
    home_events = events.find(class_="home")
    away_events = events.find(class_="away")
    home_goals, home_red_cards, away_goals, away_red_cards = "", "", "", ""
    if len(list(home_events.children)) > 1:  # Checks if events have children other than '\n'
        home_goals, home_red_cards = parse_events(home_events.find_all(class_="event"))
    if len(list(away_events.children)) > 1:
        away_goals, away_red_cards = parse_events(away_events.find_all(class_="event"))

    home_assists_list = soup.find(class_="assists").find(class_="home")
    away_assists_list = soup.find(class_="assists").find(class_="away")
    home_assists, away_assists = "", ""
    if len(list(home_assists_list.children)) > 1:  # Checks if events have children other than '\n'
        home_assists = parse_assists(home_assists_list.find_all(class_="event"))
    if len(list(away_assists_list.children)) > 1:
        away_assists = parse_assists(away_assists_list.find_all(class_="event"))

    if has_king_of_match:
        king_of_the_match = soup.find(class_="kotm-player__first-name").get_text() + " " \
                            + soup.find(class_="kotm-player__second-name").get_text()
    else:
        king_of_the_match = ""

    stat_tab = driver.find_element(By.CSS_SELECTOR, "li[role='tab'][data-tab-index='2']")
    stat_tab.click()

    has_stats = False
    try:
        condition = EC.presence_of_element_located((By.CSS_SELECTOR, "tbody[class='matchCentreStatsContainer'] > tr"))
        webdriver_wait = WebDriverWait(driver, TIMEOUT)
        webdriver_wait.until(condition)
        has_stats = True
    except TimeoutException:
        pass

    stats_list = []
    stats_columns_list = []

    if has_stats:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        stats_container = soup.find(class_="matchCentreStatsContainer")
        stat_lines = stats_container.find_all("tr")
        has_yellow_cards = False
        has_red_cards = False
        has_offsides = False
        for stat_line in stat_lines:
            stat_columns = list(stat_line.find_all("td"))
            if stat_columns[1].get_text() == "Yellow cards":
                has_yellow_cards = True
            if stat_columns[1].get_text() == "Red cards":
                has_red_cards = True
            if stat_columns[1].get_text() == "Offsides":
                has_offsides = True
            if not has_offsides and (stat_columns[1].get_text() == "Yellow cards" or
                                     stat_columns[1].get_text() == "Red cards" or
                                     stat_columns[1].get_text() == "Fouls conceded"):
                stats_columns_list.append("Home Offsides")
                stats_columns_list.append("Away Offsides")
                stats_list.append("0")
                stats_list.append("0")
                has_offsides = True
            if not has_yellow_cards and (
                    stat_columns[1].get_text() == "Red cards" or stat_columns[1].get_text() == "Fouls conceded"):
                stats_columns_list.append("Home Yellow cards")
                stats_columns_list.append("Away Yellow cards")
                stats_list.append("0")
                stats_list.append("0")
                has_yellow_cards = True
            if not has_red_cards and stat_columns[1].get_text() == "Fouls conceded":
                stats_columns_list.append("Home Red cards")
                stats_columns_list.append("Away Red cards")
                stats_list.append("0")
                stats_list.append("0")
            stats_columns_list.append("Home " + stat_columns[1].get_text())
            stats_columns_list.append("Away " + stat_columns[1].get_text())
            stats_list.append(stat_columns[0].get_text())
            stats_list.append(stat_columns[2].get_text())
    return stats_columns_list, [match_id, referee, attendance, kick_off, half_time_score, home_goals, home_red_cards,
                                away_goals,
                                away_red_cards, home_assists, away_assists, king_of_the_match] + stats_list


def scrape_all_match_stats(driver, competition, season, team, filename):
    """Scrapes all the stats for the matches in match_results.csv"""
    stats = []
    if not filename:
        driver.get('https://www.premierleague.com/results')
        webdriver_wait = WebDriverWait(driver, TIMEOUT)
        condition = EC.presence_of_element_located((By.CLASS_NAME, "fixtures__matches-list"))
        webdriver_wait.until(condition)

        set_filters(driver, competition, season, team)

        competition, season, team = get_current_filters(driver)
        filename = f"match_results_{competition}_{season}_{team}.csv"
    if not os.path.exists(filename):
        print(f"Error: {filename} does not exist.\n"
              "Please choose 'results' or 'all' to scrape results for specified filters before scraping stats.")
        sys.exit(1)
    with open(filename, 'r') as results_file:
        match_results = csv.DictReader(results_file)
        for match_result in match_results:
            columns_to_add, match_stats = scrape_match_stats(driver, match_result['Match ID'])
            stats.append(match_stats)

    stats_columns_whole = STATS_COLUMNS + columns_to_add
    df = pd.DataFrame(stats, columns=stats_columns_whole)
    filename = filename.replace("results", "stats")
    df.to_csv(filename, index=False)
    return filename


def get_current_filters(driver):
    """Returns the filters for current page"""
    soup = BeautifulSoup(driver.page_source, "html.parser")
    current_comp = soup.find(class_="current", attrs={"data-dropdown-current": "comps"})
    competition = current_comp.get_text().strip("\"")
    current_season = soup.find(class_="current", attrs={"data-dropdown-current": "compSeasons"})
    season = current_season.get_text().strip("\"").replace("/", "-")
    if len(season) > 7:
        season = re.search(r'(\d\d\d\d-)\d\d(\d\d)', season)
        season = season.group(1) + season.group(2)
    current_team = soup.find(class_="current", attrs={"data-dropdown-current": "teams"})
    team = current_team.get_text().strip("\"")
    return competition, season, team


def set_filters(driver, competition, season, team):
    """Set required filters to get the right result page"""
    if competition:
        try:
            comp_elem = driver.find_element(By.CSS_SELECTOR, f"li[data-option-name='{competition}']")
        except NoSuchElementException:
            print(f"Error: Competition '{competition}' was not found. Please choose from the following list:")
            soup = BeautifulSoup(driver.page_source, "html.parser")
            current_comp = soup.find(class_="dropdownList", attrs={"data-dropdown-list": "comps"})
            comp_list = current_comp.find_all('li')
            for comp in comp_list:
                print(comp.get_text())
            sys.exit(1)
        driver.execute_script("arguments[0].click();", comp_elem)
        time.sleep(PAUSE_TIME)

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

    if team:
        try:
            team_elem = driver.find_element(By.CSS_SELECTOR, f"li[data-option-name='{team}']")
        except NoSuchElementException:
            print(f"Error: Team '{team}' was not found. Please choose from the following list:")
            soup = BeautifulSoup(driver.page_source, "html.parser")
            current_team = soup.find(class_="dropdownList", attrs={"data-dropdown-list": "teams"})
            team_list = current_team.find_all('li')
            for team_ in team_list:
                print(team_.get_text())
            sys.exit(1)
        driver.execute_script("arguments[0].click();", team_elem)
        time.sleep(PAUSE_TIME)


def scrape_match_results(driver, competition, season, team):
    """Scrape all match results for specified, competition, season and team"""

    results = []
    driver.get('https://www.premierleague.com/results')
    webdriver_wait = WebDriverWait(driver, TIMEOUT)
    condition = EC.presence_of_element_located((By.CLASS_NAME, "fixtures__matches-list"))
    webdriver_wait.until(condition)

    set_filters(driver, competition, season, team)

    competition, season, team = get_current_filters(driver)

    print("Scraping match results for:")
    print(f"Competition: {competition}")
    print(f"Season: {season}")
    print(f"Team: {team}")

    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    soup = BeautifulSoup(driver.page_source, "html.parser")
    matches_by_date = soup.find_all(class_="fixtures__matches-list")
    for match_by_date in matches_by_date:
        match_date = match_by_date["data-competition-matches-list"]
        matches = match_by_date.find_all(class_="matchFixtureContainer")
        for match in matches:
            score = match.find(class_="score")
            scores = list(score.children)
            match_id = match["data-comp-match-item"]
            results.append([match_id,
                            match_date,
                            match["data-home"],
                            match["data-away"],
                            BeautifulSoup(match["data-venue"]).get_text(),
                            scores[SCORE_HOME],
                            scores[SCORE_AWAY]])

    df = pd.DataFrame(results, columns=RESULTS_COLUMNS)
    df.to_csv(f"match_results_{competition}_{season}_{team}.csv", index=False)
    return f"match_results_{competition}_{season}_{team}.csv"


def main():
    parser = ArgumentParser()
    parser.add_argument("type", choices=["results", "stats", "all"])
    parser.add_argument("--competition", action="store", default="", nargs='+')
    parser.add_argument("--season", action="store", default="", nargs='+')
    parser.add_argument("--team", action="store", default="", nargs='+')
    args = parser.parse_args()
    competition = ' '.join(args.competition)
    season = ' '.join(args.season)
    team = ' '.join(args.team)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("headless")
    with webdriver.Chrome(chrome_options=chrome_options) as driver:
        filename = ""
        if args.type == "results" or args.type == "all":
            filename = scrape_match_results(driver, competition, season, team)
            print(f"Successfully scraped results to {filename}")
        if args.type == "stats" or args.type == "all":
            filename = scrape_all_match_stats(driver, competition, season, team, filename)
            print(f"Successfully scraped stats to {filename}")


if __name__ == "__main__":
    main()
