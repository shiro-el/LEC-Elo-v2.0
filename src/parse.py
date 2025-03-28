from fetch import fetchStandings, fetchSchedule
import csv

def parseStandingsData(data):
    regular = data["data"]["standings"][0]["stages"][0]["sections"][0]
    
    CompletedRegularMatch = []
    UnstartedRegularMatch = []
    
    for match in regular["matches"]:
        if match["state"] == "completed":
            CompletedRegularMatch.append(match)
        elif match["state"] == "unstarted":
            UnstartedRegularMatch.append(match)
    
    ParsedCompletedRegularMatch = []
    ParsedUnstartedRegularMatch = []
    
    for match in UnstartedRegularMatch:
        ParsedUnstartedRegularMatch.append({
            "id": match["id"],
            "team1": match["teams"][0]["code"],
            "team2": match["teams"][1]["code"],
        })
    
    for match in CompletedRegularMatch:
        ParsedCompletedRegularMatch.append({
            "id": match["id"],
            "team1": match["teams"][0]["code"],
            "team2": match["teams"][1]["code"],
            "team1Score": match["teams"][0]["result"]["gameWins"],
            "team2Score": match["teams"][1]["result"]["gameWins"],
        })
    
    return ParsedCompletedRegularMatch, ParsedUnstartedRegularMatch    

def parseScheduleData(data):
    schedule = data["data"]["schedule"]["events"]

    UnstartedRegularMatch = []
    
    for match in schedule:
        if match["state"] == "unstarted":
            UnstartedRegularMatch.append(match)
    
    ParsedUnstartedRegularMatch = []
    
    for match in UnstartedRegularMatch:
        ParsedUnstartedRegularMatch.append({
            "team1": match["match"]["teams"][0]["code"],
            "team2": match["match"]["teams"][1]["code"],
        })
    
    return ParsedUnstartedRegularMatch

def __main__():
    data = fetchSchedule()
    
    UnstartedRegularMatch = parseScheduleData(data)

    with open("match.csv", "w", newline="") as matchFile:
        writer = csv.writer(matchFile)
        for match in UnstartedRegularMatch:
            writer.writerow([match["team1"], match["team2"]])
            writer.writerow([])

__main__()
