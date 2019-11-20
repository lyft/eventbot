Installation
############

Quickstart for testing
----------------------

If you just want to checkout eventbot and aren't looking to deploy it into
production check out the :ref:`quickstart <quickstart>`.

Docker installation
-------------------

To run eventbot in Docker
^^^^^^^^^^^^^^^^^^^^^^^^^

eventbot is configured through a environment variables. When starting the docker container, you'll need to inject environment variables, via ``--env-file``.

.. code-block:: bash

    docker pull lyft/eventbot
    # You can also override the logging config, via: -v logging.conf:/etc/eventbot/logging.conf
    docker run --env-file eventbot.env -t lyft/eventbot -c "gunicorn --config /srv/eventbot/config/gunicorn.conf eventbot.wsgi:app --workers=2 -k gevent --access-logfile=- --error-logfile=-"

To build the image
^^^^^^^^^^^^^^^^^^

If you want to build the image and store it in your private registry, you can
do the following:

.. code-block:: bash

    git clone https://github.com/lyft/eventbot
    cd eventbot
    docker build -t lyft/eventbot .

pip installation
----------------

#. Using Ubuntu or Debian (please help with non-Ubuntu/Debian install
   instructions!)
#. venv location: /srv/eventbot/venv

Make a virtualenv and install pip requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    sudo apt-get install -y python3 python3-dev python3-pip python3-virtualenv openssl libssl-dev gcc pkg-config libffi-dev libxml2-dev libxmlsec1-dev
    cd /srv/eventbot
    virtualenv3 venv
    source venv/bin/activate
    pip3 install -U pip
    pip3 install eventbot
    deactivate

Manual installation
-------------------

Assumptions:

#. Using Ubuntu or Debian (please help with non-Ubuntu/Debian install
   instructions!)
#. Installation location: /srv/eventbot/venv
#. venv location: /srv/eventbot/venv

Clone eventbot
^^^^^^^^^^^^^^

.. code-block:: bash

    cd /srv
    git clone https://github.com/lyft/eventbot

Make a virtualenv and install pip requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    sudo apt-get install -y python3 python3-dev python3-pip python3-virtualenv openssl libssl-dev gcc pkg-config libffi-dev libxml2-dev libxmlsec1-dev
    cd /srv/eventbot
    virtualenv venv
    source venv/bin/activate
    pip install -U pip
    pip install -r piptools_requirements3.txt
    pip install -r requirements3.txt
    deactivate

Run eventbot
^^^^^^^^^^^^

It's necessary to export your configuration variables before running eventbot.
The easiest method is to source a file that exports your environment before
running eventbot.

.. code-block:: bash

    mkdir /etc/eventbot
    mkdir /var/log/eventbot
    cd /srv/eventbot
    # You need to create eventbot.env
    cp eventbot.env /etc/eventbot/
    source /etc/eventbot/eventbot.env
    # A default logging config is included
    cp conf/logging.conf /etc/eventbot/
    source venv/bin/activate
    # You should really probably use some form of an init system here, rather than running them directly.
    gunicorn --config /srv/eventbot/config/gunicorn.conf eventbot.wsgi:app --workers=2 -k gevent --access-logfile=/var/log/eventbot/eventbot.log --error-logfile=/var/log/eventbot/eventbot.err &
