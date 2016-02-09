# Matthew Smarsch and Frank Longueira
# Machine Learning Final Project
# NBA Statistics Collection

from bs4 import BeautifulSoup
import csv
import urllib
import httplib
from lxml import html
import requests
import numpy as np
import operator

with open("201415dataAvgs.csv", "wb") as stat_file: #Open CSV file for writing
    csvout = csv.writer(stat_file) #CSV writer stream

    categories = ["TEAM", "GP", "H/A", "MP", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "FT", "FTA", 
                  "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS", "OPP", 
                  "OGP", "H/A", "OMP", "OFG", "OFGA", "OFG%", "O3P", "O3PA", "O3P%", "OFT", "OFTA", 
                  "OFT%", "OORB", "ODRB", "OTRB", "OAST", "OSTL", "OBLK", "OTOV", "OPF", "OPTS", "W%"]
    #Write category row
    csvout.writerow(categories)

    #Team codes used for URL generation
    teamCodes = ["ATL", "BOS", "BRK", "CHO", "CHI", "CLE", "DAL", "DEN", "DET", "GSW",
    			 "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP",
    			 "NYK", "OKC", "ORL", "PHI", "PHO", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"]

    teamNames = ["Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets", "Chicago Bulls", "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets",
                 "Detroit Pistons", "Golden State Warriors", "Houston Rockets", "Indiana Pacers", "Los Angeles Clippers", "Los Angeles Lakers", "Memphis Grizzlies",
                 "Miami Heat", "Milwaukee Bucks", "Minnesota Timberwolves", "New Orleans Pelicans", "New York Knicks", "Oklahoma City Thunder", 
                 "Orlando Magic", "Philadelphia 76ers", "Phoenix Suns", "Portland Trail Blazers", "Sacramento Kings", "San Antonio Spurs", "Toronto Raptors", 
                 "Utah Jazz", "Washington Wizards"] 

    #URL before teamCode
    urlStart = "http://www.basketball-reference.com/teams/"
    #URL after teamCode
    urlEnd = "/2015_games.html"

    #Hyperlink anchor text that we want to get url for
    linkText = "Box Score"

    ptsIndex = categories.index("PTS")
    optsIndex = categories.index("OPTS")

    for index, teamCode in enumerate(teamCodes): #For each team
        gameCount = 0
        url = urlStart + teamCode + urlEnd #Concatenate URL
        page = requests.get(url) #Get the html
        soup = BeautifulSoup(page.content) #Beautiful Soup instance
        urls = [] #List to contain box score url's
        runningStats = []
        runningStats.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        print "Scraping data for: " + teamCode + "..."
        for link in soup.find_all('a', href = True, text = linkText): #For all box score links
            urls.append("http://www.basketball-reference.com" + link['href']) #Add links to urls
        for url in urls:
            stats = [0, gameCount] #Add teamCode to stats row
            page = requests.get(url) #Go to box score page
            soup = BeautifulSoup(page.content)
            totals = soup.find_all('tr', class_="bold_text stat_total") #Find stat tables
            tableHeaders = soup.find_all('div', class_= "table_heading")
            if teamCode in url: #If the team is the Home team
                teamStats = totals[2].find_all('td', align="right") #Get all total values
                del teamStats[-1] #Remove empty value
                stats.append(1) #Home team
                for stat in teamStats: 
                    stats.append(stat.text) #Add each stat to stats row
                nameAndRecord = tableHeaders[0].find('h2').text
                for teamName in teamNames:
                    if teamName in nameAndRecord:
                        stats.append(0)
                        oppName = teamName
                        record = nameAndRecord[len(teamName) + 2 : -1]
                        oppGP = int(record[:record.index('-')]) + int(record[record.index('-') + 1:]) - 1
                        stats.append(oppGP)
                        break
                oppStats = totals[0].find_all('td', align="right") #Get opponents stats
                del oppStats[-1]
                stats.append(0) #Away team
                for stat in oppStats:
                    stats.append(stat.text)
            else: #Team is the Away team
                teamStats = totals[0].find_all('td', align="right")
                del teamStats[-1]
                stats.append(0) #Away team
                for stat in teamStats:
                    stats.append(stat.text)
                nameAndRecord = tableHeaders[2].find('h2').text
                for teamName in teamNames:
                    if teamName in nameAndRecord:
                        stats.append(0)
                        oppName = teamName
                        record = nameAndRecord[len(teamName) + 2 : -1]
                        oppGP = int(record[:record.index('-')]) + int(record[record.index('-') + 1:]) - 1
                        stats.append(oppGP)
                        break
                oppStats = totals[2].find_all('td', align="right")
                del oppStats[-1]
                stats.append(1) #Home Team
                for stat in oppStats:
                    stats.append(stat.text)
            if int(stats[ptsIndex]) > int(stats[optsIndex]):
                stats.append(1)
            else:
                stats.append(0)
            stats[6] = 0
            stats[9] = 0
            stats[12] = 0
            stats[28] = 0
            stats[31] = 0
            stats[34] = 0
            this_stats = map(int, stats)
            np_stats = np.array(this_stats)
            np_running = np.array(runningStats)
            runningStats.append(this_stats)
            this_avg = np.divide(np.sum(runningStats, axis=0), float(gameCount + 1))
            this_avg[6] = this_avg[4]/this_avg[5]
            this_avg[9] = this_avg[7]/this_avg[8]
            this_avg[12] = this_avg[10]/this_avg[11]
            this_avg[28] = this_avg[26]/this_avg[27]
            this_avg[31] = this_avg[29]/this_avg[30]
            this_avg[34] = this_avg[32]/this_avg[33]
            stats = this_avg.tolist()
            stats[0] = teamNames[index]
            stats[1] = gameCount
            stats[22] = oppName
            stats[23] = oppGP
            csvout.writerow(stats) #Write stats row to CSV
            stat_file.flush() #Flush CSV write buffer
            gameCount += 1