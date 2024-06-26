import functools
import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
#from werkzeug.security import check_password_has, generate_password_hash

from . import riot_api
from .db import query
from . import Constants

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/')
def index():
    return render_template('api/index.html')


# get json
@bp.route('/summoners/summoner/by-riot-name/<game_name>/<tag_line>')
def get_summoner_json(game_name, tag_line):
    summoner = query.get_summoner(game_name, tag_line)

    return jsonify(summoner)


# returns list of lists of dicts of matches.
@bp.route('/matches/by-game-name/<game_name>/<tag_line>')
def get_matches(game_name, tag_line):
    matches = query.get_matches_by_game_name(game_name, tag_line)

    # matches[0] = first match, a list of participants
    # matches[0][1] = second participant of first match
    return jsonify(matches[0])


# functions used to get test data.
#gets a single match and its 10 participants
@bp.route('/get_match', methods=['POST'])
def get_match():
    if request.method == 'POST':
        match_list = riot_api.get_match_list(Constants.TEST_PUUID)
        match = riot_api.get_match(match_list[0])
        res1 = query.insert_match(match)
        print(res1)

        participants = match['info']['participants']
        res2 = query.insert_participants(participants, match['metadata']['matchId'])
        print(res2)

        return redirect(url_for('api.index'))
    

#gets a summoner
@bp.route('/get_summoner', methods=['POST'])
def get_summoner():
    if request.method == 'POST':
        account = riot_api.get_account("vergita", "NA1")
        summoner = riot_api.get_summoner(account['puuid'])
        league = riot_api.get_league(summoner['id'])

        res = query.insert_summoner(account, summoner, league)
        print(res)

        return redirect(url_for('api.index'))