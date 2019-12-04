from Code.Variables import *


class Player:
    def __init__(self, name="", number=0, position="", clean_sheets=0, nationality="", appearances=0, goals=0,
                 assists=0, team=""):
        self.team = team
        self.name = name
        self.number = number
        self.position = position
        self.nationality = nationality
        self.appearances = appearances
        self.clean_sheets = clean_sheets
        self.goals = goals
        self.assists = assists

    def __repr__(self):
        return "Name: " + str(self.name) + "; Number: " + self.number + "; Position: " + str(
            self.position) + "; Nationality: " + str(self.nationality)


def scrape_url_team(driver):
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
    team = url_to_team(url)
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
            number, name, position = info[0].replace('-', '0'), ' '.join(info[1:-1]), info[-1]
        else:
            number, name, position = info[0], info[1], info[2]
        p = Player(number=number, name=name, position=position, team=team)
        players.append(p)

    player_stats = soup.find_all(class_='squadPlayerStats')

    for i in range(len(player_stats)):
        info = player_stats[i].get_text().split()
        j = 1
        nationality = ''
        while info[j] != 'Appearances':
            nationality += info[j] + ' '
            j += 1
        j += 1
        appearances = info[j]
        j += 1
        if len(info[j:]) == 3:
            clean_sheets = info[-1]
            players[i].clean_sheets = clean_sheets
        elif len(info[j:]) == 5:
            clean_sheets = info[j + 2]
            goals = info[-1]
            players[i].goals = goals
            players[i].clean_sheets = clean_sheets
        elif len(info[j:]) == 4:
            goals = info[j + 1]
            assists = info[-1]
            players[i].goals = goals
            players[i].assists = assists
        players[i].nationality = nationality
        players[i].appearances = appearances
    return players


def get_team_id(conn, cur, team, season):
    cur.execute('''SELECT id FROM teams_general WHERE club = %s AND season = %s''',
                (team, season))
    result = cur.fetchall()
    if not result:
        cur.execute('''INSERT INTO teams_general 
        (club, season, stadium, matches_played, wins, losses, goals, goals_conceded, clean_sheets) 
        VALUES (%s, %s, NULL, NULL, NULL, NULL, NULL, NULL, NULL)''',
                    (team, season))
        conn.commit()
        cur.execute('''SELECT id FROM teams_general WHERE club = %s AND season = %s''',
                    (team, season))
        result = cur.fetchall()
    return result[0][0]


def write_to_csv(players, team, season="2019-20"):
    result = []
    filename = PLAYER_DIRECTORY + '/' + team + '_players.csv'
    conn = mysql.connector.connect(user=DB_USER, password=DB_PWD, host='localhost', database=DB_NAME)
    cur = conn.cursor()
    for player in players:
        values = list(player.__dict__.values())
        club_id = get_team_id(conn, cur, team, season)
        row = [season] + [values[0]] + [club_id] + values[1:]
        print(row)
        result.append(values)
        cur.execute(
            '''INSERT INTO players (season, club, club_id, name, number, position, nationality, appearances, 
            clean_sheets, goals, assists) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE 
            season=VALUES(season), club=VALUES(club), club_id=VALUES(club_id), name=VALUES(name), number=VALUES(
            number), position=VALUES(position), nationality=VALUES(nationality), appearances=VALUES(appearances), 
            clean_sheets=VALUES(clean_sheets), goals=VALUES(goals), assists=VALUES(assists) ''', row)

    conn.commit()
    cur.close()
    conn.close()
    df = pd.DataFrame(result, columns=PLAYER_COLUMN_NAMES)
    df.to_csv('../Data/' + filename, index=False)


def url_to_team(url):
    return url.split('/')[-2]


def team_to_url(team, urls):
    team = team.title()
    match = [s for s in urls if team in s]
    try:
        url = match[0]
    except IndexError:
        print("Please provide a valid club name. Choose from the following:")
        for valid_url in urls:
            match = re.search(r'\d/(.*)/squad', valid_url)
            if match:
                print(' '.join(match.group(1).split("-")))
        return
    return url


class PlayersScraper:
    def __init__(self, team):
        if not os.path.exists('../Data/' + PLAYER_DIRECTORY):
            os.mkdir('../Data/' + PLAYER_DIRECTORY)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("headless")
        with webdriver.Chrome(chrome_options=chrome_options) as driver:
            urls = scrape_url_team(driver)
            urls = convert_urls_to_stats(urls)
            if not team:
                for url in urls:
                    team = url_to_team(url)
                    print(f"Scraping {team}'s players data...")
                    players = scrape_team_squad(driver, url)
                    write_to_csv(players, team)
                return
            else:
                print(f"Scraping {team}'s players data...")
                url = team_to_url(team, urls)
                if url:
                    players = scrape_team_squad(driver, url)
                    write_to_csv(players, team)
                return
