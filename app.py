from os import environ
import trello
import hipchat
import datetime
from flask import Flask, session, escape

app = Flask(__name__)


@app.route('/<board>/<int:room>', methods=['GET'])
def get_board_comments(board, room):
    """ Uses the trello lib to fetch latest comments from a board. """
    if 'since' in session:
        print 'fetching since from session'
        since = session['since']
    else:
        print 'setting since to today()'
        since = datetime.datetime(year=2012, month=1, day=1)
    print 'since: {0}'.format(since)
    for comment in trello.yield_latest_comments(board=board, since=since):
        print str(comment)
        if comment.date > since:
            print 'updating since from {0} to {1}'.format(since, comment.date)
            since = comment.date
        hipchat.send_message(str(comment), room)
    session['since'] = since
    print escape(since)
    return str(since)


@app.route('/favicon.ico', methods=['GET'])
def get_favicon():
    """ Swallows the Chrome favicon request. """
    return ''

if __name__ == '__main__':
    import settings  # import just to validate that settings exist
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(environ.get('PORT', 5000))
    app.debug = True
    app.secret_key = 'something_really_really_secret'
    app.run(host='0.0.0.0', port=port)
