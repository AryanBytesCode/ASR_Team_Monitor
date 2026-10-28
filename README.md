# ASReview Reviewer Analytics Dashboard

## Overview
The ASReview Reviewer Analytics Dashboard is a standalone Flask-based web application. It connects to an active ASReview LAB instance and provides a graphical dashboard to view reviewer-specific metrics. 

It allows you to:
- Securely log in using your ASReview LAB credentials.
- View a list of your ASReview projects.
- Access detailed screening metrics per project, including total records screened, and individual reviewer contributions (relevant, irrelevant, and inclusion rates).

## Package Contents
- `app.py`, `asreview_client.py`, `metrics.py`: The core Flask application and ASReview API client.
- `templates/`, `static/`: HTML templates and static assets for the web UI.
- `requirements.txt`: Python dependencies needed to run the application.
- `start.sh`: A convenient Bash script to start the application via Gunicorn.
- `config.env`: Default environment configuration file.

## Requirements
- Python 3.8 or higher.
- Access to an active ASReview LAB instance (v3.0+ with Server/API mode enabled).

## Deployment Instructions

### 1. Extract the Application
Extract the provided ZIP file to your preferred deployment location on your server or local machine.

### 2. Install Dependencies
It is highly recommended to use a Python virtual environment to isolate the application's dependencies.

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

### 3. Configure the Application
The application is configured using environment variables. You can define these in a `.env` file in the root of the extracted directory.

Create a new file named `.env`:
```bash
nano .env
```

Add your configuration:
```properties
# The URL of your running ASReview LAB backend API
ASREVIEW_BASE_URL=http://your-remote-asreview:8081

# The port you want this analytics dashboard to listen on
PORT=5050

# A secret key for Flask session security (change to a random string in production)
FLASK_SECRET_KEY=super-secret-key-replace-me

# Number of Gunicorn worker processes to spawn
WORKERS=4
```

### 4. Start the Application
You can start the application using the included `start.sh` script. This script automatically reads your `.env` file and starts the Flask app using Gunicorn.

```bash
# Ensure the script is executable
chmod +x start.sh

# Run the application
./start.sh
```

*(Optional: To run this in the background, you can use `nohup ./start.sh &`, or configure a systemd service.)*

### 5. Access the Dashboard
Once started, open your web browser and navigate to `http://<your-server-ip>:<PORT>` (e.g., `http://localhost:5050`). Log in using your existing ASReview credentials.
