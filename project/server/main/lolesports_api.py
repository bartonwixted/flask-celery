import json
import datetime
import requests


def get_latest_date():
    now = datetime.datetime.now(datetime.timezone.utc)
    now = now - datetime.timedelta(
        minutes=1,
        seconds=now.second,
        microseconds=now.microsecond
    )
    now_string = now.isoformat()
    return str(now_string).replace('+00:00', 'Z')


class Lolesports_API:
    API_KEY = {'x-api-key': '0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z'}
    API_URL = 'https://esports-api.lolesports.com/persisted/gw'
    LIVESTATS_API = 'https://feed.lolesports.com/livestats/v1'

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.API_KEY)

    def get_leagues(self, hl='en-US'):
        response = self.session.get(
            self.API_URL + '/getLeagues',
            params={'hl': hl}
        )

        return json.loads(response.text)['data']

    def get_tournaments_for_league(self, hl='en-US', league_id=None):
        response = self.session.get(
            self.API_URL + '/getTournamentsForLeague',
            params={
                'hl': hl,
                'leagueId': league_id
            }
        )

        return json.loads(response.text)['data']

    def get_standings(self, hl='en-US', tournament_id=None):
        response = self.session.get(
            self.API_URL + '/getStandings',
            params={
                'hl': hl,
                'tournamentId': tournament_id
            }
        )

        return json.loads(response.text)['data']

    def get_schedule(self, hl='en-US', league_id=None, pageToken=None):
        response = self.session.get(
            self.API_URL + '/getSchedule',
            params={
                'hl': hl,
                'leagueId': league_id,
                'pageToken': pageToken
            }
        )

        return json.loads(response.text)['data']

    def get_live(self, hl='en-US'):
        response = self.session.get(
            self.API_URL + '/getLive',
            params={'hl': hl}
        )

        return json.loads(response.text)['data']

    def get_completed_events(self, hl='en-US', tournament_id=None):
        response = self.session.get(
            self.API_URL + '/getCompletedEvents',
            params={
                'hl': hl,
                'tournamentId': tournament_id
            }
        )

        return json.loads(response.text)['data']

    def get_event_details(self, match_id, hl='en-US'):
        response = self.session.get(
            self.API_URL + '/getEventDetails',
            params={
                'hl': hl,
                'id': match_id
            }
        )

        return json.loads(response.text)['data']

    def get_games(self, hl='en-US', match_id=None):
        response = self.session.get(
            self.API_URL + '/getGames',
            params={
                'hl': hl,
                'id': match_id
            }
        )

        return json.loads(response.text)['data']

    def get_teams(self, hl='en-US', team_slug=None):
        response = self.session.get(
            self.API_URL + '/getTeams',
            params={
                'hl': hl,
                'id': team_slug
            }
        )

        return json.loads(response.text)['data']

    def get_window(self, game_id, starting_time=None):
        response = self.session.get(
            self.LIVESTATS_API + f'/window/{game_id}',
            params={
                'startingTime': starting_time
            }
        )

        return json.loads(response.text)

    def get_details(self, game_id, starting_time=None, participant_ids=None):
        response = self.session.get(
            self.LIVESTATS_API + f'/details/{game_id}',
            params={
                'startingTime': starting_time,
                'participantIds': participant_ids
            }
        )

        return json.loads(response.text)
