from sys import exc_info
import trello
import hipchat
import datetime
import json
import redis
from flask import Flask
from settings import DEBUG, REDIS_URL, DATE_FORMAT

app = Flask(__name__)
app.secret_key = '\xa35\xba\xf7\xb8\xc7\xbf\x97\xf4\xb5?\x99\xe5G\xc1\xbc\xdc\xb4\xaa\xe2\xc0\x0e\xde\x89'
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
    if r.exists(redis_key):
        app.logger.debug('Getting since date from redis')
        since = datetime.datetime.strptime(r.get(redis_key), DATE_FORMAT)
    else:
        since = datetime.datetime.now()

    app.logger.debug('\'since\': {0}'.format(since.isoformat()))

    try:
        comments = []
        for comment in trello.yield_latest_comments(board=board, since=since):
            if comment.timestamp > since:
                since = comment.timestamp
            comments.append(str(comment))
            hipchat.send_message(str(comment), room)
        r.set(redis_key, since.isoformat())
        # TODO: this return value isn't much use to anyone. Should probably
        # return the list of comments?
        app.logger.debug(comments)
        return json.dumps({'result': 'success', 'timestamp': since.isoformat()})
    except:
        app.logger.error(str(exc_info()[1]))
        return json.dumps({'result': 'error', 'exception': str(exc_info()[1])})


@app.route('/favicon.ico', methods=['GET'])
def get_favicon():
    """ Swallows the Chrome favicon request. """
    return ''

if __name__ == '__main__':
    app.run(debug=DEBUG)
