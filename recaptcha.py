import queue
import threading
import webbrowser

import flask


def run_app(q):
    app = flask.Flask(__name__)

    @app.route("/")
    def route_index():
        return flask.send_from_directory(".", "recaptcha.html")

    @app.route("/token", methods=["POST"])
    def route_token():  # type: ignore
        q.put(flask.request.json["token"])  # type: ignore
        return "", 204

    # silence unused variable warnings
    _ = route_index
    _ = route_token

    app.run(host="127.0.0.1", port=8888)


def get_token(site_key):
    q = queue.Queue(maxsize=1)

    # The server runs on a daemon thread rather than in a subprocess because
    # Windows spawns subprocesses instead of forking them, and the closure we
    # would need to pass as the subprocess target is not picklable.
    server = threading.Thread(target=lambda: run_app(q), daemon=True)
    server.start()
    webbrowser.open(f"http://localhost:8888#{site_key}")

    return q.get()
