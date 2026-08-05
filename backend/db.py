from database import get_connection


def save_user(name=None, city=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users (name, city)
        VALUES (%s, %s)
        ON CONFLICT (name)
        DO UPDATE
        SET city = CASE
            WHEN EXCLUDED.city IS NOT NULL
                 AND EXCLUDED.city <> ''
            THEN EXCLUDED.city
            ELSE users.city
        END
        """,
        (name, city)
    )

    conn.commit()

    cursor.close()
    conn.close()


def get_user(name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT name, city
        FROM users
        WHERE name = %s
        """,
        (name,)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user