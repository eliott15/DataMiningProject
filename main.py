import os


def main():
    print("Scraping all Liverpool players and their statistics:")
    os.system("python SquadScraper.py --team Liverpool")
    print("##########################")
    print("Scrapping all Premier League Statistics for season 2017/2018")
    os.system("python3 TeamStatsScraper.py --season 2017/18")
    print("##########################")
    print("Scrapping all Premier League results for Leicester City during 2015/2016")
    os.system(" python MatchScraper.py results --competition Premier League --season 2015/16 --team Leicester City")