Quickstart and Development
==========================

Prerequisites
-------------

# You'll need a bot `ready for use in omnibot <https://lyft.github.io/omnibot/configuration.html>`_

.. _quickstart:

Quickstart
----------

This quickstart will add a handler configuration to omnibot, start omnibot, and start eventbot.

Note that this describes the eventbot handler configuration, so you'll need to update your omnibot handler sections if other bots are configured. It assumes you're using a bot named ``eventbot``, or you're using a subcommand of the bot ``omnibot``.

Add basic omnibot configuration (in the omnibot service):

``config/development/omnibot.conf``:

.. code-block:: yaml

   handlers:
     interactive_component_handlers:
       - callback_id: 'eventbot_events'
         response_type: 'in_channel'
         bots:
           "lyft-test-sandbox":
             # If you wanted to combine this to an existing bot, you could send to "omnibot"
             # here. The unique thing is the callback_id above, so as long as it doesn't
             # clash, it's OK.
             - "eventbot"
         no_message_response: True
         callbacks:
           - module: "omnibot.handlers.network_handlers:http_handler"
             kwargs:
               request_kwargs:
                 path: "http://eventbot:8080/api/v1/eventbot"
     message_handlers:
       # A bot that fully owns all commands of the service
       - match: ""
         match_type: "command"
         description: "create events using eventbot"
         bots:
           "friendly-name-for-your-team"
             - "eventbot"
         callbacks:
           - module: "omnibot.handlers.network_handlers:http_handler"
             kwargs:
               request_kwargs:
                 path: "http://eventbot:8080/api/v1/eventbot"
       # Example of how to configure this as a subcommand of another bot
       - match: "event"
         match_type: "command"
         description: "create events using a subcommand of the bot omnibot"
         bots:
           "friendly-name-for-your-team"
             - "omnibot"
         callbacks:
           - module: "omnibot.handlers.network_handlers:http_handler"
             kwargs:
               request_kwargs:
                 path: "http://eventbot:8080/api/v1/eventbot"

Start omnibot, using docker-compose:

.. code-block:: bash

   # in the omnibot repo root
   docker-compose up

Start eventbot, using docker-compose:

.. code-block:: bash

   # in the eventbot repo root
   docker-compose up

Start `ngrok <https://ngrok.com/download>`_:

.. code-block:: bash

   ./ngrok http 80

Connect your slack app's ``Event Subscriptions`` to the https ngrok link (see the `Forwarding` section of the ngrok command output), using the ``Event Subscriptions`` section of the slack api dashboard. Example URL: ``https://abcd.ngrok.com/api/v1/slack/event``

Connect your slack app's ``Interactive Components`` to the http ngrok link, using the ``Interactive Components`` section of the slack api dashboard. Example URL: ``https://abcd.ngrok.com/api/v1/slack/interactive``

You should likely subscribe to the following events:

* Bot Events

  * ``message.channels``
  * ``message.groups``
  * ``message.im``
  * ``message.mpim``

Invite your app into a channel in your slack workspace, and send a create command to it: ``@eventbot create`` or ``@omnibot event create`` (depending on your config)

The app should respond back with an interactive message that'll let you create an event.
