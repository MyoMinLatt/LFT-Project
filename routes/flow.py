from flask import Blueprint, render_template

flow_bp = Blueprint("flow", __name__)

@flow_bp.route("/flow_diagram")
def flow_diagram():
    return render_template("flow_diag.html")