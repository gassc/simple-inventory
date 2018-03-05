from threading import Thread, Lock
import logging
import webview
from time import sleep
from project.app import app

server_lock = Lock()

logger = logging.getLogger(__name__)


def url_ok(url, port):
    from http.client import HTTPConnection

    try:
        conn = HTTPConnection(url, port)
        conn.request("GET", "/")
        r = conn.getresponse()
        return r.status == 200
    except:
        logger.exception("Server not started")
        return False


def run_server():
    app.run(host="127.0.0.1", port=23948, threaded=True, debug=False)


if __name__ == '__main__':
    logger.debug("Starting server")
    t = Thread(target=run_server)
    t.daemon = True
    t.start()
    logger.debug("Checking server")

    while not url_ok("127.0.0.1", 23948):
        sleep(0.1)

    logger.debug("Server started")
    webview.create_window(
        app.config['APP_TITLE'], "http://127.0.0.1:23948", min_size=(320, 240), fullscreen=False)
