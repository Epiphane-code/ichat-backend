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

    print (data.content)

    return {
        "id": message_id,
        "sender_id": data.sender_id,
        "receiver_id": data.receiver_id,
        "content": data.content
    }


@router.get("/messages/{user_id}/{contact_id}")
def get_messages(user_id: int, contact_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, sender_id, receiver_id, content, created_at
        FROM messages
        WHERE (sender_id = %s AND receiver_id = %s)
           OR (sender_id = %s AND receiver_id = %s)
        ORDER BY created_at ASC
    """, (user_id, contact_id, contact_id, user_id))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "id": row[0],
            "sender_id": row[1],
            "receiver_id": row[2],
            "content": row[3],
            "created_at": row[4]
        }
        for row in rows
    ]

@router.get("/discussions/{user_id}")
def get_my_discussions(user_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
      SELECT DISTINCT ON (
    CASE
        WHEN messages.sender_id = %s THEN messages.receiver_id
        ELSE messages.sender_id
    END
)
    CASE
        WHEN messages.sender_id = %s THEN messages.receiver_id
        ELSE messages.sender_id
    END AS contact_id,
    users.username,
    users.phone,
    messages.content AS last_message,
    messages.created_at AS last_message_time
FROM messages
JOIN users ON users.id = CASE
    WHEN messages.sender_id = %s THEN messages.receiver_id
    ELSE messages.sender_id
END
WHERE messages.sender_id = %s OR messages.receiver_id = %s
ORDER BY contact_id, last_message_time DESC;

    """, (user_id, user_id, user_id, user_id, user_id))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "contact_id": row[0],
            "username": row[1],
            "phone": row[2],
            "last_message": row[3],
            "last_message_time": row[4]
        }
        for row in rows
    ]



    cur.close()
    conn.close()

    