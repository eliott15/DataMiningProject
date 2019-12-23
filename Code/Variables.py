from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
from argparse import ArgumentParser
import mysql.connector
import os
import re
import time
import pandas as pd
import csv
import sys
import requests
import json
from datetime import datetime,timedelta
import dateparser

URL = 'https://www.premierleague.com'
TIMEOUT = 10
PAUSE_TIME = 2
TABLE_COLUMN_NUMBER = 10
SCORE_HOME = 0
SCORE_AWAY = 2
RESULTS_COLUMNS = ["Match ID", "Date", "Home Team", "Away Team", "Stadium", "Home Score", "Away Score"]
STATS_COLUMNS = ["Match ID", "Referee", "Attendance", "Kick Off", "HT Score", "Home Goals", "Home RC events",
                 "Away Goals", "Away RC events", "Home Assists", "Away Assists", "King of the Match"]
PLAYER_COLUMN_NAMES = ["Club", "Name", "Number", "Position", "Nationality", "Appearances", "Clean Sheets", "Goals",
                       "Assists"]
PLAYER_DIRECTORY = "Squads_Players"
DB_USER = 'root'
DB_PWD = 'newpassword'
DB_NAME = 'premier_league'
COMMON, GENERAL, ATTACK, PLAY, DEFENCE, DISCIPLINE = 2, 9, 17, 23, 36, 40
SHORT_TO_LONG = {'Birmingham': 'Birmingham City', 'Blackburn':'Blackburn Rovers', 'Bolton':'Bolton Wanderers',
'Bradford':'Bradford City', 'Brighton':'Brighton and Hove Albion', 'Cardiff': 'Cardiff City', 'Charlton': 'Charlton Athletic',
'Coventry': 'Coventry City', 'Derby': 'Derby County', 'Huddersfield': 'Huddersfield Town', 'Hull': 'Hull City',
'Ipswich': 'Ipswich Town', 'Leeds': 'Leeds United', 'Leicester': 'Leicester City', 'Man City': 'Manchester City',
'Man Utd': 'Manchester United', 'Newcastle': 'Newcastle United', 'Norwich': 'Norwich City', "Nott'm Forest": 'Nottingham Forest',
'Oldham' : 'Oldham Athletic', 'QPR': 'Queens Park Rangers', 'Sheffield': 'Sheffield United', 'Sheffield Utd': 'Sheffield United', 'Sheffield Wed': 'Sheffield Wednesday',
'Stoke': 'Stoke City', 'Swansea': 'Swansea City', 'Swindon': 'Swindon Town', 'Spurs': 'Tottenham Hotspur', 'West Brom':'West Bromwich Albion',
'West Ham': 'West Ham United', 'Wigan': 'Wigan Athletic', 'Wolves': 'Wolverhampton Wanderers'}
API_KEY="NEDgpUtU"