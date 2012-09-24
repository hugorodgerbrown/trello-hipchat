import trello
import hipchat
import datetime
import json
from flask import Flask, session

app = Flask(__name__)


@app.route('/<board>/<int:room>', methods=['GET'])
def get_board_comments(board, room):
    """ Uses the trello lib to fetch latest comments from a board. """

    try:
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
                print 'updating \'since\' from {0} to {1}'.format(since, comment.date)
                since = comment.date
            hipchat.send_message(str(comment), room)
        session['since'] = since
        return json.dumps({'since': since.isoformat()})
    except:
        from sys import exc_info
        return json.dumps({'exception': str(exc_info()[1])})


@app.route('/favicon.ico', methods=['GET'])
def get_favicon():
    """ Swallows the Chrome favicon request. """
    return ''

if __name__ == '__main__':
    import settings  # import just to validate that settings exist
    # Bind to PORT if defined, otherwise default to 5000.
    app.debug = True
    app.secret_key = '\xa35\xba\xf7\xb8\xc7\xbf\x97\xf4\xb5?\x99\xe5G\xc1\xbc\xdc\xb4\xaa\xe2\xc0\x0e\xde\x89'
    app.run()
