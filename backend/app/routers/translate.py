from fastapi import APIRouter, Depends, HTTPException, Query
from backend.app.dependencies.auth import get_current_user
from backend.app.schemas.message import Payload
from backend.app.services.firestore_service import save_message, load_last_messages, delete_message_by_content
from backend.app.services.translation_service import translate_text

router = APIRouter(prefix="/translate", tags=["translate"])

@router.get("/history")
def get_history(limit: int = Query(default=8, ge=1, le=50), user=Depends(get_current_user)):
    msgs = load_last_messages(user["uid"], limit=limit)
    return msgs if msgs else []

@router.delete("/delete")
def delete_item(payload: Payload, user=Depends(get_current_user)):
    delete_message_by_content(user["uid"], payload.text)
    return {"status": "deleted"}

@router.post("")
def translate(payload: Payload, user=Depends(get_current_user)):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    try:
        save_message(user["uid"], text)
        translation = translate_text(text)
        save_message(user["uid"], translation)

        return {
            "text": translation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")