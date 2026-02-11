from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from db.connection import get_connection


router = APIRouter()

class TokenRequest(BaseModel):
    phone: str


@router.post("/infouser")
def get_user_info(data: TokenRequest = Body()):
    phone = data.phone
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, username, phone, created_at
            FROM users
            WHERE phone = %s
        """, (phone,))

        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            return {
                "id": user[0],
                "username": user[1],
                "phone": user[2],
            }

        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    except Exception as e:
        print("ERREUR INFO USER :", e)
        raise HTTPException(status_code=500, detail=str(e))