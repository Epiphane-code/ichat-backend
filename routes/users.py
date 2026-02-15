from fastapi import APIRouter, HTTPException, Body
from db.connection import get_connection
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    phone: str
@router.post("/create")
def create_user(user: UserCreate):
    conn = get_connection()
    cur = conn.cursor()

    # Vérifier existence
    cur.execute("SELECT id FROM users WHERE phone = %s", (user.phone,))
    if cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Utilisateur déjà existant")

    # Insertion
    cur.execute(
        "INSERT INTO users (username, phone) VALUES (%s, %s) RETURNING id",
        (user.name, user.phone)
    )
    user_id = cur.fetchone()[0]
    conn.commit()

    cur.close()
    conn.close()

    return {
        "id": user_id,
        "username": user.name,
        "phone": user.phone

    }
@router.get("/exists/{phone}")
def user_exists(phone: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE phone = %s", (phone,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if user:
        return {
            "exists": True,
            "user_id": user[0]
        }
    else:
        return {
            "exists": False,
            "user_id": None
        }



@router.get("/")
def get_users():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, username, phone, created_at
            FROM users
            ORDER BY created_at DESC
        """)

        rows = cur.fetchall()
        if not rows:
            return {"message": "Aucun utilisateur trouvé"}

        users = []
        for row in rows:
            users.append({
                "id": row[0],
                "username": row[1],
                "phone": row[2],
                "created_at": row[3]
            })

        cur.close()
        conn.close()

        return users

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}")
def update_user(user_id: int, username: str = None, phone: str = None):
    if not username and not phone:
        raise HTTPException(
            status_code=400,
            detail="Aucune donnée à modifier"
        )

    conn = get_connection()
    cur = conn.cursor()

    fields = []
    values = []

    if username:
        fields.append("username = %s")
        values.append(username)

    if phone:
        fields.append("phone = %s")
        values.append(phone)

    values.append(user_id)

    query = f"""
        UPDATE users
        SET {', '.join(fields)}
        WHERE id = %s
        RETURNING id, username, phone
    """

    cur.execute(query, values)
    user = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur non trouvé"
        )

    return {
        "id": user[0],
        "username": user[1],
        "phone": user[2],
    }


@router.delete("/{user_id}")
def delete_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM users WHERE id = %s RETURNING id",
        (user_id,)
    )

    deleted = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur non trouvé"
        )

    return {"message": "Utilisateur supprimé avec succès"}




class GetIdRequest(BaseModel):
    phone: str


class GetIdRequest(BaseModel):
    phone: str

@router.post("/getID")
def get_id(data: GetIdRequest = Body()):
    conn = get_connection()
    cur = conn.cursor()

    # Normalisation rapide si besoin
    phone = data.phone

    cur.execute(
        "SELECT id FROM users WHERE phone = %s",
        (phone,)
    )
    row = cur.fetchone()
    print("PHONE RECU:", data.phone)
    print("ROW:", row)

    cur.close()
    conn.close()

    if row:
        return {
            "exists": True,
            "id": row[0]
        }
    else:
        return {
            "exists": False,
            "id": 0
        }
