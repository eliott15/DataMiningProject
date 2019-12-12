#### Welcome to Premier League scraping project!

#### General instructions

1. Unzip Code.zip and put the extracted folder "Code" in a Pycharm project.
2. Mark this Pycharm project folder as Sources Root in Pycharm (not the Code folder itself but its direct parent)

    Run the following command in the terminal:

    `export PYTHONPATH="${PYTHONPATH}:/your/source/root"`

    Where your source root is this folder path, Code's direct parent.

3. Create a database in your local mysql with the same name as the variable DB_NAME in the file Variables.py (for instance: 'premier_league')

4. In Variables.py, Update DB_PWD value to your mysql root password (or an other user's, in that case update the DB_USER too)

5. In a terminal window, go to the code's folder and run the following command:

`mysql -u <db_user> -p <db_name> < premier_league.sql`

Enter your password and it should create all the relevant tables automatically.

#### CLI Description

1. Run only the "main.py" file.
2. First argument is which scraper to use: TeamStats, Players, Match, or Table
3. Each scraper has its own fields:

    a. Match has a mandatory {results | stats | all} and then optional --competition, --season, --team
    
    b. TeamStats has optional --season field
    
    c. TableScraper has option --season, --match_week, --home_or_away
    
    d. PlayersScraper has optional --team
    
4. If you don't pass one or more of the optional argument, it will take the custom relevant filter from the website (for example current season for match results, all teams as team, and so on)

##### CLI run examples (run from Code folder):

`python main.py Match all`

`python main.py TeamStats --season 2019/20`

`python main.py Table --season 2017/18 --match_week 15 --home_or_away Home`

`python main.py Players`

#### Database

1. Please refer to premier_league.pdf to see the DB's diagram.

Note: we did not enter the tables from TableScraper to the DB since it would not have much sense, because each row in a particular scraped table has no meaning by itself but as a ranking with the other rows.

#### External API

We added a Weather scraper using meteostat API to scrape weather conditions for each match. We insert it in a new table in the database called match_weather. The sql file was updated accordingly to create the table.

Run it using following command:

`python main.py Weather`