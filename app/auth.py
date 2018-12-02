# -*- coding: utf-8 -*-


def check_auth_token(token):
    from app import domain
    try:
        user = domain.User.create_with_token(token)
        new_token = user.generate_auth_token()
    except Exception as ex:
        return None, None, None
    return user.as_dict(compact=True), new_token, user

