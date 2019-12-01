from Code.Variables import *


class Player:
    def __init__(self, name="", number="", position="", clean_sheets="", nationality="", appearances="", goals="",
                 assists="", team=""):
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


def scrape_url_team(driver, season):
    urls = []
    driver.get('https://www.premierleague.com/clubs')
    webdriver_wait = WebDriverWait(driver, TIMEOUT)
    condition = EC.presence_of_element_located((By.CLASS_NAME, "indexBadge"))
    webdriver_wait.until(condition)

    set_filters(driver, season)

    season = get_current_filters(driver)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    tags = soup.find_all('a', class_='indexItem', href=True)
    for tag in tags:
        url = tag['href']
        urls.append(url)
    return urls, season


def set_filters(driver, season):
    webdriver_wait = WebDriverWait(driver, TIMEOUT)
    condition = EC.presence_of_element_located((By.CSS_SELECTOR, "ul[class='dropdownList'] > li"))
    webdriver_wait.until(condition)
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


def get_current_filters(driver):
    """Returns the filters for current page"""
    webdriver_wait = WebDriverWait(driver, TIMEOUT)
    condition = EC.presence_of_element_located((By.CLASS_NAME, "current"))
    webdriver_wait.until(condition)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    current_season = soup.find(class_="current", attrs={"data-dropdown-current": "compSeasons"})
    season = current_season.get_text().strip("\"")
    return season


def convert_url_to_stats(url):
    words = url.split('/')
    words[-1] = 'squad'
    words[0] = URL
    new_url = '/'.join(words)
    return new_url


def convert_urls_to_stats(urls):
    return list(map(convert_url_to_stats, urls))


def scrape_team_squad(driver, url, season):
    team = url_to_team(url)
    driver.get(url)
    try:
        webdriver_wait = WebDriverWait(driver, TIMEOUT)
        condition = EC.presence_of_element_located((By.CLASS_NAME, "playerCardInfo"))
        webdriver_wait.until(condition)
    except TimeoutException:
        print("No players data was found for chosen team and season, exiting...")
        sys.exit(1)

    set_filters(driver, season)

    webdriver_wait = WebDriverWait(driver, TIMEOUT)
    condition = EC.presence_of_element_located((By.CSS_SELECTOR, "ul[class='squadPlayerStats'] > li"))
    webdriver_wait.until(condition)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    player_names = soup.find_all(class_='playerCardInfo')
    players = []
    for i in range(len(player_names)):
        info = player_names[i].get_text().split()
        if len(info) > 3:
            number, name, position = info[0], ' '.join(info[1:-1]), info[-1]
        else:
            number, name, position = info[0], info[1], info[2]
        p = Player(number=number, name=name, position=position, team=team)
        players.append(p)

    player_stats = soup.find_all(class_='squadPlayerStats')

    for i in range(len(player_stats)):
        info = player_stats[i].get_text().split()
        print(player_stats[i].get_text())
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


def write_to_csv(players, team, season):
    result = []
    season = season.replace("/", "-")
    filename = f"PLAYER_DIRECTORY/{team}_{season}_players.csv"
    for player in players:
        result.append(list(player.__dict__.values()))
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
    def __init__(self, team, season):
        if not os.path.exists('../Data/' + PLAYER_DIRECTORY):
            os.mkdir('../Data/' + PLAYER_DIRECTORY)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("headless")
        with webdriver.Chrome(chrome_options=chrome_options) as driver:
            urls, season = scrape_url_team(driver, season)
            urls = convert_urls_to_stats(urls)
            if not team:
                for url in urls:
                    team = url_to_team(url)
                    print(f"Scraping {team}'s players data for season {season}...")
                    players = scrape_team_squad(driver, url, season)
                    write_to_csv(players, team, season)
                return
            else:
                print(f"Scraping {team}'s players data for season {season}...")
                url = team_to_url(team, urls)
                if url:
                    players = scrape_team_squad(driver, url, season)
                    write_to_csv(players, team, season)
                return
