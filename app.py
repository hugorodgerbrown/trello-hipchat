"""
Main entry point for the Trello-HipChat Flask app.

Run this on its own in development:

    $ python app.py

Or through gunicorn in production:

    $ gunicorn app:app
"""
from sys import exc_info
# import trello
# import hipchat
import datetime
import json
import redis
from flask import Flask, request
from settings import DEBUG, REDIS_URL, DATE_FORMAT
from api import trello, hipchat

app = Flask(__name__)
# app.secret_key = 'make_up_something_really_random_here'
app.debug = DEBUG

SESSION_KEY_SINCE = 'since'


@app.route('/<board>/<int:room>', methods=['GET'])
def get_board_comments(board, room):
    """
    Uses the trello lib to fetch latest comments from a board.

    This method will fetch all commentCard actions from the Trello board,
    and post each comment to the HipChat room.

    It stores a timestamp (from the most recent commentCard retreived) in
    redis, and uses this on subsequent requests to prevent duplicates
    from being returned. The redis key is a deterministic ID that combines
    the board and room in the form {{board}}_{{room}}. This means that the
    app can be called for different combinations of board and room, although
    NB it stores only one set of Trello & HipChat API credentials, so it
    doesn't support lots of different people.

    On the first run, when there is no timestamp, it is set to the current
    time. NB there are some timezone issues with this - but unfortunately
    the Trello API doesn't return timestamps with a TZ, so I'm not sure
    what zone they are in.

    Args:
        board: the id of the Trello board to subscribe to. This can be found
            by looking at the URL of a board - which will contain both the
            board name and its id: https://trello.com/board/{{name}}/{{id}}
            Make sure you use the id, and not the name.

        room: the numeric id of the HipChat room to post updates to. This can
            be found by going to /rooms/ids on your hipchat.com account.

    Returns:
        If no errors occur, this will return JSON that contains the number of
        comments posted, and the timestamp of the latest update. If there was
        an error, then it is returned, along with a 'result' value of 'error'.
    """
    redis_key = '{0}_{1}'.format(board, room)
    r = redis.from_url(REDIS_URL)
    if 'test' in request.args:
        since = datetime.datetime.strptime('2012-01-01T00:00:00.000', DATE_FORMAT)
    elif r.exists(redis_key):
        since = datetime.datetime.strptime(r.get(redis_key), DATE_FORMAT)
    else:
        since = datetime.datetime.today()
        r.set(redis_key, since.isoformat())

    app.logger.debug(
        "Processing request: board={0}, room={1}, "
        "since={2}".format(board, room, since.isoformat()))

    try:
        actions = trello.get_actions(board=board, since=since)
        for comment, timestamp in actions:
            if timestamp > since:
                app.logger.debug(
                    "Resetting timestamp for redis key '%s' to %s"
                    % (redis_key, timestamp))
                r.set(redis_key, timestamp.isoformat())
            if 'no-publish' not in request.args:
                app.logger.debug("Publishing update to HipChat: %s" % comment)
                response = hipchat.send_message(str(comment), room)
                app.logger.debug("HipChat API response: %s" % response.status_code)
                if response.status_code != 200:
                    app.logger.debug(response.text)
        return json.dumps({
            'result': 'success',
            'timestamp': since.isoformat(),
            'actions': len(actions)})
    except:
        # yes, I know a blanket except is a bad idea, but in this situation
        # it does the job.
        app.logger.exception("Error raised processing Trello updates.")
        return json.dumps({'result': 'error', 'exception': str(exc_info()[1])})


@app.route('/favicon.ico', methods=['GET'])
def get_favicon():
    """Swallow the Chrome favicon request."""
    return ''

if __name__ == '__main__':
    app.run(debug=DEBUG)
