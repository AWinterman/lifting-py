from lift.core import create as create_core
from lift.util import validate_date
from lift.models import Session as SessionModel

from flask import Flask
from flask import request
from flask import Response
from flask import Blueprint
from flask.views import MethodView

import functools
import json

JSON = 'application/json'


def jsonify(call):
    @functools.wraps(jsonify)
    def wrapper(*args, **kwargs):
        if request.headers.get('Content-Type', JSON) == JSON:
            (body, status) = call(*args, **kwargs)
            return Response(json.dumps(body), status=status, mimetype=JSON)
        return Response(json.dumps({}), status=415, mimetype=JSON)
    return wrapper


class Session(MethodView):
    def __init__(self, core):
        self.core = core

    @jsonify
    def get(self, date=None, id=None):
        if date is None and id is None:
            return ([s.to_dict() for s in self.core.iterate(
                start_date=validate_date(request.args.get('start')),
                end_date=validate_date(request.args.get('end')),
                limit=request.args.get('limit')
            )], 200,)

        if date and not id:
            return (
                self.core.get(date),
                200,
            )

        if id:
            return self.core.get

    @jsonify
    def post(self, date):
        body = request.get_json()
        if not body:
            return ({'error': 'no body'}, 400)
        response = []
        for b in body:
            d = {}
            d.update(b)
            d.update('session_date', date)
            for r in self.core.insert(SessionModel.from_dict(d)):
                response.append(r)

        return {'received': body, 'put': response}, 200,


api = Blueprint("api", __name__)
core = create_core()

session_view = Session.as_view("sessions", core)
# get a list of sessions
api.add_url_rule(
    "/sessions/",
    defaults={'date': None, 'id': None},
    methods=["GET"],
    view_func=session_view
)
# get a single repetition by its id
api.add_url_rule('/sessions/<int:id>', view_func=session_view,
                 methods=['GET'])
# get what all the components of a single date
# add a single date
api.add_url_rule('/sessions/<string:date>', view_func=session_view,
                 methods=['GET', 'POST'])


def app():
    core.init_db()
    app = Flask("api only")
    app.register_blueprint(api)
    return app


if __name__ == "__main__":
    print("running api only")
    app().run()
