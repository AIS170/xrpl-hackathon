# auth_utils.py
from firebase_admin import auth
from db import get_or_create_user


def authenticate_user(id_token):
    """
    Verify Firebase ID token and return user data.
    Raises Exception if invalid.
    """
    decoded_token = auth.verify_id_token(id_token)
    uid = decoded_token['uid']
    email = decoded_token.get('email')

    # Get or create user in DB
    user_data = get_or_create_user(uid, email)
    return user_data
