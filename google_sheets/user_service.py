import gspread
from django.contrib.auth.models import User
from google.oauth2.credentials import Credentials as UserCredentials


def get_user_tokens(user: User):
    token = user.socialaccount_set.get(provider='google').socialtoken_set.get()

    return {
        'token': token.token,
        'refresh_token': token.token_secret,
    }


def get_google_sheets_client(user: User):
    tokens = get_user_tokens(user)

    credentials = UserCredentials(
        token=tokens['token'],
        refresh_token=tokens['refresh_token'],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    return gspread.authorize(credentials)


def read_from_sheet(user: User, sheet_id, range):
    client = get_google_sheets_client(user)
    spreadsheet = client.open_by_key(sheet_id)

    return spreadsheet.values_get(range)


def write_to_sheet(user: User, sheet_id, range, data):
    client = get_google_sheets_client(user)
    spreadsheet = client.open_by_key(sheet_id)

    return spreadsheet.values_update(
        range,
        params={'valueInputOption': 'RAW'},
        body={'values': data}
    )
