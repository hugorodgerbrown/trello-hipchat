"""
The API documentation is available at https://www.hipchat.com/docs/api/method/rooms/message
The room id can be found by going to https://{{your-account}}.hipchat.com/rooms/ids
The tokens can be set at https://{{your-account}}.hipchat.com/admin/api

Dependencies: Requests (http://docs.python-requests.org)
"""
import requests
from settings import HIPCHAT_API_TOKEN, HIPCHAT_API_URL

#HIPCHAT_API_TOKEN = 'c1e74d7b2fa299b12fbd4cc4c982b6'
#HIPCHAT_API_ROOM_ID = '102276'
#HIPCHAT_API_URL = 'https://api.hipchat.com/v1/rooms/message'


def send_message(msg, room_id, color='yellow', notify=False, sender='Trello'):
    """ Sends a message to a HipChat room. """
    payload = {'auth_token': HIPCHAT_API_TOKEN,
        'notify': notify,
        'color': color,
        'from': sender,
        'room_id': room_id,
        'message': msg,
        'message_format': 'text'
    }
    response = requests.post(HIPCHAT_API_URL, data=payload)
    if response.status_code != 200:
        print response.reason
        print response.url
        print response.text
