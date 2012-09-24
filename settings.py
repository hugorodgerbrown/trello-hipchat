from os import environ

HIPCHAT_API_TOKEN = environ['HIPCHAT_API_TOKEN']
HIPCHAT_API_URL = 'https://api.hipchat.com/v1/rooms/message'

TRELLO_API_KEY = environ['TRELLO_API_KEY']
TRELLO_API_TOKEN = environ['TRELLO_API_TOKEN']
TRELLO_API_URL = 'https://trello.com/1/boards/{0}/actions'
