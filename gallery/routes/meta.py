from quart import Blueprint, redirect


bp = Blueprint('meta', 'meta')


@bp.route('/about')
async def about():
    return redirect('https://art101.io')
