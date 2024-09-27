import psycopg2

conn = psycopg2.connect(database='inno-hack-vcs',
                        user='postgres',
                        host='localhost',
                        password='12345678',
                        port=5432)
cur = conn.cursor()


def preload_db():
    with open('schema.sql', 'r') as schema_obj:
        schema = schema_obj.read()
        cur.execute(schema)
    conn.commit()


def create_user(name, password):
    cur.execute('INSERT INTO users(name, password) VALUES (%s, %s)', (name, password))


if __name__ == "__main__":
    preload_db()
    conn.close()
