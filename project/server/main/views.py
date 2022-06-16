# project/server/main/views.py

from celery.result import AsyncResult
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Gamestats, Fantasyleague, Fantasyteam, Tournament, Player, Team, League, Matchup, Round, Role, Champion
from project.server import db
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
from project.server.tasks import create_task
from project.server.main.lolesports_api import Lolesports_API
from project.server.main.lolscrape import pull_league_teams, pull_league_tournaments, pull_team_players, pull_leagues, pull_league_schedule, pull_game_data
import os
import requests

main_blueprint = Blueprint("main", __name__,)

api = Lolesports_API()


@main_blueprint.route("/login", methods=['GET', 'POST'])
def login():
    if(request.method == 'POST'):
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if(user):
            if(check_password_hash(user.password, password)):
                flash("Login successful", category='success')
                login_user(user, remember=True)
                return(redirect(url_for('main.home')))
            else:
                flash("Login unsuccessful", category='error')
        else:
            flash("User does not exist", category='error')

    return render_template("login.html", user=current_user)


@main_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return(redirect(url_for("main.login")))


@main_blueprint.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if(request.method == 'POST'):
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = User.query.filter_by(email=email).first()
        if(user):
            flash('User with this email already exists', category='error')
        elif(len(email) < 4):
            flash("Email must be more than 3 characters", category='error')
        elif(len(username) < 2):
            flash("Name must be more than 2 characters", category='error')
        elif(password1 != password2):
            flash("Passwords must match", category='error')
        elif(len(password1) < 7):
            flash("Passwords must be at least 7 characters", category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash("Account created", category='success')
            user = User.query.filter_by(email=email).first()
            login_user(user, remember=True)
            return(redirect(url_for('main.home')))
    return render_template("sign-up.html", user=current_user)


@main_blueprint.route("/myleagues", methods=['GET', 'POST'])
@login_required
def myleagues():

    # How do we deal with making a new fantasy league?
    # get esports id of league
    # check all tournaments of that league
    # filter by date - find the soonest tournament that hasn't started yet.
    # if there is a tournament entry with the same esportsId
    # link the fantasy league to that tournament
    # if not, create a new tournament using that esportsid.
    # then

    # When "new fantasy league" info is submitted
    if request.method == "POST":

        # get form data - desired fantasy name and the leagueID of the league we're looking at.
        leagueName = request.form.get("leagueName")
        league = request.form.get("league")

        # we should probably just get the most recent season tbh
        now = str(datetime.today().date())

        # check to see what tournaments are available
        allTournaments = api.get_tournaments_for_league(league_id=league)

        # print to console
        print(allTournaments)

        upcomingTournaments = [
            d for d in allTournaments['leagues'][0]['tournaments'] if d['startDate'] >= now]

        if(len(upcomingTournaments) > 1):
            earliest = {}
            earliest['date'] = upcomingTournaments[0]['startDate']
            earliest['key'] = 0

            for i in range(len(upcomingTournaments) - 1):
                if(upcomingTournaments[i+1]['startDate'] < earliest['date']):
                    earliest['date'] = upcomingTournaments[i+1]
                    earliest['key'] = i+1

            nextTournament = upcomingTournaments[earliest['key']]

        elif(len(upcomingTournaments) == 1):

            nextTournament = upcomingTournaments[0]

        else:

            nextTournament = []

        # check to see that there is, in fact, a tournament soon.
        if(nextTournament == []):

            flash("No upcoming tournaments for that League", category='error')

        else:
            exists = Tournament.query.filter_by(
                esportsId=nextTournament['id']).first()
            if not exists:

                currentLeague = League.query.filter_by(
                    esportsId=league).first()

                startDate = datetime.date(datetime.strptime(
                    nextTournament['startDate'], '%Y-%m-%d'))
                endDate = datetime.date(datetime.strptime(
                    nextTournament['endDate'], '%Y-%m-%d'))

                new_tournament = Tournament(
                    esportsRegionId=league, esportsId=nextTournament['id'], name=nextTournament['slug'], startDate=startDate, endDate=endDate, league=currentLeague.id)

                db.session.add(new_tournament)
                db.session.commit()

                exists = Tournament.query.filter_by(
                    esportsId=nextTournament['id']).first()

                teams = pull_league_teams(nextTournament['id'])

                for team in teams:

                    new_team = Team(esportsId=team['esportsId'], name=team['name'],
                                    code=team['code'], slug=team['slug'], tournament=exists.id)
                    print(team)
                    db.session.add(new_team)
                    db.session.commit()

                    players = pull_team_players(team['slug'])

                    thisteam = Team.query.filter_by(
                        esportsId=team['esportsId']).first()

                    roles = ['top', 'jungle', 'mid', 'bottom', 'support']

                    for role in roles:
                        new_role = Role(team=thisteam.id, role=role)
                        db.session.add(new_role)
                        db.session.commit()
                        j = True
                        for player in players:
                            if player['role'] == role:
                                new_player = Player(
                                    esportsId=player['esportsId'], name=player['name'], team=thisteam.id, role=new_role.id, default=j)
                                print(new_player)
                                j = False
                                db.session.add(new_player)

                    db.session.commit()

            new_fantasyleague = Fantasyleague(
                owner=current_user.id, tournament=exists.id, leagueName=leagueName)
            db.session.add(new_fantasyleague)
            db.session.commit()

            flash("Fantasy league created for " +
                  nextTournament['slug'], category='success')

        print(now)
    allLeagues = League.query.all()
    allTournaments = Tournament.query.all()
    return render_template(
        "myleagues.html",
        user=current_user,
        name=current_user.username,
        now=str(datetime.today()),
        leagues=allLeagues,
        tournaments=allTournaments)


@main_blueprint.route("/", methods=["GET"])
def home():
    return render_template("main/home.html", user=current_user)


@main_blueprint.route("/tasks", methods=["POST"])
def run_task():
    content = request.json
    task_type = content["type"]
    print(task_type)

    task = create_task.delay(int(task_type))
    return jsonify({"task_id": task.id}), 202


@main_blueprint.route("/tasks/<task_id>", methods=["GET"])
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return jsonify(result), 200


@main_blueprint.route("/matchup2", methods=['GET'])
@login_required
def matchup2():
    leagueid = request.args.get('leagueid')
    matchupid = request.args.get('m')

    fantasy = Fantasyleague.query.filter_by(id=leagueid).first()
    matchup = Matchup.query.filter_by(id=matchupid).first()
    round = Round.query.filter_by(id=matchup.round).first()
    fteam1 = Fantasyteam.query.filter_by(id=matchup.team1).first()
    fteam2 = Fantasyteam.query.filter_by(id=matchup.team2).first()
    tournament = Tournament.query.filter_by(id=fantasy.tournament).first()
    champions = Champion.query.all()
    
    for role in fteam1:
        for game in role.games:
            if game.round == round.number:
                print("lol")
                
        
    # For each player in the matchup
    # If there is a champion entry, do nothing (entry already full)
    # If there is no champion entry, but there is a workerID, check the worker status
        # if worker is finished, pull and store all the data.
    # If there is no champ entry and no worker, create a worker.

    return render_template(
        "matchup.html",
        user=current_user,
        name=current_user.username, team1=fteam1, team2=fteam2, matchup=matchup, fantasy=fantasy, round=round, tournament=tournament, bestof=1, champions=champions)

@main_blueprint.route("/matchup", methods=['GET', 'POST'])
@login_required
def matchup():
    leagueid = request.args.get('leagueid')
    matchupid = request.args.get('m')
    if(request.method == 'POST'):
        print(request.form)
        matchup = Matchup.query.filter_by(id=matchupid).first()
        if request.form.get('pick1top') and (request.form.get('pick1top') != 'none'):
            champ = Champion.query.filter_by(name = request.form.get('pick1top')).first()
            print(champ.name)
            matchup.pick1top.append(champ)
            db.session.commit()
        if request.form.get('ban1top') and (request.form.get('ban1top') != 'none'):
            champ = Champion.query.filter_by(name = request.form.get('ban1top')).first()
            print(champ.name)
            matchup.ban1top.append(champ)
            db.session.commit()
        if request.form.get('pick1jungle') and (request.form.get('pick1jungle') != 'none'):
            champ = Champion.query.filter_by(name = request.form.get('pick1jungle')).first()
            print(champ.name)
            matchup.pick1jungle.append(champ)
            db.session.commit()
        if request.form.get('ban1jungle') and (request.form.get('ban1jungle') != 'none'):
            champ = Champion.query.filter_by(name = request.form.get('ban1jungle')).first()
            print(champ.name)
            matchup.ban1jungle.append(champ)
            db.session.commit()
        if request.form.get('pick1mid') and (request.form.get('pick1mid') != 'none'):
            champ = Champion.query.filter_by(name = request.form.get('pick1mid')).first()
            print(champ.name)
            matchup.pick1mid.append(champ)
            db.session.commit()
        if request.form.get('ban1mid') and (request.form.get('ban1mid') != 'none'):
            champ = Champion.query.filter_by(name = request.form.get('ban1mid')).first()
            print(champ.name)
            matchup.ban1mid.append(champ)
            db.session.commit()
        if request.form.get('pick1bottom') and (request.form.get('pick1bottom') != 'none'):
            champ = Champion.query.filter_by(name = request.form.get('pick1bottom')).first()
            print(champ.name)
            matchup.pick1bottom.append(champ)
            db.session.commit()
        if request.form.get('ban1bottom') and (request.form.get('ban1bottom') != 'none'):
            champ = Champion.query.filter_by(name = request.form.get('ban1bottom')).first()
            print(champ.name)
            matchup.ban1bottom.append(champ)
            db.session.commit()
        if request.form.get('pick1support') and (request.form.get('pick1support') != 'none'):
            champ = Champion.query.filter_by(name = request.form.get('pick1support')).first()
            print(champ.name)
            matchup.pick1support.append(champ)
            db.session.commit()
        if request.form.get('ban1support') and (request.form.get('ban1support') != 'none'):
            champ = Champion.query.filter_by(name = request.form.get('ban1support')).first()
            print(champ.name)
            matchup.ban1support.append(champ)
            db.session.commit()
        if request.form.get('pick2top') and (request.form.get('pick2top') != 'none'):
            champ = Champion.query.filter_by(name = request.form.get('pick2top')).first()
            print(champ.name)
            matchup.pick2top.append(champ)
            db.session.commit()
        if request.form.get('ban2top') and (request.form.get('ban2top') != 'none'):
            champ = Champion.query.filter_by(name = request.form.get('ban2top')).first()
            print(champ.name)
            matchup.ban2top.append(champ)
            db.session.commit()
        if request.form.get('pick2jungle') and (request.form.get('pick2jungle') != 'none'):
            champ = Champion.query.filter_by(name = request.form.get('pick2jungle')).first()
            print(champ.name)
            matchup.pick2jungle.append(champ)
            db.session.commit()
        if request.form.get('ban2jungle') and (request.form.get('ban2jungle') != 'none'):
            champ = Champion.query.filter_by(name = request.form.get('ban2jungle')).first()
            print(champ.name)
            matchup.ban2jungle.append(champ)
            db.session.commit()
        if request.form.get('pick2mid') and (request.form.get('pick2mid') != 'none'):
            champ = Champion.query.filter_by(name = request.form.get('pick2mid')).first()
            print(champ.name)
            matchup.pick2mid.append(champ)
            db.session.commit()
        if request.form.get('ban2mid') and (request.form.get('ban2mid') != 'none'):
            champ = Champion.query.filter_by(name = request.form.get('ban2mid')).first()
            print(champ.name)
            matchup.ban2mid.append(champ)
            db.session.commit()
        if request.form.get('pick2bottom') and (request.form.get('pick2bottom') != 'none'):
            champ = Champion.query.filter_by(name = request.form.get('pick2bottom')).first()
            print(champ.name)
            matchup.pick2bottom.append(champ)
            db.session.commit()
        if request.form.get('ban2bottom') and (request.form.get('ban2bottom') != 'none'):
            champ = Champion.query.filter_by(name = request.form.get('ban2bottom')).first()
            print(champ.name)
            matchup.ban2bottom.append(champ)
            db.session.commit()
        if request.form.get('pick2support') and (request.form.get('pick2support') != 'none'):
            champ = Champion.query.filter_by(name = request.form.get('pick2support')).first()
            print(champ.name)
            matchup.pick2support.append(champ)
            db.session.commit()
        if request.form.get('ban2support') and (request.form.get('ban2support') != 'none'):
            champ = Champion.query.filter_by(name = request.form.get('ban2support')).first()
            print(champ.name)
            matchup.ban2support.append(champ)
            db.session.commit()
                


    

    fantasy = Fantasyleague.query.filter_by(id=leagueid).first()
    matchup = Matchup.query.filter_by(id=matchupid).first()
    round = Round.query.filter_by(id=matchup.round).first()
    team1 = Fantasyteam.query.filter_by(id=matchup.team1).first()
    team2 = Fantasyteam.query.filter_by(id=matchup.team2).first()
    tournament = Tournament.query.filter_by(id=fantasy.tournament).first()
    champions = Champion.query.all()
    now = datetime.datetime.today()
    print(round)
    print(fantasy)
    print(matchup)

    for role in team1.roles:
        for game in role.games:
            if game.round == round.number:
                print(game.date)
                print(game.champion)
                if not game.champion and game.date < datetime.today():
                    gamedata = pull_game_data(game.gameId)
                    for data in gamedata:
                        dteam = Team.query.filter_by(
                            esportsId=data['teamId']).first()
                        print(dteam.name)
                        drole = Role.query.filter_by(
                            team=dteam.id, role=data['role']).first()
                        print(drole.role)
                        dstats = Gamestats.query.filter_by(
                            role=drole.id, gameId=game.gameId).first()
                        print(game)
                        print(dstats)
                        print(dstats.date)
                        champexists = Champion.query.filter_by(
                            name=data['pick']).first()
                        print(champexists)
                        print(data['pick'])
                        if not champexists:
                            new_champ = Champion(name=data['pick'])

                            db.session.add(new_champ)
                            db.session.commit()

                        champion = Champion.query.filter_by(
                            name=data['pick']).first()
                        dstats.champion = champion.id
                        dstats.playerId = data['id']
                        dstats.teamId = data['teamId']
                        dstats.kills = data['kills']
                        dstats.deaths = data['deaths']
                        dstats.assists = data['assists']
                        dstats.cs = data['cs']
                        dstats.wardsKilled = data['wardsKilled']
                        dstats.wardsPlaced = data['wardsPlaced']
                        dstats.cs15 = data['cs15']
                        dstats.firstBlood = data['firstBlood']
                        dstats.firstBaron = data['firstBaron']
                        dstats.firstDragon = data['firstDragon']
                        dstats.firstTower = data['firstTower']
                        dstats.barons = data['barons']
                        dstats.towers = data['towers']
                        dstats.soloKills = data['solo']
                        dstats.elders = data['elder']
                        dstats.dragons = ''
                        for dragon in data['dragons']:
                            dstats.dragons = dstats.dragons + dragon[0]
                        db.session.commit()
                        print(dstats)
    print("team 2")
    for role in team2.roles:
        for game in role.games:
            if game.round == round.number:
                print(game)
                print(game.champion)
                if not game.champion and game.date < datetime.today():
                    gamedata = pull_game_data(game.gameId)
                    for data in gamedata:
                        dteam = Team.query.filter_by(
                            esportsId=data['teamId']).first()
                        print(dteam.name)
                        drole = Role.query.filter_by(
                            team=dteam.id, role=data['role']).first()
                        print(drole.role)
                        dstats = Gamestats.query.filter_by(
                            role=drole.id, gameId=game.gameId).first()
                        print(game)
                        print(dstats)
                        print(dstats.date)
                        champexists = Champion.query.filter_by(
                            name=data['pick']).first()
                        print(champexists)
                        print(data['pick'])
                        if not champexists:
                            new_champ = Champion(name=data['pick'])

                            db.session.add(new_champ)
                            db.session.commit()

                        champion = Champion.query.filter_by(
                            name=data['pick']).first()
                        dstats.champion = champion.id
                        dstats.playerId = data['id']
                        dstats.teamId = data['teamId']
                        dstats.kills = data['kills']
                        dstats.deaths = data['deaths']
                        dstats.assists = data['assists']
                        dstats.cs = data['cs']
                        dstats.wardsKilled = data['wardsKilled']
                        dstats.wardsPlaced = data['wardsPlaced']
                        dstats.cs15 = data['cs15']
                        dstats.firstBlood = data['firstBlood']
                        dstats.firstBaron = data['firstBaron']
                        dstats.firstDragon = data['firstDragon']
                        dstats.firstTower = data['firstTower']
                        dstats.barons = data['barons']
                        dstats.towers = data['towers']
                        dstats.soloKills = data['solo']
                        dstats.elders = data['elder']
                        dstats.dragons = ''
                        for dragon in data['dragons']:
                            dstats.dragons = dstats.dragons + dragon[0]
                        db.session.commit()
                        print(dstats)

    # For each player in the matchup
    # If there is a champion entry, do nothing (entry already full)
    # If there is no champion entry, but there is a workerID, check the worker status
        # if worker is finished, pull and store all the data.
    # If there is no champ entry and no worker, create a worker.

    return render_template(
        "matchup.html",
        user=current_user,
        name=current_user.username, team1=team1, team2=team2, matchup=matchup, fantasy=fantasy, round=round, tournament=tournament, bestof=1, champions=champions, now = now)


@main_blueprint.route("/manage", methods=['GET', 'POST'])
@login_required
def manage():

    leagueid = request.args.get('leagueid')
    fantasy = Fantasyleague.query.filter_by(id=leagueid).first()
    tournament = Tournament.query.filter_by(id=fantasy.tournament).first()
    league = League.query.filter_by(id=tournament.league).first()
    print('Pre-post')

    if(request.method == 'POST'):
        action = request.form.get('action')
        print(action[0:8])
        if action == 'Invite':
            invited = User.query.filter_by(
                email=request.form.get('player_invite')).first()
            if invited:
                if not (invited in fantasy.users):
                    fantasy.users.append(invited)
                    new_fantasy_team = Fantasyteam(
                        league=fantasy.id, owner=invited.id, name=invited.username + "'s team")
                    db.session.add(new_fantasy_team)
                    db.session.commit()
                    flash("User Added", category='success')
                else:
                    flash("User already in league", category='success')
            else:
                flash("User doesn't exist", category='error')

        elif action[0:4] == "team":
            print("lmao")
            print(request.form)
            picks = request.form
            current_team = Fantasyteam.query.filter_by(
                id=action[4:]).first()
            roles = []
            print(current_team.name)
            print(current_team.roles)
            for role in current_team.roles:
                roles.append(role.role)
            for pick in picks:
                if pick != "action":
                    if not pick in roles:
                        current_role = Role.query.filter_by(
                            id=request.form.get(pick)).first()
                        current_team.roles.append(current_role)
                        fantasy.roles.append(current_role)
                        db.session.commit()
            print(current_team.roles)
        elif action == "draft":
            print('lol')

        elif action == "generate":
            # we make a big dict? list? idk.
            if not fantasy.rounds:
                schedule = pull_league_schedule(tournamentId=league.esportsId, startDate=str(
                    tournament.startDate), endDate=str(tournament.endDate))
                print(schedule)

            blocks = []
            for i in schedule:
                if not i['blockName'] in blocks:
                    blocks.append(i['blockName'])
                    print(blocks)

                    new_round = Round(name=i['blockName'],
                                      number=len(blocks), league=fantasy.id)
                    db.session.add(new_round)
                    db.session.commit()

                for teamCode in i['match']['teams']:
                    team = Team.query.filter_by(
                        code=teamCode['code'], tournament=tournament.id).first()
                    for j in range(int(i['match']['strategy']['count'])):
                        for role in team.roles:
                            game_exists = Gamestats.query.filter_by(role=role.id, teamId=team.esportsId, matchId=int(i['match']['id']), gameId=int(i['match']['id']) + 1 + j, date=datetime.strptime(
                                i['startTime'], "%Y-%m-%dT%H:%M:%SZ"), matchType=i['match']['strategy']['count'], round=len(blocks)).first()
                            if not game_exists:
                                new_gamestats = Gamestats(role=role.id, teamId=team.esportsId, matchId=int(i['match']['id']), gameId=int(i['match']['id']) + 1 + j, date=datetime.strptime(
                                    i['startTime'], "%Y-%m-%dT%H:%M:%SZ"), matchType=i['match']['strategy']['count'], round=len(blocks))
                                db.session.add(new_gamestats)
                                role.games.append(new_gamestats)
                                db.session.commit()
                                print(role.games)

            # generate matchup objects
            # team pairs for each round
            teams = fantasy.teams
            for round in fantasy.rounds:
                for i in range(int(len(teams)/2)):
                    new_matchup = Matchup(
                        round=round.id, team1=teams[i].id, team2=teams[-(i+1)].id)
                    db.session.add(new_matchup)
                    db.session.commit()
                teams = teams[0:1] + teams[2:] + teams[1:2]

            # games = Gamestats.query.all()
            # for game in games:
            #     print(game.champion)
            #     game.champion = None
            #     print(game.champion)
            # db.session.commit()
            # print(fantasy.rounds)
            # print(fantasy.rounds[0].weekstats)
            # print(fantasy.rounds[0].weekstats[0].team1)
            # print(fantasy.rounds[0].weekstats[0].team2)
            # print(fantasy.rounds[1].weekstats[0].team1)
            # print(
            #     fantasy.teams[fantasy.rounds[1].weekstats[0].team2].roles[0].games)
    # need a "generate matchups" button?
    # and also a way to view them (replacing player table maybe)
        elif action == "Settings":
            fantasy.kill = request.form.get("kill_points")
            fantasy.death = request.form.get("death_points")
            fantasy.assist = request.form.get("assist_points")
            fantasy.wardPlace = request.form.get("wardPlace_points")
            fantasy.wardKill = request.form.get("wardKill_points")
            fantasy.cs = request.form.get("cs_points")

            fantasy.firstBaron = request.form.get("firstBaron_points")
            fantasy.firstDragon = request.form.get("firstDragon_points")
            fantasy.firstTower = request.form.get("firstTower_points")
            fantasy.firstBlood = request.form.get("firstBlood_points")
            fantasy.soloKill = request.form.get("soloKill_points")
            fantasy.morecs15 = request.form.get("morecs15_points")

            fantasy.baron = request.form.get("baron_points")
            fantasy.dragon = request.form.get("dragon_points")
            fantasy.tower = request.form.get("tower_points")
            fantasy.soul = request.form.get("soul_points")
            fantasy.elder = request.form.get("elder_points")
            fantasy.win = request.form.get("win_points")

    return render_template(
        "manage.html",
        user=current_user,
        name=current_user.username, fantasy=fantasy, league=league, tournament=tournament
    )


@main_blueprint.route("/admin", methods=['GET', 'POST'])
def admin():
    if(request.method == 'POST'):
        print('lol')
        action = request.form.get('action')

        if(action == 'team'):
            name = request.form.get('teamname')
            esportsId = request.form.get('teamid')
            code = request.form.get('teamcode')
            tournament = request.form.get('tournament')
            newTeam = Team(name=name, code=code,
                           esportsId=esportsId, tournament=tournament)
            db.session.add(newTeam)
            db.session.commit()
        elif(action == 'player'):
            name = request.form.get('playername')
            team = request.form.get('playerteam')
            role = request.form.get('playerrole')
            newPlayer = Player(name=name, team=team, role=role)
            db.session.add(newPlayer)
            db.session.commit()

        elif(action == 'leagues'):
            leagues = pull_leagues()

            for league in leagues:

                new_league = League(
                    esportsId=league['esportsId'], slug=league['slug'], name=league['name'], region=league['region'])

                db.session.add(new_league)
                db.session.commit()

                tournaments = pull_league_tournaments(league['esportsId'])

        elif(action == 'defaultPlayers'):
            defaultPlayers = request.form
            print(defaultPlayers)
            for teamrole in defaultPlayers:
                print(teamrole)
                if teamrole != 'action':
                    player = request.form.get(teamrole)
                    [team, role] = teamrole.rsplit(' ', 1)
                    team = Team.query.filter_by(code=team).first()
                    role = Role.query.filter_by(
                        team=team.id, role=role).first()

                    currentDefault = Player.query.filter_by(
                        role=role.id, default=True).first()
                    print(currentDefault)
                    print(teamrole)
                    print(role)
                    if currentDefault:
                        if(player != currentDefault.id):
                            currentDefault.default = False
                            Player.query.filter_by(
                                id=player).first().default = True
                            db.session.commit()
                    else:
                        Player.query.filter_by(
                            id=player).first().default = True
                        db.session.commit()
        elif(action == "champs"):
            textfile = open('project/server/champs.txt', 'r')
            for i in textfile.readlines():
                print(i)
                i = i[0:-1]
                champexists = Champion.query.filter_by(name=i).first()

                if not os.path.exists('project/client/static/img/league/champs/' + i + '.png'):
                    champ_img = requests.get('https://ddragon.leagueoflegends.com/cdn/12.11.1/img/champion/'+ i + '.png')
                    imgfile = open('project/client/static/img/league/champs/' + i + '.png', 'wb')
                    imgfile.write(champ_img.content)
                    imgfile.close()
                    print("pulled img")
                if not champexists:
                    new_champ = Champion(name=i)
                    db.session.add(new_champ)
                    db.session.commit()
                    print("made champ db entry")
            textfile.close()

    if (current_user.id == 1):
        allLeagues = League.query.all()
        allTournaments = Tournament.query.all()
        return render_template("admin.html", user=current_user, leagues=allLeagues, tournaments=allTournaments)
    else:
        return render_template("home.html", user=current_user, name=current_user.username)
