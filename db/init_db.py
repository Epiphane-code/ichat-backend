from .connection import get_connection
import psycopg2

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
-- Table users
CREATE SEQUENCE IF NOT EXISTS users_id_seq;
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    statut TEXT DEFAULT 'online' CHECK (statut = ANY (ARRAY['online','offline'])),
    authentificated BOOLEAN DEFAULT false,
    username VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table contacts
CREATE SEQUENCE IF NOT EXISTS contacts_id_seq;
CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    my_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    username VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

-- Table messages
CREATE SEQUENCE IF NOT EXISTS messages_id_seq;
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    receiver_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table otp_codes
CREATE SEQUENCE IF NOT EXISTS otp_codes_id_seq;
CREATE TABLE IF NOT EXISTS otp_codes (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(20) NOT NULL,
    code VARCHAR(6) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    verified BOOLEAN DEFAULT false
);

-- Table status
CREATE SEQUENCE IF NOT EXISTS status_id_seq;
CREATE TABLE IF NOT EXISTS status (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(255) NOT NULL,
    type TEXT NOT NULL CHECK (type = ANY (ARRAY['image','video','text'])),
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Exemple d'insertion test
    cur.execute("""
INSERT INTO users (username, phone)
VALUES (%s, %s)
ON CONFLICT (phone) DO NOTHING;
""", ("Omar2", "90000000"))

# Commit et fermeture
    conn.commit()
    cur.close()
    conn.close()

print("Base de données initialisée avec succès !")

if __name__ == "__main__":
    init_db()