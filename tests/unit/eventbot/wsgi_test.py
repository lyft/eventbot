from eventbot.wsgi import app
from unittest.mock import patch
import json


def test_healthcheck():
    response = app.test_client().get('/healthcheck')
    assert response.status_code == 200
    assert response.data.decode('ascii') == 'OK'


@patch('eventbot.routes.views.do_healthcheck')
def test_handle_error(healthcheck_fn):
    healthcheck_fn.side_effect = Exception('testException')

    response = app.test_client().get('/healthcheck')

    assert response.status_code == 500
    json_data = json.loads(response.data)
    assert json_data['error'] == 'Internal server error'
