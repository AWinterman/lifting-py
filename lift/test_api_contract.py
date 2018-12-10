from lift import api
import sys

class TestApiContract:
    def testPutAndThenVariousGets(self):
        api.core.drop()
        api.core.init_db()
        app = api.app()
        app.testing = True
        client = app.test_client()
        r = client.open('/sessions/', content_type="application/json", method="get")
        assert r.status_code == 200
        print(r.data, file=sys.stderr)

    

