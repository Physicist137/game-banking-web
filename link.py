import datetime
from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for, abort
)

bp = Blueprint('link', __name__, url_prefix='/link')

from .database import database_session
from .models import Link

from sqlalchemy import or_


@bp.route('/<link>', methods=('GET', 'POST'))
def process_link(link):
	data = database_session.query(Link).filter(Link.link == link).first()
	today = datetime.datetime.utcnow().timestamp()

	# Check if the link is still active.
	if (today > data.expire_date  and  data.expire_date != -1): abort(404)
	if (data.status == Link.Status.disabled): abort(404)

	# Process the link.
	session['link'] = data.link
	return redirect(url_for('world.view', world_id=data.world_id))
