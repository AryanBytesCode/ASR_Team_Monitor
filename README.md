# ASReview Reviewer Analytics Dashboard

## Overview
The ASReview Reviewer Analytics Dashboard is a standalone Flask-based web application. It connects to an active ASReview LAB instance and provides a graphical dashboard to view reviewer-specific metrics. 

It allows you to:
- Securely log in using your ASReview LAB credentials.
- View a list of your ASReview projects.
- Access detailed screening metrics per project, including total records screened, and individual reviewer contributions (relevant, irrelevant, and inclusion rates).
- **Set Weekly Goals and visually track progress toward goals for each reviewer.**
- **Monitor overdue records based on the project's start date and weekly expectations.**

## Package Contents
- `app.py`, `asreview_client.py`, `metrics.py`: The core Flask application and ASReview API client.
- `templates/`, `static/`: HTML templates and static assets for the web UI.
- `docker-compose.yaml`, `Dockerfile`, `docker-entrypoint.sh`: Files for deploying the app in a containerized environment (with Cloudflare Tunnel support).
- `requirements.txt`: Python dependencies needed to run the application natively.
- `start.sh`: A convenient Bash script to start the application natively.
- `.env.example`: Default environment configuration template.

## Requirements
- Access to an active ASReview LAB instance (v3.0+ with Server/API mode enabled).
- **Docker and Docker Compose** (Recommended for deployment).
- Python 3.8+ (If deploying natively).

## Deployment Instructions (Docker - Recommended)

### 1. Extract the Application
Extract the provided ZIP file or clone the repository to your preferred deployment location.

### 2. Configure the Application
Copy the provided example environment file to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and configure your settings:
- `ASREVIEW_BASE_URL`: The URL of your running ASReview LAB backend API.
- `WEEKLY_GOAL`: Number of records each reviewer is expected to screen per week.
- `PROJECT_START_DATE`: The date the project started (YYYY-MM-DD).
- `WEEK_START_DAY`: Which day starts the week (0=Monday, 6=Sunday).
- `TUNNEL_TOKEN`: Your Cloudflare Zero Trust tunnel token (required for **Option A**).
- `DOMAIN`: Your custom public domain name (required for **Option B**).
- `LETSENCRYPT_EMAIL`: Your email address for TLS certificate expiry notices (required for **Option B**).

### 3. Start the Application

You can expose the application securely using either Cloudflare Tunnels or Nginx with Let's Encrypt. Choose the option that fits your infrastructure:

#### Option A: Cloudflare Tunnel (Default)
This method is recommended if you don't want to open any inbound ports on your server's firewall. Ensure you've provided the `TUNNEL_TOKEN` in the `.env` file.
```bash
docker-compose up -d
```

#### Option B: Nginx + Let's Encrypt
This method is recommended if you have your own domain name and want to serve the dashboard directly from your server. Ensure you have pointed your domain's DNS `A` record to your server's IP address, and that ports 80 and 443 are open on your firewall.
```bash
# Use the alternative compose file tailored for Nginx
docker-compose -f docker-compose.nginx.yaml up -d
```

### 4. Access the Dashboard
- **Local Access:** Open your web browser and navigate to `http://localhost:<PORT>` (e.g., `http://localhost:5050`).
- **Cloudflare Tunnel (Option A):** Your dashboard will be automatically routed through Cloudflare to the domain you configured in your Zero Trust dashboard.
- **Nginx Custom Domain (Option B):** Wait a minute or two for the Let's Encrypt certificate to generate, then navigate to `https://<YOUR_DOMAIN>` (e.g., `https://dashboard.yourdomain.com`).

---

## Alternative Deployment (Native Python)

If you prefer not to use Docker, you can run the app natively on your host machine:

### 1. Install Dependencies
It is highly recommended to use a Python virtual environment to isolate the application's dependencies.
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure the Application
Copy `.env.example` to `.env` and edit it as described in the Docker instructions above.

### 3. Start the Application
You can start the application using the included `start.sh` script, which uses Gunicorn.
```bash
chmod +x start.sh
./start.sh
```
*(Optional: To run this in the background, you can use `nohup ./start.sh &`, or configure a systemd service.)*