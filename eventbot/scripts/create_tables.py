import logging
import time

from flask_script import Command

from eventbot.models.event import Event
from eventbot.models.user import User

logger = logging.getLogger(__name__)


class CreateTables(Command):
    def create_table_given_class(self, cls):
        # This loop is absurd, but there are race conditions with DynamoDB
        # Local
        for i in range(5):
            logger.info(
                'Creating table for model: {}'.format(cls.__name__)
            )
            try:
                if not cls.exists():
                    cls.create_table(
                        read_capacity_units=10,
                        write_capacity_units=10,
                        wait=True
                    )
                    logger.info(
                        'Created table for model: {}'.format(cls.__name__)
                    )
                else:
                    logger.info(
                        'Table already existed for model: {}'.format(
                            cls.__name__
                        )
                    )

                break
            except Exception:
                if i == 4:
                    raise
                time.sleep(2)

    def run(self):
        classes = [Event, User]

        for cls in classes:
            self.create_table_given_class(cls)
