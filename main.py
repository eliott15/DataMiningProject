import os


def main():
    print("Scraping all Liverpool players and their statistics:")
    os.system("python SquadScraper.py --team Liverpool")
    print("##########################")
    print("Scrapping all Premier League Statistics for season 2017/2018")
    os.system("python TeamStatsScraper.py --season 2017/18")
    print("##########################")
    print("Scrapping all Premier League results for Leicester City during 2015/2016")
    os.system(" python MatchScraper.py results --competition Premier League --season 2015/16 --team Leicester City")
    print("##########################")
    print("Scraping Premier League table season 2015-2016 at Home, at the 18th match week ")
    os.system(" python TableScraper.py --season 2015/16 --match_week 18 --home_or_away Home")


if __name__ == '__main__':
    main()
