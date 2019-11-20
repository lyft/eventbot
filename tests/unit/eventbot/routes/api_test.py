import json

import pytest

from eventbot.wsgi import app


@pytest.fixture
def client():
    """Returns a Flask client for the app."""
    return app.test_client()


def test_post_slack_event(client, mocker):
    result = client.post(
        '/api/v1/eventbot',
        data=json.dumps({}),
        content_type='application/json'
    )
    data = json.loads(result.data)
    assert data
