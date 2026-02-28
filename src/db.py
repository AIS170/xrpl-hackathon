# db.py
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Firebase Admin SDK (use your service account JSON)
cred_path = os.path.join(os.path.dirname(__file__), "service-account.json")

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

db = firestore.client()


def get_or_create_user(uid, email):
    """
    Fetches a user from Firestore by uid. Creates it if not exists.
    Returns user data as a dictionary.
    """
    user_ref = db.collection("users").document(uid)
    doc = user_ref.get()

    if doc.exists:
        user_data = doc.to_dict()
    else:
        # MVP default role = 'viewer'
        user_data = {
            "uid": uid,
            "email": email,
            "role": "viewer"
        }
        user_ref.set(user_data)

    return user_data
