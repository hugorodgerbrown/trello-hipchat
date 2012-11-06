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

## Heroku setup

In order to deploy this application to Heroku, you will need an account, and an
application to which you can deploy. Refer to the docs above to read about how
to deploy to Heroku using Git.

In order to get Redis running on Heroku, I can recommend installing the RedisToGo
addon:

    $ heroku addons:add redistogo:nano

In order to view the logs more easily you can add any one of a number of logging
addons - both logentries and loggify work well:

    $ heroku addons:add logentries:tryit

The following config variables will need to be set:

    $ heroku config:add HIPCHAT_API_TOKEN=<your_token_here>
    $ heroku config:add TRELLO_API_KEY=<your_token_here>
    $ heroku config:add TRELLO_API_TOKEN=<your_token_here>

Adding RedisToGo will add the `REDISTOGO_URL` config setting.

### How do I get a Trello API user token?

In order to get the relevant access keys and tokens for Trello, you should start by reading the docs: https://trello.com/docs/

However, if you want to shortcut that process, you need two things - your app's developer API key, which is the TRELLO_API_KEY settting, and a
user access token, which is used to grant access to the relevant board / list / card. 

1. Developer API key - log in to Trello and visit this page - https://trello.com/1/appKey/generate (it's the one marked 'Key')
2. User access token - Trello supports the ability to generate keys for read or read/write, and with varying expiration periods. The app only requires read-only
access, for which you can use the following URL: 
`https://trello.com/1/authorize?key=<TRELLO_API_KEY>&name=trello-hipchat&expiration=never&response_type=token&scope=read`

The user (you, in this case) will be prompted to log in (if they are not already) - and once they've done that they will see a plain text page that includes the token. 

[UPDATE, 05-Nov-2012]: this now supports the following events:

* createCard 
* commentCard
* updateCard - only move between lists.

# TODO list

* Better management / administration (of tokens etc.)
* Custom formatting of messages