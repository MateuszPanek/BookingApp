from secrets import token_urlsafe


def create_token():
    return token_urlsafe(16)
