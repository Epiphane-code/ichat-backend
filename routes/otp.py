from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from db.connection import get_connection
import random
from datetime import datetime, timedelta

router = APIRouter()
class OTPRequest(BaseModel):
    phone: str

@router.post("/send_otp")
def send_otp(data: OTPRequest = Body()):

    try:
        code = str(random.randint(100000, 999999))
        expires_at = datetime.now() + timedelta(minutes=5)

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO otp_codes (phone, code, expires_at)
            VALUES (%s, %s, %s)
        """, (data.phone, code, expires_at))

        conn.commit()
        cur.close()
        conn.close()

        return {"message": "OTP envoyé avec succès", "code": code}

    except Exception as e:
        print("ERREUR OTP :", e)
        raise HTTPException(status_code=500, detail=str(e))


class OTPVerifyRequest(BaseModel):
    phone: str
    code: str
@router.post("/verify_otp")
def verify_otp (data: OTPVerifyRequest = Body()):
    phone = data.phone
    code = data.code
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT code, expires_at
            FROM otp_codes
            WHERE phone = %s
            ORDER BY expires_at DESC
            LIMIT 1
        """, (phone,))

        otp = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()


        if not otp:
            return {"message": False}

        stored_code, expires_at = otp

        if datetime.now() > expires_at:
            return {"message": False}

        if code == stored_code:
            return {"message": True}

        else:
            return {"message": False}

    except Exception as e:
        print("ERREUR Vérification OTP :", e)
        raise HTTPException(status_code=500, detail=str(e))