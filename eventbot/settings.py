from eventbot.utils.settings import bool_env, int_env, str_env

# Flask settings

DEBUG = bool_env('DEBUG', False)
HOST = str_env('HOST', '0.0.0.0')
PORT = int_env('PORT', 80)

# DynamoDB settings

# Set the DynamoDB to something non-standard. This can be used for local
# development. Doesn't normally need to be set.
# Example: http://localhost:8000
DYNAMODB_URL = str_env('DYNAMODB_URL')
# The DynamoDB table to use for storage of events
DYNAMODB_TABLE_EVENT = str_env('DYNAMODB_TABLE_EVENT')
DYNAMODB_GSI_EVENT_STATUS = str_env('DYNAMODB_GSI_EVENT_STATUS')
# The DynamoDB table to use for storage of user data
DYNAMODB_TABLE_USER = str_env('DYNAMODB_TABLE_USER')

# StatsD Settings

# A statsd host
STATSD_HOST = str_env('STATSD_HOST', 'localhost')
# A statsd port
STATSD_PORT = int_env('STATSD_PORT', 8125)
# A statsd prefix for metrics
STATSD_PREFIX = str_env('STATSD_PREFIX', 'eventbot')


def get(name, default=None):
    """
    Get the value of a variable in the settings module scope.
    """
    return globals().get(name, default)
