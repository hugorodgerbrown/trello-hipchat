from os import environ

HIPCHAT_API_TOKEN = environ['HIPCHAT_API_TOKEN']
HIPCHAT_API_URL = 'https://api.hipchat.com/v1/rooms/message'

TRELLO_API_KEY = environ['TRELLO_API_KEY']
TRELLO_API_TOKEN = environ['TRELLO_API_TOKEN']
TRELLO_API_URL = 'https://trello.com/1/boards/{0}/actions'
TRELLO_PERMALINK_CARD = 'https://trello.com/card/{0}/{1}'

REDIS_URL = environ['REDISTOGO_URL']

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
DATE_FORMAT_Z = '%Y-%m-%dT%H:%M:%S.%fZ'

DEBUG = bool(environ.get('FLASK_DEBUG', False) == 'True')

try:
    import local_settings
except ImportError:
    pass
