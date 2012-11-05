import requests
import datetime
from settings import (TRELLO_API_KEY, TRELLO_API_TOKEN, DATE_FORMAT_Z)
import logging

TRELLO_API_URL = 'https://trello.com/1/boards/{0}/actions'
TRELLO_PERMALINK_CARD = 'https://trello.com/card/{0}/{1}'


def parse_trello_action(action):
    """ Parses out a HipChat message from an action.

        Currently supported actions are commentCard, createCard & updateCard.
    """
    if action['type'] == 'createCard':
        return ("{member} created a new card on <i>{board} / {list}</i> "
            "called <b>{card}</b> (<a href='{link}'>link</a>)".format(
                member=action['memberCreator']['fullName'],
                board=action['data']['board']['name'],
                list=action['data']['list']['name'],
                card=action['data']['card']['name'],
                link=get_card_permalink(action['data'])))

    elif action['type'] == 'updateCard':
        # we are currently only processing cards that move between lists
        # use existence of data.listBefore and data.listAfter to recognise
        try:
            return("{member} moved card <b>{card}</b> from <i>{list_before}</i> to <i>{list_after}</i> on <i>{board}</i> (<a href='{link}'>link</a>)".format(
                    card=action['data']['card']['name'],
                    list_before=action['data']['listBefore']['name'],
                    list_after=action['data']['listAfter']['name'],
                    member=action['memberCreator']['fullName'],
                    board=action['data']['board']['name'],
                    link=get_card_permalink(action['data'])))
        except KeyError as ex:
            logging.warning('updateCard action is not a list movement.')
            logging.error(ex)

    elif action['type'] == 'commentCard':
        return ("{member} commented on card <b>{card}</b> on board <i>{board}</i> (<a href='{link}'>link</a>): <i>{comment}</i>".format(
                member=action['memberCreator']['fullName'],
                card=action['data']['card']['name'],
                board=action['data']['board']['name'],
                comment=action['data']['text'],
                link=get_card_permalink(action['data'])))

    else:
        logging.debug('Unexpected action type: {0}'.format(action['type']))


def get_card_permalink(data):
    """ Return the card permalink as parsed out from the ['data'] node of the
        returned JSON.
    """
    return TRELLO_PERMALINK_CARD.format(
        data['board']['id'],
        data['card']['idShort']
    )


def yield_actions(board, limit=5, page=0, since=None, filter='updateCard,commentCard,createCard'):
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
        'filter': filter,
        'page': page,
        'limit': limit,
        'since': since.isoformat()}
    url = TRELLO_API_URL.format(board)
    data = requests.get(url, params=params)
    if data.status_code == 200:
        for action in data.json:
            message = parse_trello_action(action)
            timestamp = datetime.datetime.strptime(action['date'], DATE_FORMAT_Z)
            yield message, timestamp
    else:
        logging.error('Error retrieving Trello data: {0}'.format(data.reason))
