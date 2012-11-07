import json
import requests
import datetime
import logging
from flask import render_template
from settings import (TRELLO_API_KEY, TRELLO_API_TOKEN, DATE_FORMAT_Z)
from jinja2.exceptions import TemplateNotFound

TRELLO_API_URL = 'https://trello.com/1/boards/{0}/actions'
TRELLO_PERMALINK_CARD = 'https://trello.com/card/{0}/{1}'


class UnsupportedTrelloActionError(Exception):
    """ Error raised when an action is returned that we cannot parse."""
    def __init__(self, action):
        """ Initialise with an instance of the TrelloAction that caused the problem."""
        self.action = action

    def __unicode__(self):
        return u"No matching template found for action: {0}".format(self.action)

    def __str__(self):
        return unicode(self).encode('utf-8')


class TrelloAction(object):
    """ Provide access to Trello API response 'action' JSON properties."""

    def __init__(self, action):
        self.action = action
        self.action_data = TrelloActionData(action['data'])

    def __unicode__(self):
        return json.dumps(self.action)

    def __str__(self):
        return unicode(self).encode('utf-8')

    @property
    def type(self):
        return self.action['type']

    @property
    def member_fullname(self):
        return self.action['memberCreator']['fullName']

    @property
    def data(self):
        return self.action_data

    @property
    def timestamp(self):
        return datetime.datetime.strptime(self.action['date'], DATE_FORMAT_Z)

    def get_hipchat_message(self):
        """ Parses out a HipChat message from an action.

            This method renders an HTML template for the action. Templates
            are stored in the /templates directory, and are named after the
            action type (commentCard, updateCard, etc.) This does replace a
            restriction in that each action has only one template, so if you
            want to use multiple message types for a single action, you'll
            need to work around this.

            If no matching template is found, then an UnsupportedTrelloActionError
            is raised. This error contains the contents of the action.
        """
        if self.type == 'updateCard' and not self.action['data'].get('listBefore'):
            # we currently only support upates that are related to moving a
            # card between lists. If this is the case, the 'data' element will
            # contain both 'listBefore' and 'listAfter' values. If these do not
            # exist, then this is some other kind of update, and we can't
            # support it. Raise the UnsupportedTrelloActionError instead.
            # NB this does not affect other actions - createCard, commentCard...
            raise UnsupportedTrelloActionError(self)

        template_name = '{type}.html'.format(type=self.type)
        try:
            return render_template(template_name, action=self)
        except TemplateNotFound:
            raise UnsupportedTrelloActionError(self)


class TrelloActionData(object):
    """ Provide access to action data."""

    def __init__(self, data):
        """ Initialises the class with the JSON data response from Trello.

            :param data: the 'action' from a Trello Response.
        """
        self.data = data

    @property
    def board_name(self):
        return self.data['board']['name']

    @property
    def card_name(self):
        return self.data['card']['name']

    @property
    def list_name(self):
        return self.data['list']['name']

    @property
    def list_before_name(self):
        return self.data['listBefore']['name']

    @property
    def list_after_name(self):
        return self.data['listAfter']['name']

    @property
    def text(self):
        return self.data['text']

    @property
    def card_permalink(self):
        return TRELLO_PERMALINK_CARD.format(
            self.data['board']['id'],
            self.data['card']['idShort']
        )

    @property
    def check_item_name(self):
        return self.data['checkItem']['name']

    def check_item_state(self):
        return self.data['checkItem']['state']


def yield_actions(board, limit=5, page=0, since=None, filter='updateCard,commentCard,createCard'):
    """ Call Trello API and yield a HipChat-friendly message for each.

        :param board: the id of the board to fetch comments from
        :limit (opt): the number of comments to return - defaults to 5
        :page (opt): the page number (if paging) - defaults to 0 (first page)
        :since (opt): date, Null or lastView (default)

        This uses the `since=lastView` request parameter
        to bring back only the latest comments - but bear
        in mind that this will reset each time the program
        is run, so will need a timestamp check as well. Probably.
    """
    params = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN,
        'filter': filter,
        'page': page,
        'limit': limit,
        'since': since.isoformat()
    }
    url = TRELLO_API_URL.format(board)
    data = requests.get(url, params=params)
    if data.status_code == 200:
        for action_data in data.json:
            action = TrelloAction(action_data)
            try:
                yield action.get_hipchat_message(), action.timestamp
            except UnsupportedTrelloActionError as ex:
                logging.error('Unsupported action:\n{0}'.format(ex))
                continue
            except KeyError as ex:
                logging.error('Unable to parse action: {0}'.format(action))
                logging.error('Error thrown: {0}'.format(ex))
                continue
    else:
        logging.error('Error retrieving Trello data: {0}'.format(data.reason))
