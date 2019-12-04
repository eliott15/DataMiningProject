from Code.Variables import *


def scrape_url_team(driver, season):
    """Scrape  all Team's url for specified season"""
    urls = []
    print("Scraping all teams stats for " + (("season " + season) if season else "All Seasons"))
    driver.get('https://www.premierleague.com/clubs')
    webdriver_wait = WebDriverWait(driver, TIMEOUT)
    condition = EC.presence_of_element_located((By.CLASS_NAME, "indexBadge"))
    webdriver_wait.until(condition)
    condition = EC.presence_of_element_located((By.CSS_SELECTOR, "ul[class='dropdownList'] > li"))
    webdriver_wait.until(condition)

    set_filters(driver, season)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    tags = soup.find_all('a', class_='indexItem', href=True)
    for tag in tags:
        url = tag['href']
        urls.append(url)
    return urls


def set_filters(driver, season):
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


def scrape_team_stat(driver, url, season):
    print("from " + url)
    driver.get(url)
    webdriver_wait = WebDriverWait(driver, TIMEOUT)
    try:
        condition = EC.presence_of_element_located((By.CLASS_NAME, "stadium"))
        webdriver_wait.until(condition)
    except TimeoutException:
        pass

    condition = EC.presence_of_element_located((By.CSS_SELECTOR, "ul[class='dropdownList'] > li"))
    webdriver_wait.until(condition)

    set_filters(driver, season)

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


def scrape_all_teams_stat(driver, urls, season):
    dictionary = {}
    for url in urls:
        club_name = url.split('/')[-2]
        print("Scrapping data on " + club_name + "...")
        stats = scrape_team_stat(driver, url, season)
        dictionary[club_name] = stats
    return dictionary


def get_team_id(cur, team, season):
    cur.execute('''SELECT id FROM teams_general WHERE club = %s AND season = %s''',
                (team, season))
    result = cur.fetchall()
    if result:
        return result[0][0]


def stats_to_csv(dictionary, season):
    conn = mysql.connector.connect(user=DB_USER, password=DB_PWD, host='localhost', database=DB_NAME)
    cur = conn.cursor()
    values = list(dictionary.values())[0]
    number_of_columns = len(values)
    column_names = ["Club"] + ["Season"] + [list(dictionary.values())[0][i][0] for i in range(number_of_columns)]
    result = []
    if season:
        season = season.replace('/', '-')
    else:
        season = "All Seasons"
    for index, club_name in enumerate(list(dictionary.keys())):
        res = [club_name] + [season] + [list(dictionary.values())[index][i][1] for i in range(number_of_columns)]
        result.append(res)
        general = res[:COMMON] + res[COMMON:GENERAL]
        attack = res[:COMMON] + res[GENERAL:ATTACK]
        play = res[:COMMON] + res[ATTACK:PLAY]
        defence = res[:COMMON] + res[PLAY:DEFENCE]
        discipline = res[:COMMON] + res[DEFENCE:DISCIPLINE]
        id = get_team_id(cur, club_name, season)
        if not id:
            cur.execute(
                '''INSERT INTO teams_general
                (club, season, stadium, matches_played, wins, losses, goals, goals_conceded, clean_sheets)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''', general)
            id = get_team_id(cur, club_name, season)

            cur.execute(
                '''INSERT INTO teams_attack (id, club, season, goals, goals_per_match, shots, shots_on_target, 
                shooting_accuracy, penalties_scored, big_chances_created, hit_woodwork) VALUES (%s, %s,%s, %s, %s, %s, %s, 
                %s, %s, %s, %s)''', [id] + attack)
            cur.execute(
                '''INSERT INTO teams_play
                (id, club, season, passes, passes_per_match, pass_accuracy, crosses, cross_accuracy)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''', [id] + play[:2] + play[3:])
            cur.execute(
                '''INSERT INTO teams_defence (id, club, season, clean_sheets, goals_conceded, goals_conceded_per_match, 
                saves, tackles, tackle_success, blocked_shots, interceptions, clearances, headed_clearance, 
                duels_won, errors_leading_to_goal, own_goals) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                 %s)''', [id] + defence)
            cur.execute(
                '''INSERT INTO teams_discipline
                (id, club, season, yellow_cards, red_cards, fouls, offsides)
                VALUES (%s,%s,%s,%s,%s,%s,%s)''', [id] + discipline)

        else:
            cur.execute(
                '''UPDATE teams_general SET club = %s, season = %s, stadium = %s, matches_played = %s, wins = %s, 
                losses = %s, goals = %s, goals_conceded = %s, clean_sheets = %s where id = %s ''',
                general + [id])

            cur.execute(
                '''UPDATE teams_attack SET club = %s, season= %s, goals = %s, goals_per_match= %s, shots= %s, 
                shots_on_target= %s, shooting_accuracy= %s, penalties_scored= %s, big_chances_created= %s, 
                hit_woodwork= %s where id = %s ''', attack + [id])
            cur.execute(
                '''UPDATE teams_play SET club = %s, season = %s, passes = %s, passes_per_match = %s, pass_accuracy = 
                %s, crosses = %s, cross_accuracy = %s where id = %s''', play[:2]+play[3:] + [id])
            cur.execute(
                '''UPDATE teams_defence SET club = %s, season = %s, clean_sheets = %s, goals_conceded = %s, 
                goals_conceded_per_match = %s, saves = %s, tackles = %s, tackle_success = %s, blocked_shots = %s, 
                interceptions = %s, clearances = %s, headed_clearance = %s, duels_won = %s, errors_leading_to_goal = 
                %s, own_goals = %s where id = %s''', defence + [id])
            cur.execute(
                '''UPDATE teams_discipline
                SET club = %s, season = %s, yellow_cards = %s, red_cards = %s, fouls = %s, offsides = %s where id = %s
                ''', discipline + [id])

    conn.commit()
    cur.close()
    conn.close()

    df = pd.DataFrame(result, columns=column_names)
    df.to_csv('../Data/' + f"Team_stats_{season}.csv", index=False)


def convert_url_to_stats(url):
    words = url.split('/')
    words[-1] = 'stats'
    if words[1]:
        words[0] = URL
    else:
        words[0] = "https:"
    new_url = '/'.join(words)
    return new_url


def convert_urls_to_stats(urls):
    return list(map(convert_url_to_stats, urls))


class TeamStatsScraper:
    def __init__(self, season):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("headless")
        with webdriver.Chrome(chrome_options=chrome_options) as driver:
            urls = scrape_url_team(driver, season)
            urls = convert_urls_to_stats(urls)
            teams_stat = scrape_all_teams_stat(driver, urls, season)
        stats_to_csv(teams_stat, season)
