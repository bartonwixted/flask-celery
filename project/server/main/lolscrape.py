from project.server.main.lolesports_api import Lolesports_API
import time
import datetime
import os
import requests

# functions to pull relevant data from LoLesports and reformat it for the site
# each function takes the api response and turns it into an array of dicts that can be directly
# read into the database as teams, tournaments, players, playergames, etc.
api = Lolesports_API()


def pull_league_teams(tournament_id):
    # pulls a whole tournament worth of info
    # all teams + players in tournament
    # hopefully images as well lol
    standings = api.get_standings(tournament_id=tournament_id)

    print(standings)

    teams = []

    teamlist = standings['standings'][0]['stages'][0]['sections'][0]['rankings']

    for i in teamlist:
        teams.append({})
        teams[-1] = {}
        teams[-1]['esportsId'] = i['teams'][0]['id']
        teams[-1]['name'] = i['teams'][0]['name']
        teams[-1]['code'] = i['teams'][0]['code']
        teams[-1]['slug'] = i['teams'][0]['slug']
        if not os.path.exists('project/client/static/img/league/teams/' + teams[-1]['code'] + '.png'):
            team_logo = requests.get(i['teams'][0]['image'])
            file = open('project/client/static/img/league/teams/' +
                        teams[-1]['code'] + '.png', 'wb')
            file.write(team_logo.content)
            file.close()

    return(teams)


def pull_team_players(team_slug):

    team = api.get_teams(team_slug=team_slug)['teams'][0]

    players = []

    for i in range(len(team['players'])):
        players.append({})
        players[i]['name'] = team['players'][i]['summonerName']
        players[i]['role'] = team['players'][i]['role']
        players[i]['esportsId'] = team['players'][i]['id']
        if not os.path.exists('project/client/static/img/league/players/' + team['code'] + '/' + players[i]['name'] + '.png'):
            if not os.path.exists('project/client/static/img/league/players/' + team['code']):
                os.makedirs(
                    'project/client/static/img/league/players/' + team['code'])
            player_img = requests.get(team['players'][i]['image'])
            file = open('project/client/static/img/league/players/' + team['code'] + '/' +
                        players[i]['name'] + '.png', 'wb')
            file.write(player_img.content)
            file.close()

    return(players)


def pull_leagues():
    all_leagues = api.get_leagues()

    leagues = []

    for league in all_leagues['leagues']:

        leagues.append({})

        leagues[-1]['esportsId'] = league['id']
        leagues[-1]['slug'] = league['slug']
        leagues[-1]['name'] = league['name']
        leagues[-1]['region'] = league['region']

        print(league['name'])

        if not os.path.exists('project/client/static/img/league/leagues/' + league['slug'] + '.png'):
            league_img = requests.get(league['image'])
            file = open('project/client/static/img/league/leagues/' +
                        league['slug'] + '.png', 'wb')
            file.write(league_img.content)
            file.close()

    return(leagues)


def pull_league_tournaments(league_id):
    print('lol')


def pull_league_schedule(tournamentId, startDate, endDate):
    scheduleTemp = api.get_schedule(league_id=tournamentId)
    while(startDate < scheduleTemp['schedule']['events'][0]['startTime']):

        schedule = scheduleTemp['schedule']['events']
        schedule2 = schedule
        scheduleTemp = api.get_schedule(
            league_id=tournamentId, pageToken=scheduleTemp['schedule']['pages']['older'])
        schedule = scheduleTemp['schedule']['events']
        schedule = schedule + schedule2

    schedule = [d for d in schedule if d['startTime']
                > startDate + 'T00:00:00Z']

    # schedule has some errors in it, unfortunately...

    if(schedule[0]['league']['name'] == 'LCS'):
        if(schedule[0]['startTime'] == '2022-02-05T21:30:00Z'):
            schedule[22]['match']['id'] = '107458367241215651'
            schedule[45]['match']['id'] = '107458367241215655'

    return(schedule)


