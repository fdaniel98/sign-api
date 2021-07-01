from jwt import decode


def verify_token(token, secret):
    data = decode(token, secret, algorithms=["HS256"]);
    return data;
