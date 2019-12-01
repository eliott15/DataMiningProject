from Code.Variables import *
from Code.TableScraper import TableScraper
from Code.MatchScraper import MatchScraper
from Code.TeamStatsScraper import TeamStatsScraper
from Code.PlayersScraper import PlayersScraper


def main():
    if not os.path.exists('../Data'):
        os.makedirs('../Data')
    scraper_list = []
    for file in os.listdir('.'):
        match = re.search(r'(.*)Scraper.py', file)
        if match:
            scraper_list.append(match.group(1))
    parser = ArgumentParser()
    parser.add_argument('scraper', choices=scraper_list)
    parser.add_argument("--season", action="store", default="", nargs='+')
    args, subargs = parser.parse_known_args()
    season = ' '.join(args.season)
    if args.scraper == 'Table':
        parser = ArgumentParser()
        parser.add_argument("--match_week", action="store", default="", nargs='+')
        parser.add_argument("--home_or_away", action="store", default="", nargs='+')
        sub_args = parser.parse_args(subargs)
        match_week = ' '.join(sub_args.match_week)
        home_or_away = ' '.join(sub_args.home_or_away)
        TableScraper(season, match_week, home_or_away)
    elif args.scraper == 'Match':
        parser = ArgumentParser()
        parser.add_argument("type", choices=["results", "stats", "all"])
        parser.add_argument("--competition", action="store", default="", nargs='+')
        parser.add_argument("--team", action="store", default="", nargs='+')
        sub_args = parser.parse_args(subargs)
        competition = ' '.join(sub_args.competition)
        team = ' '.join(sub_args.team)
        MatchScraper(sub_args.type, competition, season, team)
    elif args.scraper == 'TeamStats':
        TeamStatsScraper(season)
    elif args.scraper == 'Players':
        parser = ArgumentParser()
        parser.add_argument("--team", action="store", default="", nargs="+")
        sub_args = parser.parse_args(subargs)
        team = '-'.join(sub_args.team)
        PlayersScraper(team, season)


if __name__ == '__main__':
    main()
