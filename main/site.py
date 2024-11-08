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
        
        if leagues[1] == 200:
            code = util.insert_leagues(leagues[0], summoner_name, tagline)
            if code == 202:
                matches = riot_api.get_matches(summoner_name, tagline)
                util.insert_matches(matches)
                return redirect(url_for('site.stats'))
            else:
                return f'{session['summoner_name']}'

        return render_template('site/stats.html', method='redirect')

    # get
    summoner_name = request.args.get('summoner_name')
    tagline = request.args.get('tagline')

    # check db if league exists for player
    db = get_db()
    leagues = db.execute(
        """
        SELECT * FROM league WHERE summoner_name LIKE ? AND tagline LIKE ?
        """,
        (summoner_name, tagline)
    ).fetchall()
    print(leagues)

    metadata_ids = db.execute('SELECT metadata_id FROM participant WHERE summonerName = ? LIMIT 20', (summoner_name,)).fetchall()
    metadata = []
    for id in metadata_ids:
        metadata.append(db.execute('SELECT * FROM metadata WHERE id = ?', (id['metadata_id'],)).fetchone())

    participants = []
    for match in metadata:
        participants.append(db.execute('SELECT * FROM participant WHERE metadata_id = ?', (match['id'],)).fetchall())

    return render_template('site/stats.html', leagues=leagues, metadata=metadata, participants=participants)