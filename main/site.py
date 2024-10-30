import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from main.db import get_db

bp = Blueprint('site', __name__)


@bp.route('/')
def index():
    return render_template('site/index.html')