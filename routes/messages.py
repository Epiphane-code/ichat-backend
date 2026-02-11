from fastapi import APIRouter, Body
from db.connection import get_connection
from pydantic import BaseModel

router = APIRouter()

class MessageCreate(BaseModel):
    sender_id: int
    receiver_id: int
    content: str

@router.post("/send")
def send_message(data: MessageCreate = Body()):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO messages (sender_id, receiver_id, content)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (data.sender_id, data.receiver_id, data.content))

    message_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return {
        "id": message_id,
        "sender_id": data.sender_id,
        "receiver_id": data.receiver_id,
        "content": data.content
    }



@router.get("/discussion/{idA}/{idB}")
def get_discussion(idA: int, idB: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, sender_id, receiver_id, content, created_at
        FROM messages
        WHERE
            (sender_id = %s AND receiver_id = %s)
            OR
            (sender_id = %s AND receiver_id = %s)
        ORDER BY created_at ASC
    """, (idA, idB, idB, idA))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    messages = []
    for row in rows:
        messages.append({
            "id": row[0],
            "sender_id": row[1],
            "receiver_id": row[2],
            "content": row[3],
            "created_at": row[4],
        })

    return messages


@router.get("/discussions/{user_id}")
def get_my_discussions(user_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT
            CASE
                WHEN sender_id = %s THEN receiver_id
                ELSE sender_id
            END AS contact_id
        FROM messages
        WHERE sender_id = %s OR receiver_id = %s
    """, (user_id, user_id, user_id))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [{"contact_id": row[0]} for row in rows]


