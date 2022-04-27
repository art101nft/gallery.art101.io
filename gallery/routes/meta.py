from quart import Blueprint, render_template


bp = Blueprint('meta', 'meta')


@bp.route('/about')
async def about():
    return await render_template('about.html')
