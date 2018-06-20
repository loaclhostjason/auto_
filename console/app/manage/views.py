from . import manage
from flask import render_template
from flask_login import login_required
from ..decorators import role_required


@manage.route('/attrs', methods=['GET', 'POST'])
@login_required
@role_required
def attrs():
    return render_template('manage/attrs.html')
