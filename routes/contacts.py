from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from db.connection import get_connection
import random
from datetime import datetime, timedelta

class ContactCreate(BaseModel):
    owner_id: int
    name: str
    phone: str

router = APIRouter()

@router.post("/create")
def create_contact(contact: ContactCreate = Body()):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO contacts (my_id, username, phone) VALUES (%s, %s, %s) RETURNING id",
        (contact.owner_id, contact.name, contact.phone)
    )
    contact_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return {"id": contact_id, "username": contact.name, "phone": contact.phone}

@router.get("/liste/{owner_id}")
def get_contacts(owner_id: int):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, username, phone FROM contacts WHERE my_id = %s",
            (owner_id,)
        )
        rows = cur.fetchall()
        contacts = [{"id": r[0], "username": r[1], "phone": r[2]} for r in rows]
        return contacts
    except Exception as e:
        print("❌ ERREUR BACKEND GET CONTACTS :", e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


