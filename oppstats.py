# Matthew Smarsch and Frank Longueira
# Machine Learning Final Project
# NBA Statistics Collection

from bs4 import BeautifulSoup
import csv
import urllib
import httplib
from lxml import html
import requests

with open("oppstats.csv", "wb") as opp_file:
	csvout = csv.writer(opp_file)
	categories = ["SEASON", "LG", "TEAM", "W", "L", "FINISH", " ", "G", "MP", "FG", "FGA", "FG%", "3P", 
				  "3PA", "3P%", "2P", "2PA", "2P%", "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"]

  	csvout.writerow(categories)

  	teamCodes = ["ATL", "BOS", "NJN", "CHA", "CHI", "CLE", "DAL", "DEN", "DET", "GSW",
    			 "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOH",
    			 "NYK", "OKC", "ORL", "PHI", "PHO", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"]

	urlStart = "http://www.basketball-reference.com/teams/"
	urlEnd = "/opp_stats_per_game.html"

	for teamCode in teamCodes:
		url = urlStart + teamCode + urlEnd
		page = requests.get(url) #Get the html
		soup = BeautifulSoup(page.content)
		dataTable = soup.find('table', class_="sortable stats_table")
		body = soup.find('tbody')
		rows = body.find_all('tr')
		count = 0;
		print "Getting data for " + teamCode + "..."
		for row in rows:
			if count >= 16:
				break;
			alldata = row.find_all('td')
			stats = []
			for data in alldata:
				stats.append(data.text)
			count = count + 1
			csvout.writerow(stats)
			opp_file.flush()