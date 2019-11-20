Configuration
=============

Example Minimal Configuration
-----------------------------

``eventbot.env``:

.. code-block:: bash

    AWS_DEFAULT_REGION=us-east-1
    # AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are not required, if this is accessible from the metadata service
    AWS_ACCESS_KEY_ID=1
    AWS_SECRET_ACCESS_KEY=1
    # DYNAMODB_URL only needs to be set for development, otherwise boto will auto-configure this
    DYNAMODB_URL=http://dynamo:7777
    # You'll need to create dynamo tables for events and users, as well as a global index on the event table.
    # A script is included to auto-create the tables: python3 manage.py --create-tables
    DYNAMODB_TABLE_EVENT=eventbot-event
    DYNAMODB_TABLE_USER=eventbot-user

.. _omnibot_config_example:

``omnibot.conf``:

.. code-block:: yaml

   handlers:
     interactive_component_handlers:
       - callback_id: 'eventbot_events'
         response_type: 'in_channel'
         bots:
           "friendly-name-for-your-team":
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

Basic Configuration
-------------------

DynamoDB Configuration
^^^^^^^^^^^^^^^^^^^^^^

eventbot stores events and user information in dynamodb tables.

* ``AWS_DEFAULT_REGION`` (required): Region to use for dynamodb.
* ``AWS_ACCESS_KEY_ID`` (optional): Explicit credential to use for AWS access. Default: (system AWS credentials or metadata service-based credentials)
* ``AWS_SECRET_ACCESS_KEY`` (optional): Explicit credential to use for AWS access. Default: (system AWS credentials or metadata service-based credentials)
* ``DYNAMODB_URL`` (optional): URL to use for local dynamodb. Only needed for development. Default: (autoconfigured by boto, based on AWS region)
* ``DYNAMODB_TABLE_EVENT`` (optional): Table name for events. Default: ``eventbot-event``
* ``DYNAMODB_TABLE_USER`` (optional): Table name for users. Default: ``eventbot-user``

Logging Configuration
^^^^^^^^^^^^^^^^^^^^^

Logging is configured through your wsgi server (like gunicorn or uwsgi). eventbot has production and development ready logging configuration available at ``conf/logging.conf`` and ``conf/development/logging.conf``.

Omnibot configuration
^^^^^^^^^^^^^^^^^^^^^

See the :ref:`example minimal config <omnibot_config_example>`.

Omnibot needs to route a message command, and an interactive component callback to eventbot.
