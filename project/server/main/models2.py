from email.mime import image
from unicodedata import name
from project.server import db
from flask_login import UserMixin
from sqlalchemy.sql import func

association_table = db.Table('association', db.Model.metadata, db.Column('user_id', db.ForeignKey(
    'user.id')), db.Column('fantasyleague_id', db.ForeignKey('fantasyleague.id')))

association_table4 = db.Table('association4', db.Model.metadata, db.Column('fantasyream_id', db.ForeignKey(
    'fantasyteam.id')), db.Column('matchup_id', db.ForeignKey('matchup.id')))

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

    # each league belongs to one stage, stages don't care about leagues
    stage = db.Column(db.Integer, db.ForeignKey("stage.id"))

    # name of your fantasy league
    leagueName = db.Column(db.String(100))

    # each league has multiple teams
    teams = db.relationship("Fantasyteam")
    roles = db.relationship("Role")
    rounds = db.relationship("Round")

    # is league currently active?
    active = db.Column(db.Boolean)

    # settings
    pickmul = db.Column(db.Float, default=2.0)
    banmul = db.Column(db.Float, default=0.5)


    # player stats points
    kill = db.Column(db.Float, default=3.0)
    soloKill = db.Column(db.Float, default=2.0)
    death = db.Column(db.Float, default=-1.0)
    assist = db.Column(db.Float, default=2.0)
    cs = db.Column(db.Float, default=0.01)
    morecs15 = db.Column(db.Float, default=2.0)
    firstBlood = db.Column(db.Float, default=1.0)
    wardPlace = db.Column(db.Float, default=0.1)
    wardKill = db.Column(db.Float, default=0.1)

    # team objective points
    firstBaron = db.Column(db.Float, default=2.0)
    baron = db.Column(db.Float, default=1.0)
    firstDragon = db.Column(db.Float, default=1.0)
    dragon = db.Column(db.Float, default=1.0)
    firstTower = db.Column(db.Float, default=2.0)
    tower = db.Column(db.Float, default=0.5)
    soul = db.Column(db.Float, default=3.0)
    elder = db.Column(db.Float, default=4.0)
    win = db.Column(db.Float, default=5.0)

class Fantasyteam(db.Model):
    __tablename__ = 'fantasyteam'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))
    league = db.Column(db.Integer, db.ForeignKey("fantasyleague.id"))
    owner = db.Column(db.Integer, db.ForeignKey("user.id"))
    roles = db.relationship("Role")
    matchups = db.relationship("Matchup", secondary=association_table4)

class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(20))
    number = db.Column(db.Integer)
    matchups = db.relationship("Matchup")
    league = db.Column(db.Integer, db.ForeignKey("fantasyleague.id"))

class Matchup(db.Model):
    __tablename__ = 'matchup'
    id = db.Column(db.Integer, primary_key=True)

    round = db.Column(db.Integer, db.ForeignKey("round.id"))

    team1 = db.Column(db.Integer, db.ForeignKey("team.id"))
    base1 = db.Column(db.Float)
    score1 = db.Column(db.Float)
    pick1top = db.relationship('Champion')
    ban1top = db.relationship('Champion')
    pick1jungle = db.relationship('Champion')
    ban1jungle = db.relationship('Champion')
    pick1mid = db.relationship('Champion')
    ban1mid = db.relationship('Champion')
    pick1bottom = db.relationship('Champion')
    ban1bottom = db.relationship('Champion')
    pick1support = db.relationship('Champion')
    ban1support = db.relationship('Champion')

    team2 = db.Column(db.Integer, db.ForeignKey("team.id"))
    base2 = db.Column(db.Float)
    score2 = db.Column(db.Float)
    pick2top = db.relationship('Champion')
    ban2top = db.relationship('Champion')
    pick2jungle = db.relationship('Champion')
    ban2jungle = db.relationship('Champion')
    pick2mid = db.relationship('Champion')
    ban2mid = db.relationship('Champion')
    pick2bottom = db.relationship('Champion')
    ban2bottom = db.relationship('Champion')
    pick2support = db.relationship('Champion')
    ban2support = db.relationship('Champion')

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