from flask import (Blueprint, Response, render_template, current_app, abort, g,
    url_for, request, session)
from galatea.tryton import tryton
from galatea.utils import slugify
from galatea.helpers import customer_required
from flask_babel import gettext as _, lazy_gettext
from flask_login import login_required

production = Blueprint('production', __name__, template_folder='templates')

DISPLAY_MSG = lazy_gettext('Displaying <b>{start} - {end}</b> of <b>{total}</b>')
LIMIT = current_app.config.get('TRYTON_PAGINATION_PROJECT_LIMIT', 20)

Production = tryton.pool.get('production')
ProductionReport = tryton.pool.get('production.report', type='report')

@production.route("/", endpoint="productions")
@login_required
@customer_required
@tryton.transaction()
def production_list(lang):
    '''Productions'''

    if hasattr(Production, 'get_flask_production_domain'):
        domain = Production.get_flask_production_domain(
            external_workshop=session['customer'])
    else:
        domain = []

    productions = Production.search(domain)

    breadcrumbs = [{
        'slug': url_for('my-account', lang=g.language),
        'name': _('My Account'),
        }, {
        'slug': url_for('.productions', lang=g.language),
        'name': _('Productions'),
        }]

    return render_template('productions.html',
            breadcrumbs=breadcrumbs,
            productions=productions,
            )

@production.route("/print/<int:id>", endpoint="production_print")
@login_required
@customer_required
@tryton.transaction()
def production_print(lang, id):
    '''Production Print'''

    domain = [
        ('id', '=', id),
        ('external_workshop', '=', session['customer']),
        ]
    productions = Production.search(domain, limit=1)
    if not productions:
        abort(404)
    production, = productions
    _, report, _, _ = ProductionReport.execute([production.id], {})
    report_name = 'production-%s.pdf' % (slugify(production.reference) or
        'production')

    return Response(report, mimetype="application/pdf")
