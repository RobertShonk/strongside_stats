import functools
import json
import time

import requests
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)

from . import Constants
from . import riot_api
from .db import query

bp = Blueprint('site', __name__)


@bp.route('/')
def index():
    return render_template('site/index.html')


@bp.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        summoner_name = request.form['summoner_name']
        tag_line = request.form['tag_line']

        account = riot_api.get_account(summoner_name, tag_line)
        summoner = riot_api.get_summoner(account['puuid'])
        league = riot_api.get_league(summoner['id'])

        if summoner and account and len(league) > 0:
            res1 = query.insert_summoner(account, summoner, league)

            if res1 == 200 or res1 == 201:
                match_ids = riot_api.get_match_list(account['puuid'])

                if len(match_ids) > 0:
                    matches = []

                    for id in match_ids:
                        m = riot_api.get_match(id)
                        time.sleep(1/20) # limit api requests. currently 20 requests per seconds limit (so sleep 1 / 20th of a second)
                        matches.append(m)

                    if len(matches) > 0:
                        res2 = query.insert_matches(matches)

                        res3 = 0
                        for match in matches:
                            participants = match['info']['participants']
                            m_id = match['metadata']['matchId']
                            res3 = query.insert_participants(participants, m_id)

                        return redirect(url_for('site.result', summoner_name=summoner_name, tag_line=tag_line))

        return "posty boys"

    summoner_name = request.args.get('summoner_name')
    tag_line = request.args.get('tag_line')

    summoner = requests.get(f"{Constants.SITE['summoner_url']}{summoner_name}/{tag_line}").json()
    matches = requests.get(f"{Constants.SITE['matches_url']}{summoner_name}/{tag_line}").json()

    if summoner != 404 and matches != 404:
        with open('app\static\dragontail\data\summoner.json') as f:
            sum_spell_ids = json.load(f)

        return render_template('site/result.html', summoner=summoner, matches=matches, sum_spell_ids=sum_spell_ids['data'])
    
    return render_template('site/result.html', summoner=None, matches="404", sum_spell_ids=None)
    