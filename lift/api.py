from lift import core
from lift.util import validate_date
from lift.models import Session as SessionModel

from flask import Flask, url_for, request, Response, Blueprint
from flask.views import MethodView

from google.oauth2.id_token import verify_firebase_token
from google.auth.transport.requests import Request
import functools
import json

get_claims = verify_firebase_token
HTTP_REQUEST = Request()
JSON = 'application/json'


def jsonify(call):
    @functools.wraps(all)
    def wrapper(*args, **kwargs):
        if request.headers.get('Content-Type', JSON) == JSON:
            (body, status) = call(*args, **kwargs)
            return Response(json.dumps(body), status=status, mimetype=JSON)
        return Response(json.dumps({}), status=415, mimetype=JSON)
    return wrapper


def get_user(call):
    @functools.wraps(call)
    def wrapper(*args, **kwargs):
        login = '{}{}'.format(request.host, url_for('login'))
        failure = Response(json.dumps({
            'failure': 'Authorization rejected',
            'login': login
        }), 401)

        if 'Authorization' not in request.headers:
            return failure
        id_token = request.headers.get('Authorization').split(' ').pop()
        claims = get_claims(
                id_token, HTTP_REQUEST)
        if not claims:
            return Response(
                    json.dumps({
                        'failure', 'Authorization rejected'}),
                    401
            )
        new_args = [claims.sub]
        new_args.extend(args)
        call(*new_args, **kwargs)
    return wrapper


class Session(MethodView):
    def __init__(self, create_core):
        self.core = create_core()

    @get_user
    @jsonify
    def get(self, user, date=None, id=None):
        if date is None and id is None:
            return ([s.to_dict() for s in self.core.iterate(
                user,
                start_date=validate_date(request.args.get('start')),
                end_date=validate_date(request.args.get('end')),
                limit=request.args.get('limit')
            )], 200,)

        if date and not id:
            return (
                self.core.get(user, date=date),
                200,
            )

        if id:
            return self.core.get(user, id=id)

    @get_user
    @jsonify
    def post(self, user, date):
        body = request.get_json()
        if not body:
            return ({'error': 'no body'}, 400)
        response = []
        for b in body:
            d = {}
            d.update(b)
            d.update('session_date', date)
            for r in self.core.insert(user, SessionModel.from_dict(d)):
                response.append(r)

        return {'received': body, 'put': response}, 200,


api = Blueprint("api", __name__)

session_view = Session.as_view("sessions", core.create)
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
    app = Flask("api only")
    app.register_blueprint(api)
    return app


if __name__ == "__main__":
    print("running api only")
    app().run()
