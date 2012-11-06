from os import environ

HIPCHAT_API_TOKEN = environ['HIPCHAT_API_TOKEN']

TRELLO_API_KEY = environ['TRELLO_API_KEY']
TRELLO_API_TOKEN = environ['TRELLO_API_TOKEN']

REDIS_URL = environ['REDISTOGO_URL']

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
DATE_FORMAT_Z = '%Y-%m-%dT%H:%M:%S.%fZ'

DEBUG = bool(environ.get('FLASK_DEBUG', False) == 'True')

try:
    import local_settings
except ImportError:
    pass

if DEBUG:
    print '------------------------------------'
    print 'HIPCHAT_API_TOKEN = {0}'.format(HIPCHAT_API_TOKEN)
    print 'TRELLO_API_KEY = {0}'.format(TRELLO_API_KEY)
    print 'TRELLO_API_TOKEN = {0}'.format(TRELLO_API_TOKEN)
    print 'REDIS_URL = {0}'.format(REDIS_URL)
    print '------------------------------------'
