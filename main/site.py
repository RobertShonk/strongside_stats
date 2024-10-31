import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from main.db import get_db
import main.riot_api as riot_api

bp = Blueprint('site', __name__)


@bp.route('/')
def index():
    return render_template('site/index.html')


@bp.route('/stats', methods=('GET', 'POST'))
def stats():
    if request.method == 'POST':
        # do something if post (probably want to update info)
        summoner_name = request.form['summoner_name']
        tagline = request.form['tagline']

        leagues = riot_api.get_league(summoner_name, tagline)
        
        if leagues[1] == 200:
            return render_template('site/stats.html', data=leagues[0], method=request.method)

        return render_template('site/stats.html', data={'summoner_name': summoner_name, 'tagline': tagline}, method='redirect')

    # get
    summoner_name = request.args.get('summoner_name')
    tagline = request.args.get('tagline')

    # check db if league exists for player
    db = get_db()
    data = db.execute(
        """
        SELECT * FROM league WHERE summoner_name = ? AND tagline = ?
        """,
        (summoner_name, tagline)
    ).fetchall()

    # if exists, render template with player info
    if data:
        return render_template('site/stats.html', data=data, method=request.method)


    return render_template('site/stats.html', data={'summoner_name': summoner_name, 'tagline': tagline}, method=request.method)