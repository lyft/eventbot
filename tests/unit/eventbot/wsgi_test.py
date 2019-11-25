from eventbot.wsgi import app


def test_healthcheck():
    response = app.test_client().get('/healthcheck')
    assert response.status_code == 200
    assert response.data.decode('ascii') == 'OK'
