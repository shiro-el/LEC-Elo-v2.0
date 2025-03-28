import csv
from collections import defaultdict
import random

K = 33
x = 400

def getData():
    elo = {}
    with open("initElo.csv", "r") as initEloFile:
        reader = csv.reader(initEloFile)
        for row in reader:
            if len(row) == 2:
                elo[row[0]] = int(row[1])
    
    CompletedRegularMatch = []
    UnstartedRegularMatch = []
    with open("match.csv", "r") as matchFile:
        reader = csv.reader(matchFile)
        for row in reader:
            if len(row) == 2:
                UnstartedRegularMatch.append({
                    "team1": row[0],
                    "team2": row[1],
                })
            elif len(row) == 4:
                CompletedRegularMatch.append({
                    "team1": row[0],
                    "team2": row[1],
                    "set1": row[2],
                    "set2": row[3],
                })
            elif len(row) == 5:
                CompletedRegularMatch.append({
                    "team1": row[0],
                    "team2": row[1],
                    "set1": row[2],
                    "set2": row[3],
                    "set3": row[4],
                })
    return elo, CompletedRegularMatch, UnstartedRegularMatch

def getScores(CompletedRegularMatch):
    MatchScores = defaultdict(int)
    SetScores = defaultdict(int)
    
    for match in CompletedRegularMatch:
        team1 = match["team1"]
        team2 = match["team2"]
        
        if len(match) == 4:
            team1Win = match["set1"]
            
            SetScores[team1] += match["set1"] + match["set2"]
            SetScores[team2] += 2 - match["set1"] - match["set2"]
            
            if team1Win:
                MatchScores[team1] += 1
            else:
                MatchScores[team2] += 1
        
        if len(match) == 5:
            team1Win = 0
            for i in ("1", "2", "3"):
                team1Win += match["set"+i]
                SetScores[team1] += match["set"+i]
                SetScores[team2] += 1 - match["set"+i]
            
            if team1Win == 2:
                MatchScores[team1] += 1
            else:
                MatchScores[team2] += 1
    
    return MatchScores, SetScores

def updateElo(CompletedRegularMatch, initElo):
    def calc(team1Elo, team2Elo, team1Score, team2Score):
        expectedScore1 = 1 / (1 + 10 ** ((team2Elo - team1Elo) / x))
        expectedScore2 = 1 / (1 + 10 ** ((team1Elo - team2Elo) / x))
        
        if team1Score > team2Score:
            team1Elo = team1Elo + K * (1 - expectedScore1)
            team2Elo = team2Elo + K * (0 - expectedScore2)
        elif team1Score < team2Score:
            team1Elo = team1Elo + K * (0 - expectedScore1)
            team2Elo = team2Elo + K * (1 - expectedScore2)
        
        return team1Elo, team2Elo
    
    elo = initElo.copy()
    
    for match in CompletedRegularMatch:
        team1 = match["team1"]
        team2 = match["team2"]
        
        if len(match) == 4:
            for setN in range(1, 3):
                elo[team1], elo[team2] = calc(elo[team1], elo[team2], int(match["set" + str(setN)]), 1 - int(match["set" + str(setN)]))
        elif len(match) == 5:
            for setN in range(1, 4):
                elo[team1], elo[team2] = calc(elo[team1], elo[team2], int(match["set" + str(setN)]), 1 - int(match["set" + str(setN)]))
        
    return elo

def expectBO3(team1, team2, elo):
    team1Elo = elo[team1]
    team2Elo = elo[team2]
    
    expectedScore1 = 1 / (1 + 10 ** ((team2Elo - team1Elo) / x))
    expectedScore2 = 1 / (1 + 10 ** ((team1Elo - team2Elo) / x))
    
    expected2vs0 = expectedScore1 ** 2
    expected2vs1 = 2 * expectedScore1 ** 2 * expectedScore2
    expected1vs2 = 2 * expectedScore1 * expectedScore2 ** 2
    expected0vs2 = expectedScore2 ** 2
    
    return expected2vs0, expected2vs1, expected1vs2, expected0vs2

