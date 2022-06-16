from email.mime import image
from unicodedata import name
from project.server import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# tables to link many/many relationships

association_table = db.Table('association', db.Model.metadata, db.Column('user_id', db.ForeignKey(
    'user.id')), db.Column('fantasyleague_id', db.ForeignKey('fantasyleague.id')))

association_table2 = db.Table('association2', db.Model.metadata, db.Column('fantasyteam_id', db.ForeignKey(
    'fantasyteam.id')), db.Column('role_id', db.ForeignKey('role.id')))

association_table3 = db.Table('association3', db.Model.metadata, db.Column('fantasyleague_id', db.ForeignKey(
    'fantasyleague.id')), db.Column('role_id', db.ForeignKey('role.id')))

association_table4 = db.Table('association4', db.Model.metadata, db.Column('fantasyream_id', db.ForeignKey(
    'fantasyteam.id')), db.Column('matchup_id', db.ForeignKey('matchup.id')))

association_table5 = db.Table('association5', db.Model.metadata, db.Column('role_id', db.ForeignKey(
    'role.id')), db.Column('gamestats_id', db.ForeignKey('gamestats.id')))

association_table6 = db.Table('association6', db.Model.metadata, db.Column('matchup_id', db.ForeignKey(
    'matchup.id')), db.Column('champion_id', db.ForeignKey('champion.id')))

association_table7 = db.Table('association7', db.Model.metadata, db.Column('matchup_id', db.ForeignKey(
    'matchup.id')), db.Column('champion_id', db.ForeignKey('champion.id')))

association_table8 = db.Table('association8', db.Model.metadata, db.Column('matchup_id', db.ForeignKey(
    'matchup.id')), db.Column('champion_id', db.ForeignKey('champion.id')))

association_table9 = db.Table('association9', db.Model.metadata, db.Column('matchup_id', db.ForeignKey(
    'matchup.id')), db.Column('champion_id', db.ForeignKey('champion.id')))

association_table10 = db.Table('association10', db.Model.metadata, db.Column('matchup_id', db.ForeignKey(
    'matchup.id')), db.Column('champion_id', db.ForeignKey('champion.id')))

association_table11 = db.Table('association11', db.Model.metadata, db.Column('matchup_id', db.ForeignKey(
    'matchup.id')), db.Column('champion_id', db.ForeignKey('champion.id')))

association_table12 = db.Table('association12', db.Model.metadata, db.Column('matchup_id', db.ForeignKey(
    'matchup.id')), db.Column('champion_id', db.ForeignKey('champion.id')))

association_table13 = db.Table('association13', db.Model.metadata, db.Column('matchup_id', db.ForeignKey(
    'matchup.id')), db.Column('champion_id', db.ForeignKey('champion.id')))

association_table14 = db.Table('association14', db.Model.metadata, db.Column('matchup_id', db.ForeignKey(
    'matchup.id')), db.Column('champion_id', db.ForeignKey('champion.id')))

association_table15 = db.Table('association15', db.Model.metadata, db.Column('matchup_id', db.ForeignKey(
    'matchup.id')), db.Column('champion_id', db.ForeignKey('champion.id')))

association_table16 = db.Table('association16', db.Model.metadata, db.Column('matchup_id', db.ForeignKey(
    'matchup.id')), db.Column('champion_id', db.ForeignKey('champion.id')))

association_table17 = db.Table('association17', db.Model.metadata, db.Column('matchup_id', db.ForeignKey(
    'matchup.id')), db.Column('champion_id', db.ForeignKey('champion.id')))

association_table18 = db.Table('association18', db.Model.metadata, db.Column('matchup_id', db.ForeignKey(
    'matchup.id')), db.Column('champion_id', db.ForeignKey('champion.id')))

association_table19 = db.Table('association19', db.Model.metadata, db.Column('matchup_id', db.ForeignKey(
    'matchup.id')), db.Column('champion_id', db.ForeignKey('champion.id')))

association_table20 = db.Table('association20', db.Model.metadata, db.Column('matchup_id', db.ForeignKey(
    'matchup.id')), db.Column('champion_id', db.ForeignKey('champion.id')))

association_table21 = db.Table('association21', db.Model.metadata, db.Column('matchup_id', db.ForeignKey(
    'matchup.id')), db.Column('champion_id', db.ForeignKey('champion.id')))

association_table22 = db.Table('association22', db.Model.metadata, db.Column('matchup_id', db.ForeignKey(
    'matchup.id')), db.Column('champion_id', db.ForeignKey('champion.id')))

association_table23 = db.Table('association23', db.Model.metadata, db.Column('matchup_id', db.ForeignKey(
    'matchup.id')), db.Column('champion_id', db.ForeignKey('champion.id')))

association_table24 = db.Table('association24', db.Model.metadata, db.Column('matchup_id', db.ForeignKey(
    'matchup.id')), db.Column('champion_id', db.ForeignKey('champion.id')))

