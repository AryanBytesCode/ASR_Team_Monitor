"""
ASReview API Client for the Analytics Web Application.
Handles authentication, project queries, and RIS dataset downloads.
"""

import requests


def login_to_asreview(base_url: str, email: str, password: str):
    """
    Authenticate against ASReview LAB server.
    Returns:
        (success: bool, data_or_error: dict|str, cookies: dict)
    """
    signin_url = f"{base_url.rstrip('/')}/auth/signin"
    try:
        session = requests.Session()
        resp = session.post(
            signin_url,
            data={"email": email, "password": password},
            timeout=10
        )
        if resp.status_code == 200:
            user_data = resp.json()
            cookies = session.cookies.get_dict()
            return True, user_data, cookies
        else:
            try:
                err_data = resp.json()
                msg = err_data.get("message") or err_data.get("description") or f"Status {resp.status_code}"
            except Exception:
                msg = f"Failed with status code {resp.status_code}"
            return False, msg, {}
    except requests.exceptions.RequestException as e:
        return False, f"Could not connect to ASReview server: {e}", {}


def get_user_projects(base_url: str, cookies: dict):
    """
    Fetch the list of projects accessible to the authenticated user.
    """
    projects_url = f"{base_url.rstrip('/')}/api/projects"
    resp = requests.get(projects_url, cookies=cookies, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("result", [])


def fetch_project_dataset_ris(base_url: str, cookies: dict, project_id: str):
    """
    Export the screened dataset for a project in RIS format with reviewer metadata.
    Includes both relevant and irrelevant records.
    """
    export_url = f"{base_url.rstrip('/')}/api/projects/{project_id}/export_dataset"
    params = [
        ("collections", "relevant"),
        ("collections", "irrelevant"),
        ("format", "ris"),
        ("export_name", "1"),
        ("export_email", "1"),
        ("export_groups", "1")
    ]
    resp = requests.get(export_url, cookies=cookies, params=params, timeout=30)
    resp.raise_for_status()
    return resp.text
