import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from main.db import get_db
import main.riot_api as riot_api
import main.util as util

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
        session['summoner_name'] = summoner_name
        session['tagline'] = tagline

        leagues = riot_api.get_league(summoner_name, tagline)
        account = riot_api.get_account(summoner_name, tagline)

        if account[1] == 200:
            summoner = riot_api.get_summoner(account[0]['puuid'])
        
        if leagues[1] == 200 and summoner[1] == 200:
            code = util.insert_leagues(leagues[0], summoner_name, tagline, summoner[0]['profileIconId'], summoner[0]['summonerLevel'])
            print(f'[stats.site]: profileIconId {summoner[0]['profileIconId']}')
            if code == 202:
                matches = riot_api.get_matches(summoner_name, tagline)
                util.insert_matches(matches)
                session['redirect'] = True
                return redirect(url_for('site.stats'))
            else:
                return f'[site.py]: {session['summoner_name']}'
        else:
            return f'[site.py] Error using Riot API using this data<br> Summoner name: {summoner_name}, Tagline: {tagline}'

        return render_template('site/stats.html', method='redirect')

    summoner_name = ''
    tagline = ''
    # get
    if 'redirect' in session.keys():
        if session['redirect'] is True:
            summoner_name = session['summoner_name']
            tagline = session['tagline']
            print(f'redirect: {session['redirect']}')
            session.pop('redirect')
    else:
        session.clear()
        summoner_name = request.args.get('summoner_name')
        tagline = request.args.get('tagline')
        session['summoner_name'] = summoner_name
        session['tagline'] = tagline
    
    # check db if league exists for player
    db = get_db()
    leagues = db.execute(
        """
        SELECT * FROM league WHERE summoner_name LIKE ? AND tagline LIKE ?
        """,
        (summoner_name, tagline)
    ).fetchall()

    metadata_ids = db.execute('SELECT metadata_id FROM participant WHERE summonerName LIKE ? LIMIT 20', (summoner_name,)).fetchall()
    metadata = []
    for id in metadata_ids:
        metadata.append(db.execute('SELECT * FROM metadata WHERE id = ?', (id['metadata_id'],)).fetchone())

    participants = []
    for match in metadata:
        participants.append(db.execute('SELECT * FROM participant WHERE metadata_id = ?', (match['id'],)).fetchall())

    return render_template('site/stats.html', leagues=leagues, metadata=metadata, participants=participants)