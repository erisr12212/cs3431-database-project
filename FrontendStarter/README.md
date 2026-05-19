# PyQt6 API Client Skeleton

A minimal Python desktop frontend built with PyQt6. It includes a simple window and an API client service for issuing GET and POST requests to a backend API.

## Features

- PyQt6 desktop UI
- Configurable base API URL
- Reusable `APIClient` with `get` and `post` methods
- Background request worker so the UI stays responsive
- Simple JSON payload editor and response viewer

## Project Layout

```text
app/
  main.py
  config.py
  services/api_client.py
  ui/main_window.py
  workers/request_worker.py
run.py
requirements.txt
```

## Setup

```zsh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```zsh
python run.py
```

## How to adapt it

- Update `API_BASE_URL` in `app/config.py`
- Use the UI to enter a relative path like `/posts/1`
- For POST requests, enter JSON in the payload box
- Replace the demo endpoints with your real API routes

## Major request methods

- `APIClient.get(endpoint, params=None, headers=None, timeout=None)`
- `APIClient.post(endpoint, json_body=None, headers=None, timeout=None)`
- `MainWindow.send_get_request()`
- `MainWindow.send_post_request()`
- `MainWindow._start_request(method, endpoint, payload=None)`

## Notes

- Requests run in a background `QThread`
- Responses are shown as formatted JSON when possible
- Errors are surfaced in the response panel and status bar