association_table25 = db.Table('association25', db.Model.metadata, db.Column('matchup_id', db.ForeignKey(
    'matchup.id')), db.Column('champion_id', db.ForeignKey('champion.id')))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)

    # user's info
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150), unique=True)

    # is user a site admin?
    admin = db.Column(db.Boolean)

    # user can own many leagues
    leaguesOwned = db.relationship("Fantasyleague")

    # user can participate in many leagues
    leagues = db.relationship(
        "Fantasyleague", secondary=association_table, back_populates="users")

    # user can have many teams
    teams = db.relationship("Fantasyteam")


class Fantasyleague(db.Model):
    __tablename__ = 'fantasyleague'
    id = db.Column(db.Integer, primary_key=True)

    # each league belongs to one owner
    owner = db.Column(db.Integer, db.ForeignKey("user.id"))

    # each league belongs to many users
    users = db.relationship(
        "User", secondary=association_table, back_populates="leagues")

    # each league belongs to one tournament, tournaments don't care about leagues
    tournament = db.Column(db.Integer, db.ForeignKey("tournament.id"))

    # name of your fantasy league
    leagueName = db.Column(db.String(100))

    # each league has multiple teams
    teams = db.relationship("Fantasyteam")
    roles = db.relationship("Role", secondary=association_table3)
    rounds = db.relationship("Round")

    # is league currently active?
    active = db.Column(db.Boolean)

    # settings
    pickmul = db.Column(db.Float, default=2.00)
    banmul = db.Column(db.Float, default=0.50)

    # player stats points
    kill = db.Column(db.Float, default=3.00)
    soloKill = db.Column(db.Float, default=2.00)
    death = db.Column(db.Float, default=-1.00)
    assist = db.Column(db.Float, default=2.00)
    cs = db.Column(db.Float, default=0.01)
    morecs15 = db.Column(db.Float, default=2.00)
    firstBlood = db.Column(db.Float, default=1.00)
    wardPlace = db.Column(db.Float, default=0.10)
    wardKill = db.Column(db.Float, default=0.10)

    # team objective points
    firstBaron = db.Column(db.Float, default=2.00)
    baron = db.Column(db.Float, default=1.00)
    firstDragon = db.Column(db.Float, default=1.00)
    dragon = db.Column(db.Float, default=1.00)
    firstTower = db.Column(db.Float, default=2.00)
    tower = db.Column(db.Float, default=0.50)
    soul = db.Column(db.Float, default=3.00)
    elder = db.Column(db.Float, default=4.00)
    win = db.Column(db.Float, default=5.00)


class Fantasyteam(db.Model):
    __tablename__ = 'fantasyteam'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))
    league = db.Column(db.Integer, db.ForeignKey("fantasyleague.id"))
    owner = db.Column(db.Integer, db.ForeignKey("user.id"))
    roles = db.relationship("Role", secondary=association_table2)
    matchups = db.relationship("Matchup", secondary=association_table4)


class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(20))
    number = db.Column(db.Integer)
    weekstats = db.relationship("Matchup")
    league = db.Column(db.Integer, db.ForeignKey("fantasyleague.id"))


class Matchup(db.Model):
    __tablename__ = 'matchup'
    id = db.Column(db.Integer, primary_key=True)

    round = db.Column(db.Integer, db.ForeignKey("round.id"))

    team1 = db.Column(db.Integer, db.ForeignKey("team.id"))
    
    base1 = db.Column(db.Float, default = 0.0)
    total1 = db.Column(db.Float, default = 0.0)
    base1top = db.Column(db.Float, default = 0.0)
    total1top = db.Column(db.Float, default = 0.0)
    base1mid = db.Column(db.Float, default = 0.0)
    total1mid = db.Column(db.Float, default = 0.0)
    base1jungle = db.Column(db.Float, default = 0.0)
    total1jungle = db.Column(db.Float, default = 0.0)
    base1bottom = db.Column(db.Float, default = 0.0)
    total1bottom = db.Column(db.Float, default = 0.0)
    base1support = db.Column(db.Float, default = 0.0)
    total1support = db.Column(db.Float, default = 0.0)
    pick1top = db.relationship('Champion', secondary=association_table6)
    ban1top = db.relationship('Champion', secondary=association_table7)
    pick1jungle = db.relationship('Champion', secondary=association_table8)
    ban1jungle = db.relationship('Champion', secondary=association_table9)
    pick1mid = db.relationship('Champion', secondary=association_table10)
    ban1mid = db.relationship('Champion', secondary=association_table11)
    pick1bottom = db.relationship('Champion', secondary=association_table12)
    ban1bottom = db.relationship('Champion', secondary=association_table13)
    pick1support = db.relationship('Champion', secondary=association_table14)
    ban1support = db.relationship('Champion', secondary=association_table15)

    team2 = db.Column(db.Integer, db.ForeignKey("team.id"))
    base2 = db.Column(db.Float, default = 0.0)
    total2 = db.Column(db.Float, default = 0.0)
    base2top = db.Column(db.Float, default = 0.0)
    total2top = db.Column(db.Float, default = 0.0)
    base2mid = db.Column(db.Float, default = 0.0)
    total2mid = db.Column(db.Float, default = 0.0)
    base2jungle = db.Column(db.Float, default = 0.0)
    total2jungle = db.Column(db.Float, default = 0.0)
    base2bottom = db.Column(db.Float, default = 0.0)
    total2bottom = db.Column(db.Float, default = 0.0)
    base2support = db.Column(db.Float, default = 0.0)
    total2support = db.Column(db.Float, default = 0.0)
    pick2top = db.relationship('Champion', secondary=association_table16)
    ban2top = db.relationship('Champion', secondary=association_table17)
    pick2jungle = db.relationship('Champion', secondary=association_table18)
    ban2jungle = db.relationship('Champion', secondary=association_table19)
    pick2mid = db.relationship('Champion', secondary=association_table20)
    ban2mid = db.relationship('Champion', secondary=association_table21)
    pick2bottom = db.relationship('Champion', secondary=association_table22)
    ban2bottom = db.relationship('Champion', secondary=association_table23)
    pick2support = db.relationship('Champion', secondary=association_table24)
    ban2support = db.relationship('Champion', secondary=association_table25)


