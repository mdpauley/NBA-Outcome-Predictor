# Matthew Smarsch and Frank Longueira
# Machine Learning Final Project
# NBA Statistics Collection

from bs4 import BeautifulSoup
import csv
import urllib
import httplib
from lxml import html
import requests

with open("201415games.csv", "wb") as game_file:
	csvout = csv.writer(game_file) #CSV writer stream

	categories = ["TEAM", "GP", "OPP", "OGP"]
	csvout.writerow(categories)

	teamNames = ["Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets", "Chicago Bulls", "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets",
                 "Detroit Pistons", "Golden State Warriors", "Houston Rockets", "Indiana Pacers", "Los Angeles Clippers", "Los Angeles Lakers", "Memphis Grizzlies",
                 "Miami Heat", "Milwaukee Bucks", "Minnesota Timberwolves", "New Orleans Pelicans", "New York Knicks", "Oklahoma City Thunder", 
                 "Orlando Magic", "Philadelphia 76ers", "Phoenix Suns", "Portland Trail Blazers", "Sacramento Kings", "San Antonio Spurs", "Toronto Raptors", 
                 "Utah Jazz", "Washington Wizards"]

	url = "http://www.basketball-reference.com/leagues/NBA_2015_games.html"
	linkText = "Box Score"

	page = requests.get(url) #Get the html
	soup = BeautifulSoup(page.content)
	urls = [] #List to contain box score url's

	for link in soup.find_all('a', href = True, text = linkText): #For all box score links
		urls.append("http://www.basketball-reference.com" + link['href']) #Add links to urls
	for url in urls:
		print url
		stats = []
		page = requests.get(url) #Go to box score page
		soup = BeautifulSoup(page.content)
		tableHeaders = soup.find_all('div', class_= "table_heading")
		nameAndRecord1 = tableHeaders[0].find('h2').text
		nameAndRecord2 = tableHeaders[2].find('h2').text
		for teamName in teamNames:
			if teamName in nameAndRecord1:
				stats.append(teamName)
				record = nameAndRecord1[len(teamName) + 2 : -1]
				stats.append(int(record[:record.index('-')]) + int(record[record.index('-') + 1:]) - 1)
				break
		for teamName in teamNames:
			if teamName in nameAndRecord2:
				stats.append(teamName)
				record = nameAndRecord2[len(teamName) + 2 : -1]
				stats.append(int(record[:record.index('-')]) + int(record[record.index('-') + 1:]) - 1)
				break
		csvout.writerow(stats)
		game_file.flush()