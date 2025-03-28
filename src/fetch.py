from pprint import pprint
import requests

baseUrl = "https://esports-api.lolesports.com/persisted/gw/"
authToken = "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"
headers = {
    "x-api-key": authToken
}

hl = "en-US"
leagueId = "98767991302996019"
tournamentId = "113487400974323999"

def fetchStandings():
    url = baseUrl + "getStandings?hl=" + hl + "&tournamentId=" + tournamentId
    response = requests.get(url, headers=headers)
    data = response.json()
    
    return data

def fetchSchedule():
    url = baseUrl + "getSchedule?hl=" + hl + "&leagueId=" + leagueId
    response = requests.get(url, headers=headers)
    data = response.json()
    
    return data