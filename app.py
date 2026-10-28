"""
Flask Application for ASReview Reviewer Analytics Dashboard.
"""

from functools import wraps
import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify
)
from dotenv import load_dotenv

from asreview_client import (
    login_to_asreview,
    get_user_projects,
    fetch_project_dataset_ris
)
from metrics import parse_asreview_ris, compute_reviewer_metrics

# Load environment configuration
load_dotenv("config.env")
load_dotenv(".env")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "asreview-analytics-default-secret-key-42")

ASREVIEW_BASE_URL = os.getenv("ASREVIEW_BASE_URL", "http://127.0.0.1:8081").rstrip("/")
PORT = int(os.getenv("PORT", 5050))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "asreview_cookies" not in session:
            flash("Please sign in to access your ASReview projects.", "warning")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


@app.context_processor
def inject_global_vars():
    return {
        "asreview_base_url": ASREVIEW_BASE_URL,
        "logged_in_user": session.get("user_name"),
        "logged_in_email": session.get("user_email")
    }


@app.route("/")
def index():
    if "asreview_cookies" in session:
        return redirect(url_for("projects_list"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please provide both email and password.", "danger")
            return render_template("login.html")

        success, data_or_err, cookies = login_to_asreview(ASREVIEW_BASE_URL, email, password)

        if success:
            session["asreview_cookies"] = cookies
            session["user_name"] = data_or_err.get("name", email)
            session["user_email"] = email
            flash(f"Welcome back, {session['user_name']}!", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("projects_list"))
        else:
            flash(f"Authentication failed: {data_or_err}", "danger")
            return render_template("login.html")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("login"))


@app.route("/projects")
@login_required
def projects_list():
    cookies = session.get("asreview_cookies", {})
    try:
        projects = get_user_projects(ASREVIEW_BASE_URL, cookies)
    except Exception as e:
        flash(f"Error fetching projects: {e}", "danger")
        projects = []
    return render_template("projects.html", projects=projects)


@app.route("/project/<project_id>")
@login_required
def project_dashboard(project_id):
    cookies = session.get("asreview_cookies", {})
    
    # 1. Fetch project metadata
    project_name = f"Project {project_id[:8]}"
    try:
        projects = get_user_projects(ASREVIEW_BASE_URL, cookies)
        for p in projects:
            if p.get("id") == project_id:
                project_name = p.get("name", project_name)
                break
    except Exception:
        pass

    # 2. Fetch dataset RIS and compute metrics
    try:
        ris_text = fetch_project_dataset_ris(ASREVIEW_BASE_URL, cookies, project_id)
        records = parse_asreview_ris(ris_text)
        metrics_data = compute_reviewer_metrics(records)
    except Exception as e:
        flash(f"Error loading project screening dataset: {e}", "danger")
        metrics_data = compute_reviewer_metrics([])

    return render_template(
        "dashboard.html",
        project_id=project_id,
        project_name=project_name,
        metrics=metrics_data
    )


@app.route("/api/project/<project_id>/metrics")
@login_required
def api_project_metrics(project_id):
    cookies = session.get("asreview_cookies", {})
    try:
        ris_text = fetch_project_dataset_ris(ASREVIEW_BASE_URL, cookies, project_id)
        records = parse_asreview_ris(ris_text)
        metrics_data = compute_reviewer_metrics(records)
        return jsonify({"success": True, "data": metrics_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    print(f"Starting ASReview Analytics Webapp on port {PORT}...")
    print(f"Connected to ASReview backend at {ASREVIEW_BASE_URL}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
