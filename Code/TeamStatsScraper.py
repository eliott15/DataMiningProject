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
    condition = EC.presence_of_element_located((By.CLASS_NAME, "stadium"))
    webdriver_wait.until(condition)
    condition = EC.presence_of_element_located((By.CLASS_NAME, "dropdownList"))
    webdriver_wait.until(condition)
    time.sleep(0.5)

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


def stats_to_csv(dictionary, season):
    values = list(dictionary.values())[0]
    number_of_columns = len(values)
    column_names = ["Club"] +["Season"] + [list(dictionary.values())[0][i][0] for i in range(number_of_columns)]
    result = []
    if season:
        season = season.replace('/', '-')
    else:
        season = "All Seasons"
    for index, club_name in enumerate(list(dictionary.keys())):
        res = [club_name] + [season] + [list(dictionary.values())[index][i][1] for i in range(number_of_columns)]
        result.append(res)
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
