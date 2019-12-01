from Code.Variables import *


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
    args, subargs = parser.parse_known_args()
    os.system(f"python {args.scraper}Scraper.py {' '.join(subargs)}")


if __name__ == '__main__':
    main()
