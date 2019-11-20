#!/usr/bin/env python

# Import app first so that we can monkey patch as early as possible
from eventbot.app import app

from flask_script import Manager
from eventbot.scripts.create_tables import CreateTables

manager = Manager(app)
manager.add_command('create-tables', CreateTables())

if __name__ == "__main__":
    manager.run()
