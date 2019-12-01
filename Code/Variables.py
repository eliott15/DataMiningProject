from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
from argparse import ArgumentParser
import os
import re
import time
import pandas as pd
import csv
import sys

URL = 'https://www.premierleague.com'
TIMEOUT = 10
PAUSE_TIME = 2
TABLE_COLUMN_NUMBER = 10
SCORE_HOME = 0
SCORE_AWAY = 2
RESULTS_COLUMNS = ["Match ID", "Date", "Home Team", "Away Team", "Stadium", "Home Score", "Away Score"]
STATS_COLUMNS = ["Match ID", "Referee", "Attendance", "Kick Off", "HT Score", "Home Goals", "Home RC events",
                 "Away Goals", "Away RC events", "Home Assists", "Away Assists", "King of the Match"]
PLAYER_COLUMN_NAMES = ["Club", "Name", "Number", "Position", "Nationality", "Appearances", "Clean Sheets", "Goals", "Assists"]
PLAYER_DIRECTORY = "Squads_Players"