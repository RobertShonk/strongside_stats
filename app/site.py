import functools
import json

import requests
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)

from . import Constants

bp = Blueprint('site', __name__)


@bp.route('/')
def index():
    return render_template('site/index.html')


@bp.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        return "posty boys"

    summoner_name = request.args.get('summoner_name')
    tag_line = request.args.get('tag_line')

    summoner = requests.get(f"{Constants.SITE['summoner_url']}{summoner_name}/{tag_line}").json()
    matches = requests.get(f"{Constants.SITE['matches_url']}{summoner_name}/{tag_line}").json()

    if summoner != "404" and matches != "404":
        with open('app\static\dragontail\data\summoner.json') as f:
            sum_spell_ids = json.load(f)

        return render_template('site/result.html', summoner=summoner, matches=matches, sum_spell_ids=sum_spell_ids['data'])
    
    return render_template('site/result.html', summoner=None, matches="404", sum_spell_ids=None)
    