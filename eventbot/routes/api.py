import logging

from flask import (
    Blueprint,
    jsonify,
    request,
)

from eventbot.receiver.eventbot import router

logger = logging.getLogger(__name__)

blueprint = Blueprint('api', __name__)


@blueprint.route('/healthcheck')
def healthcheck():
    # The healthcheck returns status code 200
    return 'OK'


@blueprint.route('/api/v1/eventbot', methods=['POST'])
def eventbot_route() -> str:
    event = request.get_json()
    logger.debug(f'eventbot_route request event: {event}')
    ret = router.handle_event(event)
    logger.debug(f'eventbot_route response: {ret}')
    return jsonify(ret)
