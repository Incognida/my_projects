import sys
import subprocess
import time

import psycopg2


def delete_db():
    conn_string = "host='localhost' " \
                  "dbname='vlad_db' user='vlad_user' password='1'"
    try:
        conn = psycopg2.connect(conn_string)
        conn.set_isolation_level(0)
    except:
        print("Unable to connect to the database.")

    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT table_schema,table_name"
            " FROM information_schema.tables"
            " WHERE table_schema = 'public'"
            " ORDER BY table_schema,table_name")
        rows = cur.fetchall()
        for row in rows:
            print(f"dropping table: {row[1]}")
            cur.execute(f"drop table {row[1]} cascade")
        cur.close()
        conn.close()
    except:
        print(f"Error {sys.exc_info()[1]}")


if __name__ == '__main__':
    print('deleting migrations')
    subprocess.Popen(["find", ".", "-path", "*/migrations/*.py", "-not",
                      "-name", "__init__.py", "-delete"])
    time.sleep(1)
    subprocess.Popen(["find", ".", "-path", "*/migrations/*.pyc", "-delete"])
    print('deleted migrations')
    time.sleep(1)
    delete_db()
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            subprocess.Popen(['python', 'manage.py', 'makemigrations'])
            time.sleep(1)
            subprocess.Popen(['python', 'manage.py', 'migrate'])
            time.sleep(4)
            print('finished')