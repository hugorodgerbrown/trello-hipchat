import json
import requests
import datetime
from settings import (
    TRELLO_API_KEY,
    TRELLO_API_TOKEN,
    TRELLO_API_URL,
    TRELLO_PERMALINK_CARD,
    DATE_FORMAT_Z)


def yield_latest_comments(board, limit=5, page=0, since=None):
    """ Fetch the latest Trello comments from a board.

        :param board: the id of the board to fetch comments from
        :limit (opt): the number of comments to return - defaults to 5
        :page (opt): the page number (if paging) - defaults to 0 (first page)
        :since (opt): date, Null or lastView (default)

        This uses the `since=lastView` request parameter
        to bring back only the latest comments - but bear
        in mind that this will reset each time the program
        is run, so will need a timestamp check as well.
        Probably.
    """
    params = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN,
        'filter': 'commentCard',
        'page': page,
        'limit': limit,
        'since': since.isoformat()}
    url = TRELLO_API_URL.format(board)
    data = requests.get(url, params=params)
    print data.url
    if data.status_code == 200:
        # TODO: exception handling in case Trello doesn't like our request
        for comment in data.json:
            data_sender = comment['memberCreator']
            data_card = comment['data']['card']
            yield (CardComment(
                sender=data_sender['fullName'],
                card=data_card['name'],
                comment=comment['data']['text'],
                timestamp=datetime.datetime.strptime(comment['date'], DATE_FORMAT_Z),
                link=TRELLO_PERMALINK_CARD.format(data_card['id'], data_card['idShort'])))
    else:
        print data.reason


class CardComment():
    """ Entity class modelling a comment on a card. """

    def __init__(self, sender, card, comment, timestamp, link):
        self.sender = sender
        self.card = card
        self.comment = comment
        self.timestamp = timestamp
        self.link = link

    def __unicode__(self):
        return "{0} commented on the <a href=\'{3}\'>card<a> \'{2}\':\n{1}".format(
            self.sender, self.comment, self.card, self.link)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def json(self):
        """ Returns the CardComment object as JSON.

            This is required because dates are not seraliazable, and so
            calling __dict__ won't work. <gnashes-teeth>Aargh</gnashes-teeth>
        """
        return json.dumps({
            'sender': self.sender,
            'card': self.card,
            'comment': self.comment,  # TODO: should probably escape this
            'link': self.link,
            'timestamp': self.timestamp.isoformat()})
