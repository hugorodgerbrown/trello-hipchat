import requests
import datetime
from settings import TRELLO_API_KEY, TRELLO_API_TOKEN, TRELLO_API_URL

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fz'


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
            d = datetime.datetime.strptime(comment['date'], DATE_FORMAT)
            yield (CardComment(
                sender=comment['memberCreator']['fullName'],
                card=comment['data']['card']['name'],
                comment=comment['data']['text'],
                date=d))
    else:
        print data.reason


class CardComment():
    """ Entity class modelling a comment on a card. """

    def __init__(self, sender, card, comment, date):
        self.sender = sender
        self.card = card
        self.comment = comment
        self.date = date

    def __unicode__(self):
        return "{0} commented on the card \'{2}\':\n{1}".format(
            self.sender, self.comment, self.card)

    def __str__(self):
        return unicode(self).encode('utf-8')
