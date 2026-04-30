from datetime import datetime, timezone
from backend.app.core.firebase_config import get_firestore
from firebase_admin import firestore

db = get_firestore()

def save_message(uid: str, content: str):
    doc = {
        "content": content,
        "ts": datetime.now(timezone.utc)
    }
    db.collection("docs").document(uid).collection("translations").add(doc)

def load_last_messages(uid: str, limit: int = 8):
    q = (
        db.collection("docs")
        .document(uid)
        .collection("translations")
        .order_by("ts", direction=firestore.Query.DESCENDING)
        .limit(limit)
    )

    docs = list(q.stream())

    return [
        {
            "content": d.to_dict().get("content", "")
        }
        for d in docs
    ]

def delete_message_by_content(uid: str, content: str):
    q = (
        db.collection("docs")
        .document(uid)
        .collection("translations")
        .where("content", "==", content)
        .limit(5)
    )
    
    docs = list(q.stream())
    if docs:
        docs.sort(key=lambda d: d.to_dict().get("ts", 0), reverse=True)
        docs[0].reference.delete()