class League(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    esportsId = db.Column(db.Integer)
    slug = db.Column(db.String(20))
    name = db.Column(db.String(100))
    region = db.Column(db.String(50))

    tournaments = db.relationship("Tournament")


class Tournament(db.Model):
    __tablename__ = 'tournament'
    id = db.Column(db.Integer, primary_key=True)

    league = db.Column(db.Integer, db.ForeignKey("league.id"))

    # riot Esports IDs for region and tournament
    esportsRegionId = db.Column(db.Integer)

    esportsId = db.Column(db.Integer)

    # path to region logo? could just use name to find it.
    image = db.Column(db.String(100))

    # tournament name/title
    name = db.Column(db.String(20))

    #there are technically multiple tournaments in a season - regular season and playoffs.
    #MSI/worlds have more stages still.
    stage = db.Column(db.String(20))

    # how many teams are in this tournament?
    teamnum = db.Column(db.Integer)

    # start/end datetime.date() objects
    startDate = db.Column(db.Date)
    endDate = db.Column(db.Date)

    # track players associated with this tournament
    teams = db.relationship("Team")


class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)

    roles = db.relationship("Role")
    esportsId = db.Column(db.Integer)
    name = db.Column(db.String(20))
    code = db.Column(db.String(20))
    slug = db.Column(db.String(50))
    tournament = db.Column(db.Integer, db.ForeignKey("tournament.id"))


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    team = db.Column(db.Integer, db.ForeignKey("team.id"))
    role = db.Column(db.String(20))
    players = db.relationship("Player")
    games = db.relationship("Gamestats", secondary=association_table5)


class Player(db.Model):
    __tablename__ = 'player'
    id = db.Column(db.Integer, primary_key=True)
    esportsId = db.Column(db.Integer)
    # default player name, overridden by playergame.
    name = db.Column(db.String(20))
    # role info
    team = db.Column(db.Integer, db.ForeignKey("team.id"))
    role = db.Column(db.Integer, db.ForeignKey("role.id"))
    default = db.Column(db.Boolean)


class Champion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


class Gamestats(db.Model):
    __tablename__ = 'gamestats'
    id = db.Column(db.Integer, primary_key=True)

    # each playergame belongs to only one player
    role = db.Column(db.Integer, db.ForeignKey("role.id"))

    # we want to track which player actually played each game
    name = db.Column(db.String(20))

    #we want to track the worker ID that has these game stats.
    worker = db.Column(db.String(50))

    # get riot esportsIds for player, game, match (used to pull from esports API)
    playerId = db.Column(db.Integer)
    teamId = db.Column(db.Integer)
    gameId = db.Column(db.Integer)
    matchId = db.Column(db.Integer)

    # when did the game start?
    date = db.Column(db.DateTime)

    # I think we want to track if it's a Bo3, Bo5, or if player is eliminated.
    matchType = db.Column(db.Integer)

    # track what round (week) we're at
    round = db.Column(db.Integer)

    # game stats
    champion = db.Column(db.Integer, db.ForeignKey("champion.id"))

    # player stats
    kills = db.Column(db.Integer)
    soloKills = db.Column(db.Integer)
    deaths = db.Column(db.Integer)
    assists = db.Column(db.Integer)
    cs = db.Column(db.Integer)
    cs15 = db.Column(db.Integer)
    firstBlood = db.Column(db.Integer)
    wardsPlaced = db.Column(db.Integer)
    wardsKilled = db.Column(db.Integer)

    # team stats
    firstBaron = db.Column(db.Integer)
    barons = db.Column(db.Integer)
    firstDragon = db.Column(db.Integer)
    firstTower = db.Column(db.Integer)
    towers = db.Column(db.Integer)

    # we only want to track non-elder dragons
    # we just use the first letter (F, C, O, M, H, ' '), max of 4 dragons
    # we also know if soul has been taken - if all 4 are non-whitespace, then soul has been taken
    dragons = db.Column(db.String(4))
    elders = db.Column(db.Integer)

    #win = db.Column(db.Boolean)
