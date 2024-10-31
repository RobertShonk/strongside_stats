import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from main.db import get_db

bp = Blueprint('site', __name__)


@bp.route('/')
def index():
    return render_template('site/index.html')


@bp.route('/stats', methods=('GET', 'POST'))
def stats():
    if request.method == 'POST':
        # do something if post (probably want to update info)
        return 'stats post'

    # get
    summoner_name = request.args.get('summoner_name')
    tagline = request.args.get('tagline')

    # check db if summoner exists
    db = get_db()
    data = db.execute(
        """
        SELECT * FROM league WHERE summoner_name = ? AND tagline = ?
        """,
        (summoner_name, tagline)
    ).fetchone()

    # if exists, render template with player info
    if data:
        return render_template('site/stats.html', data=data)

    
    # if not render with none

    return render_template('site/stats.html', summoner_name=summoner_name, tagline=tagline)