def pull_game_data(game):
    participants = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}]

    gameWindow = api.get_window(game_id=game)
    gameDetails = api.get_details(game_id=game)
    stamp = gameDetails["frames"][0]["rfc460Timestamp"]

    # We assume the game is finished, but we'll check anyway.
    # This section gets all the stats discernible from the final frame of the game.

    if gameWindow["frames"][-1]["gameState"] == "finished":

        # Name, playerid, champ, role, teamid, KDA, CS, soul and elder dragons.

        for i in range(5):
            participants[i]["name"] = gameWindow["gameMetadata"]["blueTeamMetadata"][
                "participantMetadata"
            ][i]["summonerName"]
            participants[i]["id"] = gameWindow["gameMetadata"]["blueTeamMetadata"][
                "participantMetadata"
            ][i]["esportsPlayerId"]
            participants[i]["pick"] = gameWindow["gameMetadata"]["blueTeamMetadata"][
                "participantMetadata"
            ][i]["championId"]
            participants[i]["role"] = gameWindow["gameMetadata"]["blueTeamMetadata"][
                "participantMetadata"
            ][i]["role"]
            participants[i]["teamId"] = gameWindow["gameMetadata"]["blueTeamMetadata"][
                "esportsTeamId"
            ]
            participants[i]["kills"] = gameDetails["frames"][-1]["participants"][i]["kills"]
            participants[i]["deaths"] = gameDetails["frames"][-1]["participants"][i][
                "deaths"
            ]
            participants[i]["assists"] = gameDetails["frames"][-1]["participants"][i][
                "assists"
            ]
            participants[i]["cs"] = gameDetails["frames"][-1]["participants"][i][
                "creepScore"
            ]
            participants[i]["wardsKilled"] = gameDetails["frames"][-1]["participants"][i]["wardsDestroyed"]
            participants[i]["wardsPlaced"] = gameDetails["frames"][-1]["participants"][i]["wardsPlaced"]
            participants[i]["cs15"] = 0
            participants[i]["firstBlood"] = 0
            participants[i]["firstTower"] = 0
            participants[i]["towers"] = gameWindow['frames'][-1]['blueTeam']['towers']
            participants[i]["firstDragon"] = 0
            participants[i]["firstBaron"] = 0
            participants[i]["dragons"] = gameWindow["frames"][-1]["blueTeam"]["dragons"]
            participants[i]["solo"] = 0
            participants[i]["barons"] = gameWindow["frames"][-1]["blueTeam"]["barons"]

            if (3 < len(gameWindow["frames"][-1]["blueTeam"]["dragons"])) and (
                gameWindow["frames"][-1]["blueTeam"]["dragons"][3] != "elder"
            ):
                participants[i]["soul"] = 1
            else:
                participants[i]["soul"] = 0

            participants[i]["elder"] = len(
                [d for d in gameWindow["frames"][-1]
                    ["blueTeam"]["dragons"] if d == "elder"]
            )

        for i in range(5):
            participants[i + 5]["name"] = gameWindow["gameMetadata"]["redTeamMetadata"][
                "participantMetadata"
            ][i]["summonerName"]
            participants[i + 5]["id"] = gameWindow["gameMetadata"]["redTeamMetadata"][
                "participantMetadata"
            ][i]["esportsPlayerId"]
            participants[i + 5]["pick"] = gameWindow["gameMetadata"]["redTeamMetadata"][
                "participantMetadata"
            ][i]["championId"]
            participants[i + 5]["role"] = gameWindow["gameMetadata"]["redTeamMetadata"][
                "participantMetadata"
            ][i]["role"]
            participants[i + 5]["teamId"] = gameWindow["gameMetadata"]["redTeamMetadata"][
                "esportsTeamId"
            ]
            participants[i + 5]["kills"] = gameDetails["frames"][-1]["participants"][i + 5][
                "kills"
            ]
            participants[i + 5]["deaths"] = gameDetails["frames"][-1]["participants"][
                i + 5
            ]["deaths"]
            participants[i + 5]["assists"] = gameDetails["frames"][-1]["participants"][
                i + 5
            ]["assists"]
            participants[i + 5]["cs"] = gameDetails["frames"][-1]["participants"][i + 5][
                "creepScore"
            ]
            participants[i+5]["wardsKilled"] = gameDetails["frames"][-1]["participants"][i+5]["wardsDestroyed"]
            participants[i+5]["wardsPlaced"] = gameDetails["frames"][-1]["participants"][i+5]["wardsPlaced"]
            participants[i + 5]["cs15"] = 0
            participants[i + 5]["firstBlood"] = 0
            participants[i + 5]["firstTower"] = 0
            participants[i + 5]["towers"] = gameWindow['frames'][-1]['redTeam']['towers']
            participants[i + 5]["firstDragon"] = 0
            participants[i + 5]["firstBaron"] = 0
            participants[i + 5]["dragons"] = gameWindow["frames"][-1]["redTeam"]["dragons"]
            participants[i + 5]["solo"] = 0
            participants[i+5]["barons"] = gameWindow["frames"][-1]["redTeam"]["barons"]

            if (3 < len(gameWindow["frames"][-1]["redTeam"]["dragons"])) and (
                gameWindow["frames"][-1]["redTeam"]["dragons"][3] != "elder"
            ):
                participants[i + 5]["soul"] = 1
            else:
                participants[i + 5]["soul"] = 0

            participants[i + 5]["elder"] = len(
                [d for d in gameWindow["frames"][-1]
                    ["blueTeam"]["dragons"] if d == "elder"]
            )

    # If the game isn't finished, then we should be using the "ongoing game" function.
    else:
        quit(0)

    gameStart = "0000-00-00T00:00:00.000Z"

    previousFrame = {}
    previousFrame["blueTeam"] = {}
    previousFrame["redTeam"] = {}
    previousFrame["players"] = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}]
    previousFrame["blueTeam"]["kills"] = gameWindow["frames"][-1]["blueTeam"]["totalKills"]
    previousFrame["redTeam"]["kills"] = gameWindow["frames"][-1]["redTeam"]["totalKills"]

    for j in range(5):
        previousFrame["players"][j]["kills"] = gameWindow["frames"][-1]["blueTeam"][
            "participants"
        ][j]["kills"]
        previousFrame["players"][j]["deaths"] = gameWindow["frames"][-1]["blueTeam"][
            "participants"
        ][j]["deaths"]
        previousFrame["players"][j]["assists"] = gameWindow["frames"][-1]["blueTeam"][
            "participants"
        ][j]["assists"]
    for j in range(5):
        previousFrame["players"][j + 5]["kills"] = gameWindow["frames"][-1]["redTeam"][
            "participants"
        ][j]["kills"]
        previousFrame["players"][j + 5]["deaths"] = gameWindow["frames"][-1]["redTeam"][
            "participants"
        ][j]["deaths"]
        previousFrame["players"][j + 5]["assists"] = gameWindow["frames"][-1]["redTeam"][
            "participants"
        ][j]["assists"]

    firstTrack = {}
    firstTrack["blood"] = 0
    firstTrack["baron"] = 0
    firstTrack["dragon"] = 0
    firstTrack["tower"] = 0

    pausefinder = {}
    pausefinder["old"] = gameDetails["frames"][-1]["rfc460Timestamp"]
    pausefinder["new"] = gameDetails["frames"][-1]["rfc460Timestamp"]
    pausefinder["delays"] = []

    oldStamp = stamp

    while gameStart != stamp:

        for i in range(len(gameDetails["frames"])):
            # print('Match Time: ' + str(gameWindow['frames'][-(i+1)]['rfc460Timestamp']))
            if gameWindow["frames"][-(i + 1)]["gameState"] != "finished":
                # check for delays

                pausefinder["old"] = pausefinder["new"]
                pausefinder["new"] = gameDetails["frames"][-(
                    i + 1)]["rfc460Timestamp"]

                if len(pausefinder["new"]) == 20:
                    pausefinder["new"] = pausefinder["new"][0:19:1] + ".000Z"

                if (
                    datetime.datetime.strptime(
                        pausefinder["old"], "%Y-%m-%dT%H:%M:%S.%fZ")
                    - datetime.datetime.strptime(
                        pausefinder["new"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    )
                ).seconds > 2:
                    pausefinder["delays"].append({})
                    pausefinder["delays"][-1]["start"] = datetime.datetime.strptime(
                        pausefinder["new"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    )
                    pausefinder["delays"][-1]["duration"] = (
                        datetime.datetime.strptime(
                            pausefinder["old"], "%Y-%m-%dT%H:%M:%S.%fZ"
                        )
                        - datetime.datetime.strptime(
                            pausefinder["new"], "%Y-%m-%dT%H:%M:%S.%fZ"
                        )
                    ).seconds

                # check against previous frame for kill changes
                # If a kill change occurs, but only one person got kill credit, that person gets +1 to their solo score

                solo = 1
                if (previousFrame["blueTeam"]["kills"] != gameWindow["frames"][-(i + 1)]["blueTeam"]["totalKills"]):
                    for j in range(5):
                        if (previousFrame["players"][j]["assists"] != gameWindow["frames"][-(i + 1)]["blueTeam"]["participants"][j]["assists"]):
                            solo = 0

                    if solo == 1:
                        for j in range(5):
                            if (previousFrame["players"][j]["kills"] != gameWindow["frames"][-(i + 1)]["blueTeam"]["participants"][j]["kills"]):
                                participants[j]["solo"] = participants[j]["solo"] + 1

                solo = 1
                if (previousFrame["redTeam"]["kills"] != gameWindow["frames"][-(i + 1)]["redTeam"]["totalKills"]):
                    for j in range(5):
                        if (previousFrame["players"][j + 5]["assists"] != gameWindow["frames"][-(i + 1)]["redTeam"]["participants"][j]["assists"]):
                            solo = 0

                    if solo == 1:
                        for j in range(5):
                            if (previousFrame["players"][j + 5]["kills"] != gameWindow["frames"][-(i + 1)]["redTeam"]["participants"][j]["kills"]):
                                participants[j +
                                             5]["solo"] = (participants[j + 5]["solo"] + 1)

                # check to see how many dragons, barons, towers and kills there are
                # if there is only one dragon, baron, tower or kill, then those players get that stat set to 1.

                if (
                    (gameWindow["frames"][-(i + 1)]["blueTeam"]["barons"] == 1)
                    and (gameWindow["frames"][-(i + 1)]["redTeam"]["barons"] == 0)
                    and not (firstTrack["baron"])
                ):
                    for j in range(5):
                        participants[j]["firstBaron"] = 1
                    firstTrack["baron"] = 1

                if (
                    (gameWindow["frames"][-(i + 1)]["redTeam"]["barons"] == 1)
                    and (gameWindow["frames"][-(i + 1)]["blueTeam"]["barons"] == 0)
                    and not (firstTrack["baron"])
                ):
                    for j in range(5):
                        participants[j + 5]["firstBaron"] = 1
                    firstTrack["baron"] = 1

                if (
                    (gameWindow["frames"][-(i + 1)]["blueTeam"]["towers"] == 1)
                    and (gameWindow["frames"][-(i + 1)]["redTeam"]["towers"] == 0)
                    and not (firstTrack["tower"])
                ):
                    for j in range(5):
                        participants[j]["firstTower"] = 1
                    firstTrack["tower"] = 1

                if (
                    (gameWindow["frames"][-(i + 1)]["redTeam"]["towers"] == 1)
                    and (gameWindow["frames"][-(i + 1)]["blueTeam"]["towers"] == 0)
                    and not (firstTrack["tower"])
                ):
                    for j in range(5):
                        participants[j + 5]["firstTower"] = 1
                    firstTrack["tower"] = 1

                if (
                    (len(gameWindow["frames"][-(i + 1)]
                         ["blueTeam"]["dragons"]) == 1)
                    and (len(gameWindow["frames"][-(i + 1)]["redTeam"]["dragons"]) == 0)
                    and not (firstTrack["dragon"])
                ):
                    for j in range(5):
                        participants[j]["firstDragon"] = 1
                    firstTrack["dragon"] = 1

                if (
                    (len(gameWindow["frames"][-(i + 1)]
                         ["redTeam"]["dragons"]) == 1)
                    and (len(gameWindow["frames"][-(i + 1)]["blueTeam"]["dragons"]) == 0)
                    and not (firstTrack["dragon"])
                ):
                    for j in range(5):
                        participants[j + 5]["firstDragon"] = 1
                    firstTrack["dragon"] = 1

                if (
                    (gameWindow["frames"][-(i + 1)]
                     ["blueTeam"]["totalKills"] == 1)
                    and (gameWindow["frames"][-(i + 1)]["redTeam"]["totalKills"] == 0)
                    and not (firstTrack["blood"])
                ):
                    for j in range(5):
                        if (
                            gameWindow["frames"][-(i + 1)]["blueTeam"]["participants"][j][
                                "kills"
                            ]
                            == 1
                        ) or (
                            gameWindow["frames"][-(i + 1)]["blueTeam"]["participants"][j][
                                "assists"
                            ]
                            == 1
                        ):
                            participants[j]["firstBlood"] = 1
                    # print(
                    #     "first blood at" +
                    #     str(gameWindow["frames"][i]["rfc460Timestamp"])
                    # )
                    firstTrack["blood"] = 1

                if (
                    (gameWindow["frames"][-(i + 1)]
                     ["redTeam"]["totalKills"] == 1)
                    and (gameWindow["frames"][-(i + 1)]["blueTeam"]["totalKills"] == 0)
                    and not (firstTrack["blood"])
                ):
                    for j in range(5):
                        if (
                            gameWindow["frames"][-(i + 1)]["redTeam"]["participants"][j][
                                "kills"
                            ]
                            == 1
                        ) or (
                            gameWindow["frames"][-(i + 1)]["redTeam"]["participants"][j][
                                "assists"
                            ]
                            == 1
                        ):
                            participants[j + 5]["firstBlood"] = 1
                    # print(
                    #     "first blood at" +
                    #     str(gameWindow["frames"][i]["rfc460Timestamp"])
                    # )
                    firstTrack["blood"] = 1

            previousFrame["blueTeam"]["kills"] = gameWindow["frames"][-(i + 1)]["blueTeam"][
                "totalKills"
            ]
            previousFrame["redTeam"]["kills"] = gameWindow["frames"][-(i + 1)]["redTeam"][
                "totalKills"
            ]
            for j in range(5):
                previousFrame["players"][j]["kills"] = gameWindow["frames"][-(i + 1)][
                    "blueTeam"
                ]["participants"][j]["kills"]
                previousFrame["players"][j]["deaths"] = gameWindow["frames"][-(i + 1)][
                    "blueTeam"
                ]["participants"][j]["deaths"]
                previousFrame["players"][j]["assists"] = gameWindow["frames"][-(i + 1)][
                    "blueTeam"
                ]["participants"][j]["assists"]
            for j in range(5):
                previousFrame["players"][j + 5]["kills"] = gameWindow["frames"][-(i + 1)][
                    "redTeam"
                ]["participants"][j]["kills"]
                previousFrame["players"][j + 5]["deaths"] = gameWindow["frames"][-(i + 1)][
                    "redTeam"
                ]["participants"][j]["deaths"]
                previousFrame["players"][j + 5]["assists"] = gameWindow["frames"][-(i + 1)][
                    "redTeam"
                ]["participants"][j]["assists"]

        stamp = gameDetails["frames"][0]["rfc460Timestamp"]

        if len(stamp) == 20:
            stamp = stamp[0:19:1] + ".000Z"

        point = datetime.datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        point = point - datetime.timedelta(
            seconds=(point.second % 10) + 10, microseconds=point.microsecond
        )

        stamp = str(point.isoformat()) + "Z"
        # print(stamp)

        try:

            gameWindow = api.get_window(game_id=game, starting_time=stamp)
            gameDetails = api.get_details(game_id=game, starting_time=stamp)

        except:

            # print("too early")

            stamp = gameWindow["frames"][0]["rfc460Timestamp"]
            gameStart = stamp

        # Check stats

    # %% CS15

    point = datetime.datetime.strptime(gameStart, "%Y-%m-%dT%H:%M:%S.%fZ")

    point = point + datetime.timedelta(minutes=15)
    for i in range(len(pausefinder["delays"])):
        if pausefinder["delays"][-(i + 1)]["start"] < point:
            point = point + datetime.timedelta(
                seconds=pausefinder["delays"][-(i + 1)]["duration"]
            )
    point2 = point - datetime.timedelta(
        seconds=(point.second % 10), microseconds=point.microsecond
    )

    stamp = str(point2.isoformat()) + "Z"

    gameWindow = api.get_window(game_id=game, starting_time=stamp)
    gameDetails = api.get_details(game_id=game, starting_time=stamp)

    for i in range(len(gameWindow)):
        stamp = datetime.datetime.strptime(
            gameWindow["frames"][-(i + 1)
                                 ]["rfc460Timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ"
        )

        if stamp > point2:
            # print(i)
            j = i

    # print(stamp)
    # print(point2)

    for i in range(5):
        participants[i]["cs15"] = gameWindow["frames"][-(j + 1)]["blueTeam"][
            "participants"
        ][i]["creepScore"]
        print(participants[i])
    for i in range(5):
        participants[i + 5]["cs15"] = gameWindow["frames"][-(j + 1)]["redTeam"][
            "participants"
        ][i]["creepScore"]
        print(participants[i + 5])
    return(participants)
