from flask import Blueprint, render_template


bp = Blueprint('meta', 'meta')


@bp.route('/about')
def about():
    return render_template('about.html')