def expectBO5(team1, team2, elo):
    team1Elo = elo[team1]
    team2Elo = elo[team2]
    
    expectedScore1 = 1 / (1 + 10 ** ((team2Elo - team1Elo) / x))
    expectedScore2 = 1 / (1 + 10 ** ((team1Elo - team2Elo) / x))
    
    expected3vs0 = expectedScore1 ** 3
    expected3vs1 = 3 * expectedScore1 ** 3 * expectedScore2
    expected3vs2 = 6 * expectedScore1 ** 3 * expectedScore2 ** 2
    expected2vs3 = 6 * expectedScore1 ** 2* expectedScore2 ** 3
    expected1vs3 = 3 * expectedScore1 * expectedScore2 ** 3
    expected0vs3 = expectedScore2 ** 3
    
    return expected3vs0, expected3vs1, expected3vs2, expected2vs3, expected1vs3, expected0vs3

def expectRegularMatchScore(MatchScores, UnstartedRegularMatch, elo):
    expectedMatchScore = MatchScores.copy()
    
    for match in UnstartedRegularMatch:
        team1 = match["team1"]
        team2 = match["team2"]
        
        expected2vs0, expected2vs1, expected1vs2, expected0vs2 = expectBO3(team1, team2, elo)
        
        expectedMatchScore[team1] += expected2vs0 + expected2vs1
        expectedMatchScore[team2] += expected1vs2 + expected0vs2
    
    return expectedMatchScore

def monteCarlo(MatchScores, SetScores, UnstartedRegularMatch, elo):
    n = 100000
    teams = list(elo.keys())
    playoffQualifications = defaultdict(int)
    upperBracketQualifications = defaultdict(int)
    finals = defaultdict(int)
    wins = defaultdict(int)

    def simulBO5(team1, team2, memoBO5, elo):
        if not (team1, team2) in memoBO5:
                memoBO5[(team1, team2)] = expectBO5(team1, team2, elo)
        expected3vs0, expected3vs1, expected3vs2, expected2vs3, expected1vs3, expected0vs3 = memoBO5[(team1, team2)]
        outcome = random.choices(
            ["3-n", "n-3"],
            weights=[expected3vs0 + expected3vs1 + expected3vs2, expected2vs3 + expected1vs3 + expected0vs3],
            k=1
        )[0]
        
        if outcome == "3-n":
            winner, loser = team1, team2
        else: 
            winner, loser = team2, team1
        
        return winner, loser
    
    memoBO3 = {}
    memoBO5 = {}

    for _ in range(n):
        simulatedMatchScores = MatchScores.copy()
        simulatedSetScores = SetScores.copy()
        
        for match in UnstartedRegularMatch:
            team1 = match["team1"]
            team2 = match["team2"]

            if not (team1, team2) in memoBO3:
                memoBO3[(team1, team2)] = expectBO3(team1, team2, elo)
            expected2vs0, expected2vs1, expected1vs2, expected0vs2 = memoBO3[(team1, team2)]
            outcome = random.choices(
                ["2-0", "2-1", "1-2", "0-2"],
                weights=[expected2vs0, expected2vs1, expected1vs2, expected0vs2],
                k=1
            )[0]
            
            if outcome == "2-0":
                simulatedSetScores[team1] += 2
                simulatedMatchScores[team1] += 1
            elif outcome == "2-1":
                simulatedMatchScores[team1] += 1
                simulatedSetScores[team1] += 2
                simulatedSetScores[team2] += 1
            elif outcome == "1-2":
                simulatedMatchScores[team2] += 1
                simulatedSetScores[team2] += 2
                simulatedSetScores[team1] += 1
            elif outcome == "0-2":
                simulatedMatchScores[team2] += 1
                simulatedSetScores[team2] += 2

        sortedTeams = sorted(teams, key=lambda x:(simulatedMatchScores[x], simulatedSetScores[x]), reverse=True)
        top6Teams = sortedTeams[:6]
        top4Teams = sortedTeams[:4]

        for team in top6Teams:
            playoffQualifications[team] += 1
        for team in top4Teams:
            upperBracketQualifications[team] += 1
        
        team1, team3, team4, team2, team6, team5 = top6Teams
        
        winnerM1, loserM1 = simulBO5(team1, team2, memoBO5, elo)
        winnerM2, loserM2 = simulBO5(team3, team4, memoBO5, elo)
        winnerM3, loserM3 = simulBO5(team5, loserM1, memoBO5, elo)
        winnerM4, loserM4 = simulBO5(team6, loserM2, memoBO5, elo)
        winnerM5, loserM5 = simulBO5(winnerM1, winnerM2, memoBO5, elo)
        winnerM6, loserM6 = simulBO5(winnerM3, winnerM4, memoBO5, elo)
        winnerM7, loserM7 = simulBO5(loserM5, winnerM6, memoBO5, elo)
        winner, runnerUp = simulBO5(winnerM5, winnerM7, memoBO5, elo)
        
        finals[winner] += 1
        finals[runnerUp] += 1
        wins[winner] += 1

    expectedPOrate = {team: playoffQualifications[team] / n for team in teams}
    expectedUBrate = {team: upperBracketQualifications[team] / n for team in teams}
    expectedFinalsRate = {team: finals[team] / n for team in teams}
    expectedWinsRate = {team: wins[team] / n for team in teams}
    
    return expectedPOrate, expectedUBrate, expectedFinalsRate, expectedWinsRate

