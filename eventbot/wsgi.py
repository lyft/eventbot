import logging
from typing import Text, Tuple

import statsd
from flask import jsonify
from werkzeug.exceptions import HTTPException

from eventbot import settings
from eventbot.app import app
from eventbot.routes import api # noqa:E402

logger = logging.getLogger(__name__)

# register your blueprint here
app.register_blueprint(api.blueprint)

_STATS_CLIENT = None


def _get_stats():
    global _STATS_CLIENT
    if _STATS_CLIENT is None:
        _STATS_CLIENT = statsd.StatsClient(
            settings.STATSD_HOST,
            settings.STATSD_PORT,
            prefix=settings.STATSD_PREFIX
        )
    return _STATS_CLIENT


# handle abort()
@app.errorhandler(HTTPException)
def handle_http_exception(e: HTTPException) -> Tuple[Text, int]:
    return e.get_response()


# catch all exceptions, rather than letting them propagate to gunicorn
@app.errorhandler(Exception)
def handle_error(e: Exception) -> Tuple[Text, int]:
    statsd = _get_stats()
    exception_class_name = type(e).__name__
    logger.exception(
        'Uncaught exception',
        extra={'exception': {'class': exception_class_name, 'message': str(e)}},
    )
    statsd.incr(f'uncaught_exception.{exception_class_name}')

    return jsonify(
        {'error': 'Internal server error'}
    ), 500


if __name__ == '__main__':
    app.run(
        host=settings.get('HOST', '0.0.0.0'),
        port=settings.get('PORT', 5000),
        debug=settings.get('DEBUG', True)
    )
