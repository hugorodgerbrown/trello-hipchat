# Trello-HipChat-Heroku

This is a (very) simple web application that picks up notifications from a 
Trello board, and posts them to a HipChat room.

There is lots that could be done to improve it - at the moment this is just the
minimum required to get (my) job done.

It is designed to run as a Flask app within Heroku, and as such there are some
conventions that need to be adhered to. These are best described as the Zen of 
Heroku (in deference to the Zen of Python), a set of rules that Heroku requires
you to follow when setting up your application to run on their infrastructure.

The only one that really matters from our point of view is that all settings
(state) are held in environment variables, as opposed to config settings. The
`settings.py` file therefore reads these settings out using `os.environ`.

The application has only one endpoint, set up to respond to the following url:

    http://app/board_id/room_id

The app will unpack the board_id, and combine that with the TRELLO_API_KEY and
TRELLO_API_TOKEN in the env vars to call the board API and retrieve all 
commentCard actions. Each comment is then sent to the HipChat room identified
on the URL (again, using the HIPCHAT_API_TOKEN from the env vars.)

The only additional complexity is that it uses the latest comment date returned
as the 'since' API parameter value to prevent duplicate comments coming back.
The value of the last date is stored in Redis, so that it is available to all
processes. The key used is {{board}}_{{room}}.

I would recommend the following as background reading:

1. Heroku - https://devcenter.heroku.com/articles/quickstart
2. Flask documentation - http://flask.pocoo.org/docs/
3. Trello API - https://trello.com/docs/
4. HipChat API - https://www.hipchat.com/docs/api

# TODO list

* Incorporate additional notifications - e.g. create card, move card
* Better management / administration (of tokens etc.)