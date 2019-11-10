from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import pandas as pd

TIMEOUT = 10
SCORE_HOME = 0
SCORE_AWAY = 2
RESULTS_COLUMNS = ["Match ID", "Date", "Home Team", "Away Team", "Stadium", "Home Score", "Away Score"]
MATCH_COLUMNS = ["Match ID", "Referee", "Attendance", "Kick Off", "HalfTime Score", "Home Goals", "Home Red Cards",
                 "Away Goals", "Away Red Cards"]
SCROLL_PAUSE_TIME = 0.5


def parse_events(events):
    """Parse an event to Goal or Red Card"""
    goals = ""
    red_cards = ""
    for index, event in enumerate(events):
        event_list = event.get_text().split()
        if event_list[-1] == "Goal":
            goals += " ".join(event_list[:-1]) + ("" if index == len(events) - 1 else "\n")
        elif event_list[-1] == "Card":
            red_cards += " ".join(event_list[:-2]) + "\n"
    return goals, red_cards


def scrape_match_stats(driver, match_id):
    """Scrape the stats for a specific match"""
    driver.get("https://www.premierleague.com/match/" + match_id)
    webdriver_wait = WebDriverWait(driver, TIMEOUT)
    condition = EC.presence_of_element_located((By.CLASS_NAME, "centralContent"))
    webdriver_wait.until(condition)

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
    return [match_id, referee, attendance, kick_off, half_time_score, home_goals, home_red_cards, away_goals,
            away_red_cards]


def scrape_match_results(driver):
    """Scrape all match results from current Premier League season"""
    results = []
    driver.get('https://www.premierleague.com/results')
    webdriver_wait = WebDriverWait(driver, TIMEOUT)
    condition = EC.presence_of_element_located((By.CLASS_NAME, "fixtures__matches-list"))
    webdriver_wait.until(condition)
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

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
                            BeautifulSoup(match["data-venue"], "lxml").get_text(),
                            scores[SCORE_HOME],
                            scores[SCORE_AWAY]])

    df = pd.DataFrame(results, columns=RESULTS_COLUMNS)
    df.to_csv('match_results.csv', index=False)


def main():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("headless")
    with webdriver.Chrome(chrome_options=chrome_options) as driver:
        # scrape_match_results(driver)
        print(scrape_match_stats(driver, "46701"))


if __name__ == "__main__":
    main()
