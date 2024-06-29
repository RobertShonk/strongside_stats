import functools

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


# get summoner json
@bp.route('/summoners/summoner/by-riot-name/<game_name>/<tag_line>')
def get_summoner_json(game_name, tag_line):
    summoner = query.get_summoner(game_name, tag_line)
    return jsonify(summoner)


# get matches json
# returns list of lists of dicts of matches.
@bp.route('/matches/by-game-name/<game_name>/<tag_line>')
def get_matches(game_name, tag_line):
    matches = query.get_matches_by_game_name(game_name, tag_line)
    # matches[0] = first match, a list of participants
    # matches[0][1] = second participant of first match
    ms = []
    for match in matches:
        match = [dict(m) for m in match]
        ms.append(match)
    return jsonify(ms)


# functions used to get test data.
# gets a single match and its 20 participants
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
    

# gets a summoner
@bp.route('/get_summoner', methods=['POST'])
def get_summoner():
    if request.method == 'POST':
        account = riot_api.get_account("vergita", "NA1")
        summoner = riot_api.get_summoner(account['puuid'])
        league = riot_api.get_league(summoner['id'])

        res = query.insert_summoner(account, summoner, league)
        print(res)

        return redirect(url_for('api.index'))
    

# TODO make routes for inserting/updating summoner and inserting matches+participants
# want to get account, summoner, league, match_ids, matches
# literally does result() but only responds to post and returns response code only
# used for whenever players want to insert their info for the first time or to update existing info.
@bp.route('/insert_update', methods=['POST', 'GET'])
def insert_update():
    if request.method == 'POST':
        # want to get account, summoner, league, match_ids, matches
        summoner_name = request.form['summoner_name']
        tag_line = request.form['tag_line']

        account = riot_api.get_account(summoner_name, tag_line)
        summoner = riot_api.get_summoner(account['puuid'])
        league = riot_api.get_league(summoner['id'])

        res1 = query.insert_summoner(account, summoner, league)

        match_ids = riot_api.get_match_list(account['puuid'])
        matches = []
        for id in match_ids:
            match = riot_api.get_match(id)
            matches.append(match)

        res2 = query.insert_matches(matches)

        res3 = ""
        for match in matches:
            participants = match['info']['participants']
            res3 = query.insert_participants(participants, match['metadata']['matchId'])

        return res3
    
    return "shouldve been a post"
    

# gets summoner and list of matches by summoner_name + game_name.
@bp.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        summoner_name = request.form['summoner_name']
        tag_line = request.form['tag_line']

        account = riot_api.get_account(summoner_name, tag_line)
        summoner = riot_api.get_summoner(account['puuid'])
        league = riot_api.get_league(summoner['id'])

        res1 = query.insert_summoner(account, summoner, league)

        match_ids = riot_api.get_match_list(account['puuid'])
        matches = []
        for id in match_ids:
            match = riot_api.get_match(id)
            matches.append(match)

        res2 = query.insert_matches(matches)

        res3 = ""
        for match in matches:
            participants = match['info']['participants']
            res3 = query.insert_participants(participants, match['metadata']['matchId'])

        return redirect(url_for('api.result', summoner_name=summoner_name, tag_line=tag_line))
    
    # get request
    summoner_name = request.args.get('summoner_name')
    tag_line = request.args.get('tag_line')

    summoner = query.get_summoner(summoner_name, tag_line)

    # list of list of dicts
    matches = query.get_matches_by_game_name(summoner_name, tag_line)

    return render_template('api/result.html', summoner=summoner, matches=matches)