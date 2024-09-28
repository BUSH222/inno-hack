import psycopg2

conn = psycopg2.connect(database='inno-hack-vcs',
                        user='postgres',
                        host='localhost',
                        password='12345678',
                        port=5432)
cur = conn.cursor()


def preload_db(populate=False):
    with open('schema.sql', 'r') as schema_obj:
        schema = schema_obj.read()
        cur.execute(schema)
    if populate:
        with open('populate.sql', 'r') as populate_obj:
            populate_query = populate_obj.read()
            cur.execute(populate_query)
    conn.commit()


def create_user(name, password):
    cur.execute('INSERT INTO users(name, password) VALUES (%s, %s) RETURNING (id, name, password, email)',
                (name, password))
    conn.commit()
    return cur.fetchone()[0]


def get_all_user_data_by_name(name):
    cur.execute("SELECT id, name, password, email FROM users WHERE name = %s", (name,))
    return cur.fetchone()


def get_all_user_data_by_id(id):
    cur.execute("SELECT id, name, password, email FROM users WHERE id = %s", (id,))
    return cur.fetchone()


def check_access(repoid, userid):
    cur.execute("SELECT 1 FROM repo_access WHERE EXISTS (SELECT 1 FROM repo_access WHERE repoid = %s AND userid = %s)",
                (repoid, userid))
    return bool(cur.fetchone())


def create_repository(userid, reponame):
    cur.execute('INSERT INTO repositories (name, user_creator_id) VALUES (%s, %s) RETURNING id', (reponame, userid))
    conn.commit()
    return cur.fetchone()[0]


def get_repo_info(id):
    cur.execute('SELECT id, name FROM commits WHERE repository = %s', (id, ))
    return cur.fetchall()


def get_full_repo_info(id):
    cur.execute('SELECT id, name, user_creator_id, user_creator_id FROM repositories WHERE user_creator_id = %s',
                (id, ))
    return cur.fetchall()[0]


def make_commit(data, userid, repoid, commit_name):
    cur.execute('INSERT INTO commits(name, author, repository, data) VALUES (%s, %s, %s, %s)',
                (commit_name, userid, repoid, data))
    conn.commit()


def get_user_repos(userid):
    cur.execute('SELECT repoid FROM repo_access WHERE userid = %s', (userid, ))
    return list(map(lambda x: x[0], cur.fetchall()))


def add_user_to_repo(userid, repoid):
    cur.execute('INSERT INTO repo_access(repoid, userid) VALUES (%s, %s)', (repoid, userid, ))
    conn.commit()


def validate_pwd(userid, pwd):
    cur.execute('SELECT userid, pwd FROM users WHERE EXISTS(SELECT 1 FROM users WHERE id = %s AND password = %s))',
                (userid, pwd))
    return bool(cur.fetchone())


def get_latest_commit(repoid):
    cur.execute('SELECT id, name, data FROM commits WHERE repository = %s ORDER BY creation_time DESC LIMIT 1;',
                (repoid, ))
    return cur.fetchone()[0]


def get_commit_files(commitid):
    cur.execute('SELECT data FROM commits WHERE id = %s', commitid)
    return cur.fetchone()[0]


if __name__ == "__main__":
    preload_db(populate=False)
    conn.close()
