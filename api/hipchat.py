"""
Code for sending messages to HipChat.

The API documentation is available at https://www.hipchat.com/docs/api/method/rooms/message
The room id can be found by going to https://{{your-account}}.hipchat.com/rooms/ids
The tokens can be set at https://{{your-account}}.hipchat.com/admin/api

Dependencies: Requests (http://docs.python-requests.org)
"""
import requests
from settings import HIPCHAT_API_TOKEN

HIPCHAT_API_URL = 'https://api.hipchat.com/v1/rooms/message'


def send_message(msg, room_id, color='yellow', notify=False, sender='Trello'):
    """
    Send a message to a HipChat room.

    Args:
        msg: the string message to send to HipChat.
        room_id: the numeric id of the room to send the message to.
        color: the background color of the message as seen in HipChat.
        notify: if True, then 'ping' when a new message is sent.
        sender: the name of the sender - must be < 15 chars.

    Returns:
        the response returned from calling the HipChat API.
    """
    payload = {
        'auth_token': HIPCHAT_API_TOKEN,
        'notify': notify,
        'color': color,
        'from': sender[:15],
        'room_id': room_id,
        'message': msg,
        'message_format': 'html'
    }
    return requests.post(HIPCHAT_API_URL, data=payload)
