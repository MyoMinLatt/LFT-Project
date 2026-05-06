from flask import Blueprint, render_template
from services.monitoring import get_monitoring_data

monitoring_bp = Blueprint("monitoring", __name__)


@monitoring_bp.route("/monitoring")
def monitoring():

    data = get_monitoring_data()

    return render_template(
        "dashboard.html",
        data=data
    )
