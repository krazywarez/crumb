import os
from datetime import datetime
from flask import Flask, request

app = Flask(__name__)
LOG_PATH = os.path.expanduser("~/.crumb/history.org")

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)


@app.after_request
def add_cors_headers(response):
    """
    Add CORS headers to the response to allow cross-origin requests.

    Args:
        response (flask.Response): The response object to modify.

    Returns:
        flask.Response: The modified response object with CORS headers.
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/", methods=["POST", "OPTIONS"])
def log_visit():
    """
    Handle POST requests to log visit information and OPTIONS requests for CORS preflight.

    For POST requests, parse JSON data from the request, extract visit details,
    and append them to the log file in org-mode format.

    For OPTIONS requests, return a 204 No Content response.

    Returns:
        tuple: An empty string and the HTTP status code 204.
    """
    if request.method == "OPTIONS":
        return "", 204

    data = request.json
    title = data.get("title", "No Title")
    url = data.get("url", "No URL")
    hostname = data.get("hostname", "")
    path = data.get("path", "")
    query = data.get("query", "")
    tab_id = data.get("tabId", "")
    window_id = data.get("windowId", "")
    favicon = data.get("favIconUrl", "")
    timestamp = datetime.utcnow().isoformat()

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"* {title}\n")
        f.write(":PROPERTIES:\n")
        f.write(f":URL:       {url}\n")
        f.write(f":TIMESTAMP: {timestamp}\n")
        f.write(f":HOST:      {hostname}\n")
        f.write(f":PATH:      {path}\n")
        if query:
            f.write(f":QUERY:     {query}\n")
        f.write(f":TAB:       {tab_id}\n")
        f.write(f":WINDOW:    {window_id}\n")
        if favicon:
            f.write(f":FAVICON:   {favicon}\n")
        f.write(":END:\n\n")

    return "", 204


if __name__ == "__main__":
    """
    Run the Flask application on port 3555 when executed as the main program.
    """
    app.run(port=3555)
