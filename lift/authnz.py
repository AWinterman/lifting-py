import google.oauth2.id_token

get_claims = google.oauth2.id_token.verify_firebase_token


class Authnz:
    def get_claims(self, authorization_header):
            id_token = request.headers['Authorization'].split(' ').pop()
            return self.get_claims(id_token, HTTP_REQUEST)
