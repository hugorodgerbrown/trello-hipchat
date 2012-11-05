from sys import exc_info
import trello
import hipchat
import datetime
import json
import redis
from flask import Flask, request
from settings import DEBUG, REDIS_URL, DATE_FORMAT

app = Flask(__name__)
app.secret_key = 'make_up_something_really_random_here'
app.debug = DEBUG

SESSION_KEY_SINCE = 'since'


@app.route('/<board>/<int:room>', methods=['GET'])
def get_board_comments(board, room):
    """ Uses the trello lib to fetch latest comments from a board.

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
    """
    redis_key = '{0}_{1}'.format(board, room)
    r = redis.from_url(REDIS_URL)
    if 'test' in request.args:
        since = datetime.datetime.strptime('2012-01-01T00:00:00.000', DATE_FORMAT)
    elif r.exists(redis_key):
        since = datetime.datetime.strptime(r.get(redis_key), DATE_FORMAT)
    else:
        since = datetime.datetime.now()

    app.logger.debug("Processing request: board={0}, room={1}, "
        "since={1}]".format(board, room, since.isoformat()))

    try:
        count = 0
        for comment, timestamp in trello.yield_actions(board=board, since=since):
            count += 1
            if timestamp > since:
                since = timestamp
            if 'no-publish' not in request.args:
                hipchat.send_message(str(comment), room)
        r.set(redis_key, since.isoformat())
        return json.dumps({'result': 'success',
            'timestamp': since.isoformat(),
            'actions': count})
    except:
        app.logger.error(repr(exc_info()[0]))  # type
        app.logger.error(repr(exc_info()[1]))  # value (message)
        app.logger.error(repr(exc_info()[2]))  # stack trace
        return json.dumps({'result': 'error', 'exception': str(exc_info()[1])})


@app.route('/favicon.ico', methods=['GET'])
def get_favicon():
    """ Swallows the Chrome favicon request. """
    return ''

if __name__ == '__main__':
    app.run(debug=DEBUG)
