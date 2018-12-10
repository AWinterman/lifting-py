from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from lift.models import Session

from datetime import datetime


class GDocsExporter:
    def __init__(self, storage, config):
        self.storage = storage
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            print('getting creds')
            if not config.oauth_secret or not config.oauth_scope:
                raise ValueError((
                    "must specify GCP_OAUTH_CLIENT_SECRET to "
                    "export to google sheets"
                ))

            flow = client.flow_from_clientsecrets(
                    config.oauth_secret,
                    config.oauth_scope
            )
            creds = tools.run_flow(flow, store)
        self.service = build('sheets', 'v4', http=creds.authorize(Http()))

    def export(self):
        name = 'lifting-sessions-dump-{}'.format(datetime.now())
        spreadsheet = {
            'properties': {
                'title': name
            }
        }
        spreadsheet = self.service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId'
        ).execute()
        spreadsheet_id = spreadsheet.get('spreadsheetId')

        sheet = []
        sheet.append(Session.NAMES)
        for session in self.storage.iterate():
            sheet.append([v for k, v in session.to_dict().items()])

        body = {'values': sheet}
        result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='Sheet1!1:{}'.format(len(sheet)),
                valueInputOption='USER_ENTERED',
                body=body
        ).execute()
        print('{0} cells updated.'.format(result.get('updatedCells')))


if __name__ == '__main__':
    from lift.storage import Storage
    from os import environ

    exporter = GDocsExporter(Storage(environ), environ)
    exporter.export()
