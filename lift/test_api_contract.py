from lift import api


def testPutAndThenVariousGets():
    api.core.drop()
    api.core.init_db()
    app = api.app()
    app.testing = True
    client = app.test_client()
    r = client.get('/sessions/', content_type="application/json")
    print("opened request")
    assert r.status_code == 200