def exportResult(elo, expectedRegularMatchScore, expectedPOrate, expectedUBrate, expectedFinalsRate, expectedWinsRate):
    with open("lec.csv", "w", newline="", encoding = "euc-kr") as resultFile:
        writer = csv.writer(resultFile)
        writer.writerow([" ", "레이팅", "정규 승", "PO 진출", "상위 브라켓 진출", "결승 진출", "우승"])
        teams = list(elo.keys())
        teams.sort(key = lambda x:elo[x])
        for team in teams:
            writer.writerow([team,
                             elo[team],
                             expectedRegularMatchScore[team],
                             expectedPOrate[team],
                             expectedUBrate[team],
                             expectedFinalsRate[team],
                             expectedWinsRate[team]])

def __main__():
    data = input("예상 결과를 원하는 경기 정보를 입력하세요. \n 예시: G2,KC,3/FNC,MKOI,5 \n")
    parsedData = data.split(sep="/")
    matches = []
    for match in parsedData:
        matches.append(match.split(sep=","))
    
    initElo, CompletedRegularMatch, UnstartedRegularMatch = getData()
    
    MatchScores, SetScores= getScores(CompletedRegularMatch)
    
    elo = updateElo(CompletedRegularMatch, initElo)
    
    for match in matches:
        team1, team2, bo = match
        if bo == "3":
            expected2vs0, expected2vs1, expected1vs2, expected0vs2 = expectBO3(team1, team2, elo)
            print(team1, "vs", team2, "BO3:",
                  round(expected2vs0*100, 2), 
                  round(expected2vs1*100, 2), 
                  round(expected1vs2*100, 2), 
                  round(expected0vs2*100, 2))
        if bo == "5":
            expected3vs0, expected3vs1, expected3vs2, expected2vs3, expected1vs3, expected0vs3 = expectBO5(team1, team2, elo)
            print(team1, "vs", team2, "BO5:", 
            round(expected3vs0*100, 2),
            round(expected3vs1*100, 2), 
            round(expected3vs2*100, 2), 
            round(expected2vs3*100, 2), 
            round(expected1vs3*100, 2), 
            round(expected0vs3*100, 2))
        
    
    expectedRegularMatchScore =  expectRegularMatchScore(MatchScores, UnstartedRegularMatch, elo)
    
    expectedPOrate, expectedUBrate, expectedFinalsRate, expectedWinsRate = monteCarlo(MatchScores, SetScores, UnstartedRegularMatch, elo)
    
    exportResult(elo, expectedRegularMatchScore, expectedPOrate, expectedUBrate, expectedFinalsRate, expectedWinsRate)
    
__main__()