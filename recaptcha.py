import multiprocessing
import webbrowser

import flask

def run_app(q):
    app = flask.Flask(__name__)

    @app.route("/")
    def route_index():
        return flask.send_from_directory(".", "recaptcha.html")

    @app.route("/token", methods=["POST"])
    def route_token():
        q.put(flask.request.json["token"])  # type: ignore
        return "", 204

    # silence unused variable warnings
    _ = route_index
    _ = route_token

    app.run(host="127.0.0.1", port=8888)


def get_token(site_key):
    q = multiprocessing.Queue(maxsize=1)

    server = multiprocessing.Process(
        target=run_app(q), daemon=True
    )
    server.start()
    webbrowser.open(f"http://localhost:8888#{site_key}")

    token = q.get()

    server.terminate()
    server.join()

    return token
