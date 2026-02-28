# db.py
import firebase_admin
from firebase_admin import credentials, auth, firestore

# Initialize (Make sure service-account.json is in your folder!)
cred = credentials.Certificate("service-account.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def get_or_create_user(uid, email):
    user_ref = db.collection("users").document(uid)
    doc = user_ref.get()
    
    if not doc.exists:
        # This is where you'll eventually generate a real XRPL wallet
        new_user_data = {
            "uid": uid,
            "email": email,
            "xrpl_address": "rPendingGeneration...", # Placeholder for now
            "balance": 0.0,
            "currency": "RLUSD"
        }
        user_ref.set(new_user_data)
        return new_user_data
    
    return doc.to_dict()